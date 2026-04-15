"""
pipeline/motion_transfer.py
----------------------------
Three pipeline modes:

  1. make_animation()  — PRIMARY MODE:
                         Source image gets animated by driving video motion.
                         Output = source image moving like driving video.
                         Background and clothes come from the SOURCE IMAGE.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fomm_core'))

import numpy as np
import torch
from tqdm import tqdm

from pipeline.keypoints import (
    normalize_kp, get_kp_pixels,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Mode 1 — Base animation
# ─────────────────────────────────────────────────────────────────────────────

def make_animation(source_image, driving_video, generator, kp_detector,
                   relative=True, adapt_scale=True, cpu=False):
    """
    PRIMARY MODE — Pure FOMM animation.

    The source image is animated by the driving video's motion:
      - Pose, expression, and head movement come from the DRIVING VIDEO.
      - Appearance (face, clothes, background) comes from the SOURCE IMAGE.

    Use this as the default pipeline mode. It produces the cleanest results
    with no compositing artefacts since the entire output frame is generated
    directly by the FOMM model without any masking or blending.

    Args:
        source_image  : numpy array (256, 256, 3) float32 0-1
        driving_video : list of numpy arrays (256, 256, 3) float32 0-1
        generator     : loaded OcclusionAwareGenerator
        kp_detector   : loaded KPDetector
        relative      : use relative keypoint movement (default True)
        adapt_scale   : adapt movement scale to face size (default True)
        cpu           : run on CPU if True

    Returns:
        list of numpy arrays (256, 256, 3) float64, one per driving frame
    """
    with torch.no_grad():
        predictions = []
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

        for frame_idx in tqdm(range(driving.shape[2]), desc="Motion transfer"):
            driving_frame = driving[:, :, frame_idx]
            if not cpu:
                driving_frame = driving_frame.cuda()
            kp_driving = kp_detector(driving_frame)
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


# ─────────────────────────────────────────────────────────────────────────────
#  find_best_frame
# ─────────────────────────────────────────────────────────────────────────────

def find_best_frame(source_image, driving_video, kp_detector, cpu=False):
    """
    Find driving frame whose pose best matches source image.
    Eliminates the sudden jump at frame 0 of the motion transfer.
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
            t = torch.tensor(
                frame[np.newaxis].astype(np.float32)
            ).permute(0, 3, 1, 2)
            if not cpu:
                t = t.cuda()
            drv_pts = get_kp_pixels(kp_detector(t)['value'])
            dist    = np.sum((src_pts - drv_pts) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_idx  = i

    print(f"  Best frame: {best_idx}  (dist={best_dist:.1f})")
    return best_idx


