"""
pipeline/face_composition.py
----------------------------
Face composition pipeline mode
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
    temporal_smooth, extract_prev_state, init_conv_lstm_state
)
from pipeline.masking import (
    build_hull_mask, build_occlusion_mask, build_combined_mask
)
from pipeline.blending import (
    poisson_blend, alpha_blend, color_correct
)


# ─────────────────────────────────────────────────────────────────────────────
#  Face composition mode
# ─────────────────────────────────────────────────────────────────────────────

def face_composition(source_image, driving_video, generator, kp_detector,
                    cpu=False, use_color_correct=False, debug=False):
    """
    Original compositing pipeline renamed to face composition.
    """
    import torch.nn.functional as F_torch
    os.makedirs('outputs', exist_ok=True)

    with torch.no_grad():
        result_frames = []
        source = torch.tensor(
            source_image[np.newaxis].astype(np.float32)
        ).permute(0, 3, 1, 2)
        if not cpu:
            source = source.cuda()

        driving = torch.tensor(
            np.array(driving_video)[np.newaxis].astype(np.float32)
        ).permute(0, 4, 1, 2, 3)

        kp_source          = kp_detector(source)
        kp_driving_initial = kp_detector(driving[:, :, 0])
        src_pts            = get_kp_pixels(kp_source['value'])
        prev_kp_value      = None
        prev_kp_jacobian   = None
        conv_state         = init_conv_lstm_state()

        for frame_idx in tqdm(range(driving.shape[2]), desc="Face composition"):
            driving_frame = driving[:, :, frame_idx]
            if not cpu:
                driving_frame = driving_frame.cuda()

            kp_driving = kp_detector(driving_frame)
            kp_smooth  = temporal_smooth(
                kp_driving['value'], kp_driving.get('jacobian', None),
                prev_kp_value, prev_kp_jacobian, alpha=0.60,
                use_conv_lstm=True, conv_lstm_state=conv_state
            )
            conv_state = kp_smooth.get('conv_state', (None, None))
            prev_kp_value, prev_kp_jacobian = extract_prev_state(kp_smooth)
            kp_norm = normalize_kp(
                kp_source=kp_source, kp_driving=kp_smooth,
                kp_driving_initial=kp_driving_initial,
                use_relative_movement=True, use_relative_jacobian=True,
                adapt_movement_scale=True
            )
            out       = generator(source, kp_source=kp_source, kp_driving=kp_norm)
            generated = np.transpose(
                out['prediction'].data.cpu().numpy(), [0, 2, 3, 1]
            )[0]
            drive_np  = driving_video[frame_idx].copy()
            occ_map   = out['occlusion_map']
            drv_pts   = get_kp_pixels(kp_driving['value'])

            tform   = SimilarityTransform()
            success = tform.estimate(src_pts, drv_pts)

            if success:
                aligned = sk_warp(
                    generated, tform.inverse,
                    output_shape=(256, 256),
                    preserve_range=True, mode='edge'
                ).astype(np.float64)
                occ_up = F_torch.interpolate(
                    occ_map, size=(256, 256),
                    mode='bilinear', align_corners=False
                )
                occ_np = occ_up[0, 0].data.cpu().numpy()
                occ_warped = sk_warp(
                    occ_np, tform.inverse, output_shape=(256, 256),
                    preserve_range=True, mode='constant', cval=0
                ).astype(np.float64)
                occ_tensor = torch.tensor(
                    occ_warped[np.newaxis, np.newaxis]
                ).float()
            else:
                aligned    = generated.astype(np.float64)
                occ_tensor = F_torch.interpolate(
                    occ_map, size=(256, 256),
                    mode='bilinear', align_corners=False
                ).cpu()

            hull_mask = build_hull_mask(drv_pts, shrink=0.85)
            occ_mask  = build_occlusion_mask(occ_tensor, threshold=0.15)
            combined  = build_combined_mask(hull_mask, occ_mask)
            if use_color_correct:
                aligned = color_correct(aligned, drive_np, combined)
            blended = poisson_blend(aligned, drive_np, combined)
            if blended is None:
                blended = alpha_blend(aligned, drive_np, combined)
            result_frames.append(np.clip(blended, 0.0, 1.0))

    print(f"Face composition complete: {len(result_frames)} frames")
    return result_frames


# ─────────────────────────────────────────────────────────────────────────────
#  Debug helper
# ─────────────────────────────────────────────────────────────────────────────

def _save_debug_frame(frame_idx, driving, generated, mask, blended, prefix='frame'):
    """
    Save side-by-side debug image:
    [driving | generated | mask | blended]
    """
    from skimage import img_as_ubyte
    mask_vis = np.stack([mask, mask, mask], axis=-1)
    row = np.concatenate([
        np.clip(driving,   0, 1),
        np.clip(generated, 0, 1),
        np.clip(mask_vis,  0, 1),
        np.clip(blended,   0, 1),
    ], axis=1)
    path = os.path.join('outputs', f'debug_{prefix}_{frame_idx}.png')
    imageio.imwrite(path, img_as_ubyte(row))
    print(f"  Debug saved: {path}")
