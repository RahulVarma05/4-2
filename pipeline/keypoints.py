"""
pipeline/keypoints.py
---------------------
Responsible for ALL keypoint processing logic.
- Converting keypoint tensors to pixel coordinates
- Temporal smoothing (EMA) to eliminate frame-to-frame jitter
- Re-exporting normalize_kp from fomm_core so other files
  don't need to reach into fomm_core directly

Nothing else belongs here. No blending, no masking, no file I/O.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fomm_core'))

import numpy as np
import torch

# Re-export normalize_kp from fomm_core so the rest of our code
# can do:  from pipeline.keypoints import normalize_kp
# instead of reaching into fomm_core directly
from animate import normalize_kp


# ──────────────────────────────────────────────
#  Coordinate conversion
# ──────────────────────────────────────────────

def get_kp_pixels(kp_tensor, image_size=256):
    """
    Convert FOMM keypoint tensor coordinates from [-1, 1] range
    to pixel coordinates in [0, image_size] range.

    FOMM outputs keypoints normalised to [-1, 1] where:
        -1 = left/top edge of the image
        +1 = right/bottom edge of the image

    We need pixel coordinates (0 to 255) for:
        - SimilarityTransform alignment
        - ConvexHull mask building
        - Debug visualisation

    Args:
        kp_tensor  : torch tensor of shape (1, num_kp, 2)
                     as returned by kp_detector(frame)['value']
        image_size : target pixel range (default 256 for FOMM)

    Returns:
        numpy array of shape (num_kp, 2)
        each row is [x_pixel, y_pixel]
    """
    kp_np = kp_tensor[0].data.cpu().numpy()          # (num_kp, 2)
    kp_px = (kp_np + 1.0) / 2.0 * image_size         # map [-1,1] → [0,256]
    return kp_px                                       # shape (num_kp, 2)


# ──────────────────────────────────────────────
#  Temporal smoothing
# ──────────────────────────────────────────────

def init_conv_lstm_state():
    """
    Initialize ConvLSTM hidden state and cell state.
    """
    return None, None

def temporal_smooth(kp_value, kp_jacobian,
                    prev_kp_value, prev_kp_jacobian,
                    alpha=0.60, use_conv_lstm=False,
                    conv_lstm_state=(None, None)):
    """
    Apply either Exponential Moving Average (EMA) or ConvLSTM smoothing 
    to keypoints across consecutive video frames to eliminate jitter.
    """
    result = {}

    if use_conv_lstm:
        from pipeline.conv_lstm import get_conv_lstm
        model = get_conv_lstm(kp_value.shape[1], kp_value.device)
        state_in = conv_lstm_state if conv_lstm_state[0] is not None else None
        smoothed_value, new_state = model(kp_value, state_in)
        result['value'] = smoothed_value
        result['conv_state'] = new_state
    else:
        # EMA route
        if prev_kp_value is None:
            smoothed_value = kp_value
        else:
            smoothed_value = alpha * kp_value + (1.0 - alpha) * prev_kp_value
        result['value'] = smoothed_value

    # Apply EMA to jacobians if present
    if kp_jacobian is not None and prev_kp_jacobian is not None:
        smoothed_jacobian = alpha * kp_jacobian + (1.0 - alpha) * prev_kp_jacobian
        result['jacobian'] = smoothed_jacobian
    elif kp_jacobian is not None:
        result['jacobian'] = kp_jacobian

    return result


def extract_prev_state(smoothed_kp):
    """
    Helper to extract the tensors to store as 'previous' state
    for the next frame's smoothing call.

    Args:
        smoothed_kp: dict with 'value' and optionally 'jacobian'

    Returns:
        (prev_value, prev_jacobian) — both cloned tensors, detached from graph
    """
    prev_value    = smoothed_kp['value'].clone().detach()
    prev_jacobian = smoothed_kp['jacobian'].clone().detach() \
                    if 'jacobian' in smoothed_kp else None
    return prev_value, prev_jacobian