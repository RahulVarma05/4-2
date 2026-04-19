"""
app.py — FOMM Motion Transfer Web App
Multi-page Flask app: Home, About, User Guide
"""
import os, sys, uuid, threading, traceback, time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, abort, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fomm_core'))

from pipeline.loader import load_checkpoints, load_source_image, load_driving_video, save_video
from pipeline.motion_transfer import make_animation
from pipeline.face_composition import face_composition

app = Flask(__name__, static_folder='web-design/dist', static_url_path='/')
app.config['SECRET_KEY'] = 'fomm-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


def _is_api_request():
    # Treat JSON requests as API-style clients expecting status codes + JSON bodies.
    if request.path.startswith('/api/') or request.path.startswith('/generate') or request.path.startswith('/status') or request.path.startswith('/download'):
        return True
    if request.is_json:
        return True
    accept = (request.headers.get('Accept') or '').lower()
    return 'application/json' in accept


def _get_credential(field_name):
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        value = payload.get(field_name)
    else:
        value = request.form.get(field_name)
    if isinstance(value, str):
        return value.strip()
    return value

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    if _is_api_request():
        return jsonify({'error': 'Authentication required.'}), 401
    return redirect('/')

def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required.'}), 401
        return f(*args, **kwargs)
    return decorated

with app.app_context():
    db.create_all()

UPLOAD_FOLDER = 'web_uploads'
RESULT_FOLDER = 'web_results'
SAMPLE_VIDEOS = {
    "1": os.path.join('samples', 'VideoProject.mp4'),
    "2": os.path.join('samples', 'driving.mp4'),
    "3": os.path.join('samples', 'driving-2.mp4'),
    "4": os.path.join('samples', 'driving-3.mp4'),
}
CONFIG_PATH   = os.path.join('fomm_core', 'config', 'vox-256.yaml')
CHECKPOINT    = os.path.join('checkpoints', 'vox-cpk.pth.tar')
MAX_SECONDS   = 5
CPU_MODE      = not __import__('torch').cuda.is_available()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

jobs = {}

JOB_TTL = 3600  # 1 hour

def cleanup_old_jobs():
    now = time.time()
    expired = [
        jid for jid, job in list(jobs.items())
        if now - job.get('created_at', now) > JOB_TTL
    ]
    for jid in expired:
        result_path = jobs[jid].get('result_path')
        if result_path and os.path.exists(result_path):
            try:
                os.remove(result_path)
            except:
                pass
        del jobs[jid]
    
    if expired:
        print(f"Cleaned up {len(expired)} expired jobs")

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
        drv, fps = load_driving_video(driving_path, max_seconds=MAX_SECONDS)
        jobs[job_id]['message'] = f'Processing {len(drv)} frames...'
        if mode == 'animate':
            preds = make_animation(src, drv, generator, kp_detector,
                                   cpu=CPU_MODE)
        else:
            preds = face_composition(src, drv, generator, kp_detector,
                                    cpu=CPU_MODE, use_color_correct=True, debug=False)
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
                if p and os.path.exists(p) and p not in SAMPLE_VIDEOS.values(): os.remove(p)
            except: pass


# UI routes removed, single page app handles UI


@app.route('/api/register', methods=['POST'])
def api_register():
    email = _get_credential('email')
    password = _get_credential('password')
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists.'}), 400
    new_user = User(email=email, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({'message': 'Registration successful.'}), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    email = _get_credential('email')
    password = _get_credential('password')
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    login_user(user)
    return jsonify({'message': 'Login successful.'}), 200


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logout successful.'}), 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    else:
        return app.send_static_file('index.html')


@app.route('/generate', methods=['POST'])
@api_login_required
def generate():
    cleanup_old_jobs()
    if not MODEL_READY: return jsonify({'error': 'Model not loaded.'}), 500
    if 'source_image' not in request.files: return jsonify({'error': 'No source image.'}), 400
    sf  = request.files['source_image']
    ext = Path(sf.filename).suffix.lower()
    if ext not in ('.jpg','.jpeg','.png','.webp'):
        return jsonify({'error': 'Unsupported image format. Use JPG, PNG, or WEBP.'}), 400
    jid = str(uuid.uuid4())
    sp  = os.path.join(UPLOAD_FOLDER, f'{jid}_source{ext}')
    sf.save(sp)
    
    use_sample = request.form.get('use_sample', '')
    
    if use_sample in SAMPLE_VIDEOS:
        dp = SAMPLE_VIDEOS[use_sample]
        if not os.path.exists(dp):
            return jsonify({'error': f'Sample video {use_sample} not found.'}), 500
    else:
        if 'driving_video' not in request.files: 
            return jsonify({'error': 'No driving video.'}), 400
        dv = request.files['driving_video']
        dp = os.path.join(UPLOAD_FOLDER, f'{jid}_driving.mp4')
        dv.save(dp)
        
    mode = request.form.get('mode', 'animate')
    if mode not in ('animate', 'face_composition'): 
        mode = 'animate'
        
    jobs[jid] = {
        'status': 'queued',
        'message': 'Queued...',
        'result_path': None,
        'created_at': time.time()
    }
    
    threading.Thread(
        target=run_pipeline,
        args=(jid, sp, dp, mode),
        daemon=True
    ).start()
    
    return jsonify({'job_id': jid})


@app.route('/status/<jid>')
@api_login_required
def status(jid):
    if jid not in jobs: return jsonify({'error':'Not found'}), 404
    j = jobs[jid]
    return jsonify({'status':j['status'],'message':j['message'],'ready':j['status']=='done'})


@app.route('/download/<jid>')
@api_login_required
def download(jid):
    if jid not in jobs: abort(404)
    j = jobs[jid]
    if j['status']!='done' or not j['result_path']: abort(404)
    return send_file(
        j['result_path'],
        mimetype='video/mp4',
        as_attachment=True,
        download_name='motion_mimic.mp4'
    )

@app.route('/samples/<path:filename>')
def serve_sample(filename):
    sample_path = os.path.join('samples', filename)
    if not os.path.exists(sample_path):
        abort(404)
    return send_file(sample_path)

@app.route('/sample-video/<int:sample_id>')
def sample_video(sample_id):
    key = str(sample_id)
    if key not in SAMPLE_VIDEOS:
        abort(404)
    path = SAMPLE_VIDEOS[key]
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype='video/mp4')

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
