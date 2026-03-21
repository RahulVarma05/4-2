"""
pipeline/blending.py
--------------------
Responsible for ALL compositing operations.

Two blend modes:
  1. poisson_blend()  — primary method using cv2.seamlessClone (NORMAL_CLONE)
  2. alpha_blend()    — fallback when Poisson fails (mask too close to border)

Plus:
  3. color_correct()  — optional per-channel histogram matching to fix
                        skin tone mismatch between source and driving video

Bug fixes applied here vs the old demo.py:
  - MIXED_CLONE changed to NORMAL_CLONE
    (MIXED_CLONE let driving video skin texture bleed back through face centre)
  - Post-Poisson fade_mask removed entirely
    (re-applying alpha blend on top of Poisson was creating a visible halo ring)
"""

import numpy as np
from scipy.ndimage import gaussian_filter


# ──────────────────────────────────────────────
#  Poisson blending  (primary method)
# ──────────────────────────────────────────────

def poisson_blend(generated_rgb, driving_rgb, mask_2d):
    """
    Seamlessly composite generated_rgb onto driving_rgb using
    Poisson blending (cv2.seamlessClone with NORMAL_CLONE).

    How it works:
        seamlessClone solves a mathematical optimisation in the gradient
        domain. Inside the mask region it takes gradients (texture, edges)
        from the SOURCE (generated face). At the mask boundary it forces
        pixel values to match the DESTINATION (driving frame).
        This automatically handles colour and lighting differences at the
        boundary — no seams, no halos.

    Why NORMAL_CLONE not MIXED_CLONE:
        MIXED_CLONE at each pixel picks whichever gradient is stronger —
        source OR destination. For face compositing this is wrong: the driving
        video's skin texture has strong gradients that bleed back through the
        face centre, creating a partial overlay of both faces.
        NORMAL_CLONE takes gradients ONLY from the source (generated face),
        which is exactly what we want.

    Why no fade_mask after this:
        The old code applied a soft alpha blend AFTER seamlessClone:
            result = poisson_result * fade_mask + driving * (1-fade_mask)
        This re-introduced a semi-transparent ring at the boundary —
        the exact halo that Poisson blending eliminates. Trust the solver.

    Args:
        generated_rgb : numpy array (256, 256, 3) float, values 0-1
                        the aligned generated face frame
        driving_rgb   : numpy array (256, 256, 3) float, values 0-1
                        the original driving video frame
        mask_2d       : numpy array (256, 256) float, values 0-1
                        the combined mask from masking.py

    Returns:
        numpy array (256, 256, 3) float64, values 0-1
        or None if mask is too small for Poisson blending
    """
    import cv2

    # Convert float RGB → uint8 BGR for OpenCV
    src_bgr = (np.clip(generated_rgb, 0, 1) * 255).astype(np.uint8)[:, :, ::-1]
    dst_bgr = (np.clip(driving_rgb,   0, 1) * 255).astype(np.uint8)[:, :, ::-1]

    # Binary mask for seamlessClone — use low threshold (0.05) to give
    # the Poisson solver a generous region for gradient blending
    poisson_mask = (mask_2d > 0.05).astype(np.uint8) * 255

    # Find the centroid of the mask (required by seamlessClone)
    ys, xs = np.where(poisson_mask > 0)
    if len(xs) < 50:
        # Mask too small — Poisson blending cannot work reliably
        return None

    center = (int(xs.mean()), int(ys.mean()))

    # Check mask does not touch image border — seamlessClone fails if it does
    if (ys.min() == 0 or ys.max() == 255 or
            xs.min() == 0 or xs.max() == 255):
        # Erode mask slightly away from border
        kernel = np.ones((5, 5), np.uint8)
        poisson_mask = cv2.erode(poisson_mask, kernel, iterations=2)
        ys, xs = np.where(poisson_mask > 0)
        if len(xs) < 50:
            return None
        center = (int(xs.mean()), int(ys.mean()))

    try:
        # NORMAL_CLONE: gradients from source only, colour matched at boundary
        result_bgr = cv2.seamlessClone(
            src_bgr, dst_bgr, poisson_mask, center, cv2.NORMAL_CLONE
        )
        # Convert back to float RGB — return directly, NO additional blending
        result = result_bgr[:, :, ::-1].astype(np.float64) / 255.0
        return result

    except cv2.error as e:
        print(f"  WARNING: seamlessClone failed ({e}) — falling back to alpha blend")
        return None


# ──────────────────────────────────────────────
#  Alpha blending  (fallback)
# ──────────────────────────────────────────────

def alpha_blend(generated_rgb, driving_rgb, mask_2d):
    """
    Simple soft alpha blend — used as fallback when Poisson blending fails.

    result = generated * mask + driving * (1 - mask)

    Less seamless than Poisson blending (colour mismatch at boundary is
    not corrected) but always works regardless of mask position.

    Args:
        generated_rgb : numpy array (256, 256, 3) float 0-1
        driving_rgb   : numpy array (256, 256, 3) float 0-1
        mask_2d       : numpy array (256, 256) float 0-1

    Returns:
        numpy array (256, 256, 3) float64, values 0-1
    """
    mask_3d = mask_2d[:, :, np.newaxis]               # (256, 256, 1) for broadcast
    blended = generated_rgb * mask_3d + driving_rgb * (1.0 - mask_3d)
    return blended.astype(np.float64)


# ──────────────────────────────────────────────
#  Color correction  (optional improvement)
# ──────────────────────────────────────────────

def color_correct(generated_rgb, driving_rgb, mask_2d):
    """
    Match the colour statistics of the generated face to the driving frame
    to fix skin tone mismatch caused by different lighting conditions.

    Method: per-channel mean+std matching (histogram matching approximation)
        For each channel (R, G, B):
            corrected = (generated - gen_mean) / gen_std * drv_std + drv_mean

    This rescales the generated channel so its mean and standard deviation
    match the driving frame's values within the masked region.

    When to use:
        When the source image has noticeably different lighting than the
        driving video (e.g. warm indoor photo vs cool outdoor video).
        Enable with --color_correct flag in main.py.

    Args:
        generated_rgb : numpy array (256, 256, 3) float 0-1  — generated face
        driving_rgb   : numpy array (256, 256, 3) float 0-1  — driving frame
        mask_2d       : numpy array (256, 256) float 0-1     — face region mask

    Returns:
        numpy array (256, 256, 3) float64 — colour-corrected generated frame
    """
    face_region = mask_2d > 0.5                        # binary face mask
    if face_region.sum() < 100:
        return generated_rgb.astype(np.float64)        # too few pixels, skip

    corrected = generated_rgb.copy().astype(np.float64)

    for c in range(3):
        gen_vals = generated_rgb[:, :, c][face_region]
        drv_vals = driving_rgb[:, :, c][face_region]

        gen_mean = gen_vals.mean()
        gen_std  = max(gen_vals.std(), 1e-6)           # avoid division by zero
        drv_mean = drv_vals.mean()
        drv_std  = max(drv_vals.std(), 1e-6)

        # Rescale this channel to match driving statistics
        corrected[:, :, c] = (
            (generated_rgb[:, :, c] - gen_mean) / gen_std * drv_std + drv_mean
        )

    return np.clip(corrected, 0.0, 1.0)