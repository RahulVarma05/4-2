# FOMM Motion Transfer

AI-powered face animation using First Order Motion Model (NeurIPS 2019).
Upload a portrait photo and a driving video — the AI transfers head motion,
facial expressions and lip movements onto your static image.

## Setup

**Step 1 — Clone this repo**
```
git clone https://github.com/RahulVarma05/4-2.git
cd 4-2
```

**Step 2 — Clone FOMM core (read-only dependency)**
```
git clone https://github.com/AliaksandrSiarohin/first-order-model fomm_core
```

**Step 3 — Create conda environment**
```
conda create -n fomm python=3.8 -y
conda activate fomm
```

**Step 4 — Install dependencies**
```
pip install -r requirements.txt
pip install -r requirements_web.txt
pip install opencv-python==4.7.0.72
```

**Step 5 — Download checkpoint**
```
python prepare_demo.py
```

**Step 6 — Add your driving video**
Place a close-up face video at `samples/driving.mp4`

**Step 7 — Run the web app**
```
python app.py
```
Open `http://localhost:5000`

## Pages

- **Home** — upload source image and driving video, generate animation
- **About** — project background and full pipeline architecture
- **User Guide** — input requirements, examples, troubleshooting

## Command line usage
```
python main.py --mode animate --max_frames 30 --cpu
python main.py --mode motion_transfer --find_best_frame --cpu
```

## Research

Based on: First Order Motion Model for Image Animation
Siarohin et al., NeurIPS 2019
https://papers.nips.cc/paper/8935-first-order-motion-model-for-image-animation
```

