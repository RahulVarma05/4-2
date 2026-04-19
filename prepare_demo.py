import os
import requests
from tqdm import tqdm

def download_file(url, dest):
    if os.path.exists(dest):
        print(f"{dest} already exists. Skipping download.")
        return
    
    print(f"Downloading model checkpoint to {dest}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    with open(dest, 'wb') as f, tqdm(
        desc=dest,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

if __name__ == "__main__":
    # Create required directories
    dirs = ['checkpoints', 'samples', 'web_uploads', 'web_results']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Ensured directory exists: {d}")

    # Checkpoint URL (This is a common public link for vox-cpk.pth.tar)
    # Note: If this link expires, the user will need to update it.
    CHECKPOINT_URL = "https://github.com/AliaksandrSiarohin/first-order-model/releases/download/v1.0/vox-cpk.pth.tar"
    CHECKPOINT_PATH = "checkpoints/vox-cpk.pth.tar"
    
    # Since the file is 700MB+, we only download if missing
    if not os.path.exists(CHECKPOINT_PATH):
        print("Model checkpoint missing.")
        # Try to download if URL is provided, otherwise instruct user
        # download_file(CHECKPOINT_URL, CHECKPOINT_PATH)
        print(f"Please ensure {CHECKPOINT_PATH} is present before running the app.")
    else:
        print("Model checkpoint found.")
