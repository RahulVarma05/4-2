import os
import requests
from tqdm import tqdm

checkpoint_url = "https://github.com/graphemecluster/first-order-model-demo/releases/download/checkpoints/vox-cpk.pth.tar"
checkpoint_path = os.path.join("checkpoints", "vox-cpk.pth.tar")


def download_file(url, target_path):
    if os.path.exists(target_path):
        print(f"  Already exists: {target_path}")
        return True

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    print(f"  Downloading from: {url}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"  ERROR: Could not download — {e}")
        return False

    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024

    with open(target_path, "wb") as f:
        for data in tqdm(
            response.iter_content(block_size),
            total=total_size // block_size if total_size else None,
            unit="KB",
            unit_scale=True,
        ):
            f.write(data)
    print(f"  Saved to {target_path}")
    return True


if __name__ == "__main__":

    print("\n=== Step 1: Model checkpoint ===")
    if os.path.exists(checkpoint_path):
        print(f"  Already exists: {checkpoint_path}")
    else:
        download_file(checkpoint_url, checkpoint_path)

    print("\n=== Step 2: Sample driving video ===")
    user_video = os.path.join("samples", "driving.mp4")
    if os.path.exists(user_video):
        print(f"  Found existing video at {user_video} — skipping download.")
    else:
        print("  The original sample video URL is no longer available online.")
        print("  ACTION REQUIRED: Manually place a short MP4 video of a face")
        print(r"  into the samples\ folder and name it  driving.mp4")
        print()
        print("  Good free sources for a test driving video:")
        print("  1. Record yourself talking for 5-10 seconds with your phone")
        print("  2. Download any short talking-head clip from YouTube (720p, MP4)")
        print("  3. Use the official FOMM Colab notebook sample videos:")
        print("     https://github.com/AliaksandrSiarohin/first-order-model")

    print("\n=== Step 3: Source image ===")
    user_source = os.path.join("samples", "source_image.jpg")
    if os.path.exists(user_source):
        print(f"  Found your source image at {user_source} — ready to use.")
    else:
        print(r"  ACTION REQUIRED: Copy your photo into samples\ and name it source_image.jpg")
        print("  (A clear front-facing portrait works best)")

    print("\n=== Step 4: FOMM core repo ===")
    if os.path.isdir("fomm_core"):
        print("  fomm_core\\ already exists — good.")
    else:
        print("  fomm_core\\ not found.")
        print("  ACTION REQUIRED: Run this command:")
        print("  git clone https://github.com/AliaksandrSiarohin/first-order-model fomm_core")

    print("\n=== Setup summary ===")

    def check(path, label):
        status = "  OK     " if os.path.exists(path) else "  MISSING"
        print(f"{status}  {label:35s}  ({path})")

    check(checkpoint_path,                             "Model checkpoint")
    check(os.path.join("samples", "driving.mp4"),      "Driving video")
    check(os.path.join("samples", "source_image.jpg"), "Your source image")
    check("fomm_core",                                 "FOMM core repo")

    print()
    print("Fix any MISSING items above before moving to Phase 2.")