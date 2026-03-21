"""
pipeline/loader.py
------------------
Responsible for ALL file input/output operations.
- Loading model checkpoints
- Loading source image
- Loading driving video
- Saving output video
- Muxing audio from driving video into output

Nothing else belongs here. No model logic, no blending, no keypoints.
"""

import os
import sys

# Allow importing from fomm_core without modifying it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fomm_core'))

import yaml
import imageio
import numpy as np
import torch
from skimage.transform import resize
from skimage import img_as_ubyte
from sync_batchnorm import DataParallelWithCallback
from modules.generator import OcclusionAwareGenerator
from modules.keypoint_detector import KPDetector


# ──────────────────────────────────────────────
#  Model loading
# ──────────────────────────────────────────────

def load_checkpoints(config_path, checkpoint_path, cpu=False):
    """
    Load the FOMM generator and keypoint detector from a checkpoint file.

    Args:
        config_path    : path to vox-256.yaml (inside fomm_core/config/)
        checkpoint_path: path to vox-cpk.pth.tar (inside checkpoints/)
        cpu            : if True, run on CPU instead of GPU

    Returns:
        generator    : OcclusionAwareGenerator in eval mode
        kp_detector  : KPDetector in eval mode
    """
    with open(config_path) as f:
        config = yaml.full_load(f)

    # Auto-detect: if PyTorch has no CUDA support, fall back to CPU silently
    if not cpu and not torch.cuda.is_available():
        print("  WARNING: CUDA not available — running on CPU.")
        print("  Add --cpu to your command to suppress this warning.")
        cpu = True

    # Build generator
    generator = OcclusionAwareGenerator(
        **config['model_params']['generator_params'],
        **config['model_params']['common_params']
    )
    if not cpu:
        generator.cuda()

    # Build keypoint detector
    kp_detector = KPDetector(
        **config['model_params']['kp_detector_params'],
        **config['model_params']['common_params']
    )
    if not cpu:
        kp_detector.cuda()

    # Always load weights to CPU first, then move if needed
    checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
    generator.load_state_dict(checkpoint['generator'])
    kp_detector.load_state_dict(checkpoint['kp_detector'])

    # Wrap for multi-GPU only when real CUDA is available
    if not cpu:
        generator   = DataParallelWithCallback(generator)
        kp_detector = DataParallelWithCallback(kp_detector)

    generator.eval()
    kp_detector.eval()

    print(f"  Loaded checkpoint: {checkpoint_path}")
    return generator, kp_detector


# ──────────────────────────────────────────────
#  Image / video loading
# ──────────────────────────────────────────────

def load_source_image(path):
    """
    Load a source image and prepare it for FOMM.

    - Reads the image file
    - Resizes to 256x256 (FOMM's required input size)
    - Drops alpha channel if present (keeps only RGB)
    - Returns float32 numpy array with values in range [0, 1]

    Args:
        path: path to source image (jpg, png, etc.)

    Returns:
        numpy array of shape (256, 256, 3), dtype float32, values 0-1
    """
    image = imageio.imread(path)
    image = resize(image, (256, 256))[..., :3]          # resize + drop alpha
    image = image.astype(np.float32)
    print(f"  Loaded source image: {path}  shape={image.shape}")
    return image


def load_driving_video(path, max_frames=None):
    """
    Load a driving video and prepare each frame for FOMM.

    - Reads every frame from the video file
    - Resizes each frame to 256x256
    - Drops alpha channel if present
    - Optionally limits to max_frames (useful for fast iteration)

    Args:
        path      : path to driving video (mp4, avi, etc.)
        max_frames: if set, only load this many frames (None = load all)

    Returns:
        frames : list of numpy arrays, each shape (256, 256, 3), float32, 0-1
        fps    : frames per second of the original video (used when saving)
    """
    reader = imageio.get_reader(path)
    fps    = reader.get_meta_data()['fps']

    frames = []
    try:
        for frame in reader:
            frames.append(frame)
            if max_frames and len(frames) >= max_frames:
                break
    except RuntimeError:
        # imageio raises RuntimeError at end of some video files — this is normal
        pass
    reader.close()

    # Resize all frames to 256x256 and normalise to float32 0-1
    frames = [resize(f, (256, 256))[..., :3].astype(np.float32) for f in frames]

    print(f"  Loaded driving video : {path}")
    print(f"  Frames: {len(frames)}  FPS: {fps:.2f}  Resolution: 256x256")
    return frames, fps


# ──────────────────────────────────────────────
#  Video saving
# ──────────────────────────────────────────────

def save_video(frames, output_path, fps):
    """
    Save a list of float32 numpy frames as an MP4 video.

    Args:
        frames      : list of numpy arrays, shape (H, W, 3), values 0-1
        output_path : where to save the video (e.g. outputs/result.mp4)
        fps         : frames per second for the output video
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    imageio.mimsave(output_path, [img_as_ubyte(f) for f in frames], fps=fps)
    print(f"  Saved video: {output_path}  ({len(frames)} frames @ {fps:.2f} fps)")


# ──────────────────────────────────────────────
#  Audio muxing
# ──────────────────────────────────────────────

def mux_audio(video_path, audio_source_path, output_path):
    """
    Copy the audio track from audio_source_path into video_path,
    saving the result to output_path.

    Uses ffmpeg with -c copy (no re-encoding) so it is fast.
    Falls back gracefully if the source has no audio track.

    Args:
        video_path       : the video file (no audio) — e.g. outputs/result.mp4
        audio_source_path: the driving video (has audio) — e.g. samples/driving.mp4
        output_path      : final output with audio — e.g. outputs/result_audio.mp4
    """
    try:
        import ffmpeg
        from tempfile import NamedTemporaryFile
        from shutil import copyfileobj
        from os.path import splitext

        ext = splitext(output_path)[1]
        with NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp_path = tmp.name

        (
            ffmpeg
            .output(
                ffmpeg.input(video_path).video,
                ffmpeg.input(audio_source_path).audio,
                tmp_path,
                vcodec='copy',
                acodec='aac',
                strict='experimental'
            )
            .overwrite_output()
            .run(quiet=True)
        )

        # Replace original with audio version
        os.replace(tmp_path, output_path)
        print(f"  Audio muxed into: {output_path}")

    except ffmpeg.Error as e:
        print("  WARNING: Could not mux audio.")
        print("  The driving video may have no audio track, or ffmpeg failed.")
        print(f"  Details: {e}")
    except Exception as e:
        print(f"  WARNING: Audio mux skipped — {e}")