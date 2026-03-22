"""
app.py — FOMM Motion Transfer Web App
Multi-page Flask app: Home, About, User Guide
"""
import os, sys, uuid, threading, traceback
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, abort

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fomm_core'))

from pipeline.loader import load_checkpoints, load_source_image, load_driving_video, save_video
from pipeline.motion_transfer import make_animation, motion_transfer

app = Flask(__name__)

UPLOAD_FOLDER = 'web_uploads'
RESULT_FOLDER = 'web_results'
SAMPLE_VIDEO  = os.path.join('samples', 'driving.mp4')
CONFIG_PATH   = os.path.join('fomm_core', 'config', 'vox-256.yaml')
CHECKPOINT    = os.path.join('checkpoints', 'vox-cpk.pth.tar')
MAX_FRAMES    = 60
CPU_MODE      = not __import__('torch').cuda.is_available()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

jobs = {}

print("\nLoading FOMM model...")
try:
    generator, kp_detector = load_checkpoints(CONFIG_PATH, CHECKPOINT, cpu=CPU_MODE)
    print(f"  Model ready  (CPU={CPU_MODE})")
    MODEL_READY = True
except Exception as e:
    print(f"  ERROR: {e}")
    MODEL_READY = False


def run_pipeline(job_id, source_path, driving_path, mode):
    jobs[job_id].update({'status': 'processing', 'message': 'Loading inputs...'})
    try:
        src  = load_source_image(source_path)
        drv, fps = load_driving_video(driving_path, max_frames=MAX_FRAMES)
        jobs[job_id]['message'] = f'Processing {len(drv)} frames...'
        preds = make_animation(src, drv, generator, kp_detector, relative=True, adapt_scale=True, cpu=CPU_MODE) \
                if mode == 'animate' else \
                motion_transfer(src, drv, generator, kp_detector, cpu=CPU_MODE, use_color_correct=True, debug=False)
        out = os.path.join(RESULT_FOLDER, f'{job_id}.mp4')
        jobs[job_id]['message'] = 'Saving...'
        save_video(preds, out, fps)
        jobs[job_id].update({'status': 'done', 'message': 'Complete!', 'result_path': out})
    except Exception as e:
        jobs[job_id].update({'status': 'error', 'message': str(e)})
        traceback.print_exc()
    finally:
        for p in [source_path, driving_path]:
            try:
                if p and os.path.exists(p) and p != SAMPLE_VIDEO: os.remove(p)
            except: pass


@app.route('/')
def index():  return render_template('index.html',  model_ready=MODEL_READY, active='home')

@app.route('/about')
def about():  return render_template('about.html',  active='about')

@app.route('/guide')
def guide():  return render_template('guide.html',  active='guide')


@app.route('/generate', methods=['POST'])
def generate():
    if not MODEL_READY: return jsonify({'error': 'Model not loaded.'}), 500
    if 'source_image' not in request.files: return jsonify({'error': 'No source image.'}), 400
    sf  = request.files['source_image']
    ext = Path(sf.filename).suffix.lower()
    if ext not in ('.jpg','.jpeg','.png','.webp'): return jsonify({'error': 'Image must be JPG/PNG/WEBP.'}), 400
    jid = str(uuid.uuid4())
    sp  = os.path.join(UPLOAD_FOLDER, f'{jid}_source{ext}')
    sf.save(sp)
    use_sample = request.form.get('use_sample','false').lower()=='true'
    if use_sample:
        dp = SAMPLE_VIDEO
        if not os.path.exists(dp): return jsonify({'error': 'Sample video missing.'}), 500
    else:
        if 'driving_video' not in request.files: return jsonify({'error': 'No driving video.'}), 400
        dv = request.files['driving_video']
        dp = os.path.join(UPLOAD_FOLDER, f'{jid}_driving.mp4')
        dv.save(dp)
    mode = request.form.get('mode','animate')
    if mode not in ('animate','motion_transfer'): mode='animate'
    jobs[jid] = {'status':'queued','message':'Queued...','result_path':None}
    threading.Thread(target=run_pipeline, args=(jid,sp,dp,mode), daemon=True).start()
    return jsonify({'job_id': jid})


@app.route('/status/<jid>')
def status(jid):
    if jid not in jobs: return jsonify({'error':'Not found'}), 404
    j = jobs[jid]
    return jsonify({'status':j['status'],'message':j['message'],'ready':j['status']=='done'})


@app.route('/download/<jid>')
def download(jid):
    if jid not in jobs: abort(404)
    j = jobs[jid]
    if j['status']!='done' or not j['result_path']: abort(404)
    return send_file(j['result_path'], mimetype='video/mp4', as_attachment=True,
                     download_name='motion_transfer_result.mp4')

@app.route('/sample-video')
def sample_video():
    if not os.path.exists(SAMPLE_VIDEO): abort(404)
    return send_file(SAMPLE_VIDEO, mimetype='video/mp4')

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
