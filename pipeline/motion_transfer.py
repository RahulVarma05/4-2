"""
pipeline/motion_transfer.py
----------------------------
The main per-frame orchestrator for motion transfer.

Calls all other pipeline modules in the correct order:
    keypoints  → generator → masking → blending

All 8 bug fixes from the old demo.py are applied here:
  Fix 1: kp_source detected ONCE before the loop (not per-frame)
  Fix 2: temporal smoothing alpha = 0.60 (was 0.75)
  Fix 3: always RELATIVE mode generation (use_relative_movement=True)
  Fix 4: alignment via src_pts→drv_pts transform (not re-detection on generated)
  Fix 5: hull shrink = 0.85 (was 0.60) — in masking.py
  Fix 6: occlusion threshold = 0.15 (was 0.40) — in masking.py
  Fix 7: NORMAL_CLONE not MIXED_CLONE — in blending.py
  Fix 8: no post-Poisson fade_mask — in blending.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fomm_core'))

import numpy as np
import torch
import imageio
from tqdm import tqdm
from skimage.transform import SimilarityTransform, warp as sk_warp

from pipeline.keypoints import (
    normalize_kp, get_kp_pixels,
    temporal_smooth, extract_prev_state
)
from pipeline.masking import (
    build_hull_mask, build_occlusion_mask, build_combined_mask
)
from pipeline.blending import (
    poisson_blend, alpha_blend, color_correct
)


# ──────────────────────────────────────────────
#  Base animation  (no compositing)
# ──────────────────────────────────────────────

def make_animation(source_image, driving_video, generator, kp_detector,
                   relative=True, adapt_scale=True, cpu=False):
    """
    Basic FOMM animation — generates the source image moving
    with the driving video's motion.

    No compositing, no masking. Pure FOMM output.
    Use this as the FIRST test to verify the model works before
    adding any compositing on top.

    Args:
        source_image  : numpy (256,256,3) float32
        driving_video : list of numpy (256,256,3) float32
        generator     : loaded OcclusionAwareGenerator
        kp_detector   : loaded KPDetector
        relative      : use relative keypoint mode (recommended: True)
        adapt_scale   : adapt movement scale (recommended: True)
        cpu           : run on CPU if True

    Returns:
        list of numpy arrays (256,256,3) float32 — one per driving frame
    """
    with torch.no_grad():
        predictions = []

        # Prepare source tensor
        source = torch.tensor(
            source_image[np.newaxis].astype(np.float32)
        ).permute(0, 3, 1, 2)
        if not cpu:
            source = source.cuda()

        # Prepare all driving frames as one tensor
        driving = torch.tensor(
            np.array(driving_video)[np.newaxis].astype(np.float32)
        ).permute(0, 4, 1, 2, 3)

        # FIX 1: detect source keypoints ONCE — reuse every frame
        kp_source          = kp_detector(source)
        kp_driving_initial = kp_detector(driving[:, :, 0])

        for frame_idx in tqdm(range(driving.shape[2]), desc="Animating"):
            driving_frame = driving[:, :, frame_idx]
            if not cpu:
                driving_frame = driving_frame.cuda()

            kp_driving = kp_detector(driving_frame)

            # FIX 3: always relative mode
            kp_norm = normalize_kp(
                kp_source=kp_source,
                kp_driving=kp_driving,
                kp_driving_initial=kp_driving_initial,
                use_relative_movement=relative,
                use_relative_jacobian=relative,
                adapt_movement_scale=adapt_scale
            )
            out = generator(source, kp_source=kp_source, kp_driving=kp_norm)
            predictions.append(
                np.transpose(out['prediction'].data.cpu().numpy(), [0, 2, 3, 1])[0]
            )

    return predictions


# ──────────────────────────────────────────────
#  Find best starting frame
# ──────────────────────────────────────────────

def find_best_frame(source_image, driving_video, kp_detector, cpu=False):
    """
    Find the driving frame whose pose most closely matches the source image.

    FOMM in relative mode computes keypoint deltas from the FIRST driving frame.
    If the first frame has a very different pose from the source image, the
    animation snaps/jumps at frame 0. Starting from the best-matching frame
    eliminates this snap entirely.

    Method:
        For each driving frame, compute the sum of squared distances
        between source keypoints and driving keypoints (after normalising
        both to zero-mean unit-scale). Return the index of the minimum.

    Args:
        source_image  : numpy (256,256,3) float32
        driving_video : list of numpy (256,256,3) float32
        kp_detector   : loaded KPDetector
        cpu           : run on CPU if True

    Returns:
        int — index of the best matching driving frame
    """
    with torch.no_grad():
        source = torch.tensor(
            source_image[np.newaxis].astype(np.float32)
        ).permute(0, 3, 1, 2)
        if not cpu:
            source = source.cuda()

        kp_source = kp_detector(source)
        src_pts   = get_kp_pixels(kp_source['value'])

        best_idx  = 0
        best_dist = float('inf')

        for i, frame in enumerate(tqdm(driving_video, desc="Finding best frame")):
            drv_tensor = torch.tensor(
                frame[np.newaxis].astype(np.float32)
            ).permute(0, 3, 1, 2)
            if not cpu:
                drv_tensor = drv_tensor.cuda()

            kp_drv  = kp_detector(drv_tensor)
            drv_pts = get_kp_pixels(kp_drv['value'])

            dist = np.sum((src_pts - drv_pts) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_idx  = i

    print(f"  Best starting frame: {best_idx}  (distance={best_dist:.2f})")
    return best_idx


# ──────────────────────────────────────────────
#  Motion transfer  (full compositing pipeline)
# ──────────────────────────────────────────────

def motion_transfer(source_image, driving_video, generator, kp_detector,
                    cpu=False, use_color_correct=False, debug=False):
    """
    Full motion transfer pipeline — composites source face appearance
    onto driving video frames using Poisson blending.

    Per-frame sequence:
        1. Detect driving keypoints
        2. Apply temporal smoothing (alpha=0.60)
        3. Generate with RELATIVE mode
        4. Extract occlusion map
        5. Align generated frame to driving frame position
        6. Build hull mask + occlusion mask + combine
        7. Optionally colour-correct the generated face
        8. Poisson blend (NORMAL_CLONE, no post-blend fade)
        9. Fallback to alpha blend if Poisson fails
       10. Save debug visualisation for first 5 frames (if --debug)

    Args:
        source_image      : numpy (256,256,3) float32
        driving_video     : list of numpy (256,256,3) float32
        generator         : loaded OcclusionAwareGenerator
        kp_detector       : loaded KPDetector
        cpu               : run on CPU if True
        use_color_correct : apply per-channel colour correction before blending
        debug             : save side-by-side debug images for first 5 frames

    Returns:
        list of numpy arrays (256,256,3) float64 clipped to 0-1
    """
    os.makedirs('outputs', exist_ok=True)

    with torch.no_grad():
        result_frames = []

        # ── Prepare source tensor ──────────────────────────────
        source = torch.tensor(
            source_image[np.newaxis].astype(np.float32)
        ).permute(0, 3, 1, 2)
        if not cpu:
            source = source.cuda()

        driving = torch.tensor(
            np.array(driving_video)[np.newaxis].astype(np.float32)
        ).permute(0, 4, 1, 2, 3)

        # FIX 1: kp_source detected ONCE — stable anchor for every frame
        kp_source          = kp_detector(source)
        kp_driving_initial = kp_detector(driving[:, :, 0])

        # FIX 4: src_pts computed once — used as alignment anchor every frame
        src_pts = get_kp_pixels(kp_source['value'])

        # Temporal smoothing state
        prev_kp_value    = None
        prev_kp_jacobian = None

        for frame_idx in tqdm(range(driving.shape[2]), desc="Motion transfer"):

            driving_frame = driving[:, :, frame_idx]
            if not cpu:
                driving_frame = driving_frame.cuda()

            # ── Step 1: Detect driving keypoints ──────────────
            kp_driving = kp_detector(driving_frame)

            # ── Step 2: Temporal smoothing (FIX 2: alpha=0.60) ─
            kp_smooth = temporal_smooth(
                kp_driving['value'],
                kp_driving.get('jacobian', None),
                prev_kp_value,
                prev_kp_jacobian,
                alpha=0.60
            )
            prev_kp_value, prev_kp_jacobian = extract_prev_state(kp_smooth)

            # ── Step 3: Generate with RELATIVE mode (FIX 3) ───
            kp_norm = normalize_kp(
                kp_source=kp_source,
                kp_driving=kp_smooth,
                kp_driving_initial=kp_driving_initial,
                use_relative_movement=True,
                use_relative_jacobian=True,
                adapt_movement_scale=True
            )
            out = generator(source, kp_source=kp_source, kp_driving=kp_norm)

            generated    = np.transpose(
                out['prediction'].data.cpu().numpy(), [0, 2, 3, 1]
            )[0]                                       # (256,256,3) float32
            drive_np     = driving_video[frame_idx].copy()

            # ── Step 4: Extract occlusion map ─────────────────
            occ_map = out['occlusion_map']             # (1,1,64,64)

            # ── Step 5: Align generated frame (FIX 4) ─────────
            # Use src_pts → drv_pts transform (stable, no re-detection)
            drv_pts = get_kp_pixels(kp_driving['value'])

            tform   = SimilarityTransform()
            success = tform.estimate(src_pts, drv_pts)

            if success:
                aligned = sk_warp(
                    generated, tform.inverse,
                    output_shape=(256, 256),
                    preserve_range=True, mode='edge'
                ).astype(np.float64)

                # Warp occlusion map with same transform
                import torch.nn.functional as F_torch
                occ_up = F_torch.interpolate(
                    occ_map, size=(256, 256),
                    mode='bilinear', align_corners=False
                )
                occ_np = occ_up[0, 0].data.cpu().numpy()
                occ_warped = sk_warp(
                    occ_np, tform.inverse,
                    output_shape=(256, 256),
                    preserve_range=True, mode='constant', cval=0
                ).astype(np.float64)

                # Rebuild a fake tensor for build_occlusion_mask
                import torch as _torch
                occ_tensor_warped = _torch.tensor(
                    occ_warped[np.newaxis, np.newaxis]
                ).float()
            else:
                # Transform failed — use unaligned output
                aligned          = generated.astype(np.float64)
                occ_tensor_warped = occ_map.cpu()

            # ── Step 6: Build masks (FIX 5 & 6 in masking.py) ─
            hull_mask = build_hull_mask(drv_pts, shrink=0.85)
            occ_mask  = build_occlusion_mask(occ_tensor_warped, threshold=0.15)
            combined  = build_combined_mask(hull_mask, occ_mask)

            # ── Step 7: Optional colour correction ────────────
            if use_color_correct:
                aligned = color_correct(aligned, drive_np, combined)

            # ── Step 8: Poisson blend (FIX 7 & 8 in blending.py)
            blended = poisson_blend(aligned, drive_np, combined)
            if blended is None:
                # Fallback to alpha blend
                blended = alpha_blend(aligned, drive_np, combined)

            blended = np.clip(blended, 0.0, 1.0)

            # ── Step 9: Debug output (first 5 frames) ─────────
            if debug and frame_idx < 5:
                _save_debug_frame(
                    frame_idx, drive_np, generated,
                    combined, blended
                )

            result_frames.append(blended)

    print(f"  Motion transfer complete: {len(result_frames)} frames processed")
    return result_frames


# ──────────────────────────────────────────────
#  Debug helper
# ──────────────────────────────────────────────

def _save_debug_frame(frame_idx, driving, generated, mask, blended):
    """
    Save a side-by-side debug image for frame inspection.

    Layout: [driving | generated | mask | blended]

    Use this to diagnose:
      - Mask too small   → occlusion threshold too high
      - Seam visible     → NORMAL_CLONE not active, or post-Poisson fade active
      - Face misaligned  → alignment transform failed
      - Skin mismatch    → enable color_correct
    """
    from skimage import img_as_ubyte

    # Make mask visible as a greyscale image
    mask_vis = np.stack([mask, mask, mask], axis=-1)

    row = np.concatenate([
        np.clip(driving,   0, 1),
        np.clip(generated, 0, 1),
        np.clip(mask_vis,  0, 1),
        np.clip(blended,   0, 1),
    ], axis=1)                                         # join horizontally

    out_path = os.path.join('outputs', f'debug_frame_{frame_idx}.png')
    imageio.imwrite(out_path, img_as_ubyte(row))
    print(f"  Debug frame saved: {out_path}")