"""
main.py
-------
Command-line entry point. Contains ONLY argument parsing and top-level
call sequence. No model logic, no blending, no keypoints here.

Usage examples:

  # Test base animation (do this FIRST)
  python main.py --mode animate --max_frames 30

  # Motion transfer with debug frames
  python main.py --mode motion_transfer --max_frames 30 --debug

  # Full run with audio
  python main.py --mode motion_transfer --find_best_frame --audio

  # Full run with colour correction + audio
  python main.py --mode motion_transfer --find_best_frame --color_correct --audio
"""

import os
import sys
from argparse import ArgumentParser

from pipeline.loader import (
    load_checkpoints, load_source_image,
    load_driving_video, save_video, mux_audio
)
from pipeline.motion_transfer import (
    make_animation, find_best_frame, motion_transfer
)


def parse_args():
    parser = ArgumentParser(description="FOMM Motion Transfer Pipeline")

    # ── Required paths ──────────────────────────────────────────────
    parser.add_argument(
        "--config",
        default=os.path.join("fomm_core", "config", "vox-256.yaml"),
        help="Path to FOMM config YAML (default: fomm_core/config/vox-256.yaml)"
    )
    parser.add_argument(
        "--checkpoint",
        default=os.path.join("checkpoints", "vox-cpk.pth.tar"),
        help="Path to model checkpoint (default: checkpoints/vox-cpk.pth.tar)"
    )
    parser.add_argument(
        "--source_image",
        default=os.path.join("samples", "source_image.jpg"),
        help="Path to source image (default: samples/source_image.jpg)"
    )
    parser.add_argument(
        "--driving_video",
        default=os.path.join("samples", "driving.mp4"),
        help="Path to driving video (default: samples/driving.mp4)"
    )
    parser.add_argument(
        "--result_video",
        default=os.path.join("outputs", "result.mp4"),
        help="Path to save output video (default: outputs/result.mp4)"
    )

    # ── Mode ────────────────────────────────────────────────────────
    parser.add_argument(
        "--mode",
        default="animate",
        choices=["animate", "motion_transfer"],
        help="Pipeline mode:\n"
             "  animate         — pure FOMM generation, no compositing\n"
             "  motion_transfer — full pipeline with Poisson blending"
    )

    # ── Flags ───────────────────────────────────────────────────────
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Run on CPU (slow but works without a GPU)"
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Copy audio track from driving video into output"
    )
    parser.add_argument(
        "--find_best_frame",
        action="store_true",
        help="Start animation from the driving frame closest in pose "
             "to the source image — eliminates frame-0 snap/jump"
    )
    parser.add_argument(
        "--color_correct",
        action="store_true",
        help="Apply per-channel colour correction to fix skin tone mismatch"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save side-by-side debug images for first 5 frames into outputs/"
    )
    parser.add_argument(
        "--max_frames",
        type=int,
        default=None,
        help="Only process this many frames — use 30 for fast testing"
    )

    return parser.parse_args()


def main():
    opt = parse_args()

    print("\n" + "=" * 55)
    print("  FOMM Motion Transfer Pipeline")
    print("=" * 55)
    print(f"  Mode          : {opt.mode}")
    print(f"  Source image  : {opt.source_image}")
    print(f"  Driving video : {opt.driving_video}")
    print(f"  Checkpoint    : {opt.checkpoint}")
    print(f"  Output        : {opt.result_video}")
    if opt.max_frames:
        print(f"  Max frames    : {opt.max_frames}  (test mode)")
    print("=" * 55 + "\n")

    # ── Load inputs ─────────────────────────────────────────────────
    print("[1/4] Loading source image ...")
    source_image = load_source_image(opt.source_image)

    print("\n[2/4] Loading driving video ...")
    driving_video, fps = load_driving_video(opt.driving_video, max_frames=opt.max_frames)

    print("\n[3/4] Loading model checkpoint ...")
    generator, kp_detector = load_checkpoints(
        config_path=opt.config,
        checkpoint_path=opt.checkpoint,
        cpu=opt.cpu
    )

    # ── Optionally find best starting frame ─────────────────────────
    if opt.find_best_frame and opt.mode in ("animate", "motion_transfer"):
        print("\n  Finding best starting frame ...")
        best_idx      = find_best_frame(source_image, driving_video, kp_detector, cpu=opt.cpu)
        driving_video = driving_video[best_idx:]
        print(f"  Driving video sliced to {len(driving_video)} frames from index {best_idx}")

    # ── Run pipeline ─────────────────────────────────────────────────
    print(f"\n[4/4] Running {opt.mode} pipeline ...")

    if opt.mode == "animate":
        predictions = make_animation(
            source_image, driving_video,
            generator, kp_detector,
            relative=True, adapt_scale=True, cpu=opt.cpu
        )

    elif opt.mode == "motion_transfer":
        predictions = motion_transfer(
            source_image, driving_video,
            generator, kp_detector,
            cpu=opt.cpu,
            use_color_correct=opt.color_correct,
            debug=opt.debug
        )

    # ── Save output ──────────────────────────────────────────────────
    print(f"\n  Saving output video ...")
    save_video(predictions, opt.result_video, fps)

    # ── Mux audio ────────────────────────────────────────────────────
    if opt.audio:
        print("  Muxing audio from driving video ...")
        mux_audio(opt.result_video, opt.driving_video, opt.result_video)

    print("\n" + "=" * 55)
    print(f"  Done!  Output saved to: {opt.result_video}")
    if opt.debug:
        print("  Debug frames saved to:  outputs/debug_frame_0-4.png")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()