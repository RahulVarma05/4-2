"""
pipeline/masking.py
-------------------
Responsible for building ALL masks used in the compositing pipeline.

Three masks are built per frame and combined:
  1. Hull mask    — covers the face region using keypoint ConvexHull
  2. Occlusion mask — covers pixels the generator is confident about
  3. Combined mask  — intersection of both, with feathered edges

Bug fixes applied here vs the old demo.py:
  - Hull shrink raised from 0.60 to 0.85
    (old value only covered 60% of face, causing seams at cheeks/forehead)
  - Occlusion threshold lowered from 0.40 to 0.15
    (old threshold discarded most valid pixels, leaving patchy mask)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fomm_core'))

import numpy as np
import torch
import torch.nn.functional as F
from scipy.ndimage import gaussian_filter
from scipy.spatial import ConvexHull
from skimage.draw import polygon


# ──────────────────────────────────────────────
#  Hull mask
# ──────────────────────────────────────────────

def build_hull_mask(kp_pixels, image_size=256, shrink=0.85):
    """
    Build a soft binary mask covering the face region using the
    ConvexHull of the driving frame's keypoints.

    Steps:
      1. Compute the centroid of all keypoints
      2. Compute the ConvexHull of all keypoints
      3. Shrink each hull vertex toward the centroid by `shrink` factor
         (shrink=0.85 means hull vertices move 15% closer to centre)
      4. Fill the shrunk polygon to create a binary mask
      5. Apply gaussian blur to feather the mask edges smoothly

    Why shrink=0.85 (not the old 0.60):
        At 0.60 the mask covered only 60% of the face hull —
        roughly just the nose and inner cheek area. The forehead,
        outer cheeks, and chin were excluded, so the blend boundary
        fell in the MIDDLE of the face, creating obvious seam lines.
        At 0.85 the mask covers the full inner face up to the natural
        face-background boundary.

    Args:
        kp_pixels  : numpy array shape (num_kp, 2) — pixel coordinates
                     as returned by get_kp_pixels()
        image_size : output mask size (default 256)
        shrink     : how much to shrink hull toward centroid (0-1)
                     1.0 = full hull, 0.5 = half-size, 0.85 = recommended

    Returns:
        numpy array shape (image_size, image_size), dtype float64
        values smoothly between 0.0 and 1.0
    """
    h = w = image_size
    mask = np.zeros((h, w), dtype=np.float64)

    # Centroid of all keypoints
    cx = kp_pixels[:, 0].mean()
    cy = kp_pixels[:, 1].mean()

    try:
        # Compute convex hull of keypoints
        hull = ConvexHull(kp_pixels)
        hull_pts = kp_pixels[hull.vertices]        # just the boundary points

        # Shrink each boundary point toward the centroid
        shrunk_x = cx + (hull_pts[:, 0] - cx) * shrink
        shrunk_y = cy + (hull_pts[:, 1] - cy) * shrink

        # Fill the shrunk polygon
        rr, cc = polygon(shrunk_y, shrunk_x, shape=(h, w))
        mask[rr, cc] = 1.0

    except Exception:
        # Fallback: use an ellipse if ConvexHull fails
        # (happens when keypoints are collinear or too few unique points)
        rx = max(np.ptp(kp_pixels[:, 0]) * 0.38, 20)
        ry = max(np.ptp(kp_pixels[:, 1]) * 0.38, 20)
        Y, X = np.mgrid[0:h, 0:w].astype(np.float64)
        dist = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
        mask = np.clip(1.5 - dist, 0.0, 1.0)

    # Feather edges with gaussian blur for smooth blending boundary
    mask = gaussian_filter(mask, sigma=6)
    return mask


# ──────────────────────────────────────────────
#  Occlusion mask
# ──────────────────────────────────────────────

def build_occlusion_mask(occ_map_tensor, image_size=256, threshold=0.15):
    """
    Build a mask from the generator's occlusion map output.

    The occlusion map (shape 1x1x64x64) indicates for each spatial
    position how confident the generator is that the pixel is valid
    and unoccluded. Values closer to 1 = high confidence.

    Steps:
      1. Upsample 64x64 → 256x256 using bilinear interpolation
      2. Threshold: pixels above threshold become 1.0, below become 0.0
      3. Apply gaussian blur to feather the edges

    Why threshold=0.15 (not the old 0.40):
        FOMM's occlusion map values for a front-facing face are
        typically between 0.1 and 0.35 in the face interior.
        Using 0.40 was discarding almost all face pixels, leaving
        a thin patchy mask. At 0.15 all model-confident pixels
        are correctly recovered.

    Args:
        occ_map_tensor : torch tensor shape (1, 1, 64, 64)
                         as returned in out['occlusion_map']
        image_size     : upsample target size (default 256)
        threshold      : confidence threshold (default 0.15)

    Returns:
        numpy array shape (image_size, image_size), dtype float64
        values between 0.0 and 1.0
    """
    # Upsample 64x64 → 256x256
    occ_up = F.interpolate(
        occ_map_tensor,
        size=(image_size, image_size),
        mode='bilinear',
        align_corners=False
    )
    occ_np = occ_up[0, 0].data.cpu().numpy()          # (256, 256)

    # Threshold and feather
    occ_binary = (occ_np > threshold).astype(np.float64)
    occ_binary = gaussian_filter(occ_binary, sigma=3)
    return occ_binary


# ──────────────────────────────────────────────
#  Combined mask
# ──────────────────────────────────────────────

def build_combined_mask(hull_mask, occlusion_mask):
    """
    Combine the hull mask and occlusion mask into one final blending mask.

    Method:
      - Multiply them element-wise (intersection of both)
        Hull covers the face region.
        Occlusion covers only confident pixels.
        Product = pixels that are BOTH inside the face AND confidently generated.
      - Apply a final gaussian blur for extra-smooth edges
      - Normalise so the maximum value is exactly 1.0

    Args:
        hull_mask     : numpy array (H, W) float64 from build_hull_mask()
        occlusion_mask: numpy array (H, W) float64 from build_occlusion_mask()

    Returns:
        numpy array (H, W) float64, values 0.0 to 1.0
    """
    combined = hull_mask * occlusion_mask
    combined = gaussian_filter(combined, sigma=4)

    # Normalise to 0-1
    max_val = combined.max()
    if max_val > 0:
        combined = combined / max_val

    return combined