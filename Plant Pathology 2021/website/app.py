import os
import glob
import traceback
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results_predict'
MODELS_FOLDER = os.path.join('models', 'object_detection')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.secret_key = 'change-me'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Simple in-memory model cache to avoid re-loading models each request
MODEL_CACHE = {
    'detection': {},
    'segmentation': {}
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def model_label(path: str) -> str:
    try:
        parts = os.path.normpath(path).split(os.sep)
        if 'object_detection' in parts:
            i = parts.index('object_detection')
            if i + 1 < len(parts):
                return parts[i + 1]
        if 'segmentation' in parts:
            i = parts.index('segmentation')
            if i + 1 < len(parts):
                return parts[i + 1]
        parent = os.path.basename(os.path.dirname(path))
        if parent:
            return parent
        return os.path.splitext(os.path.basename(path))[0]
    except Exception:
        return os.path.splitext(os.path.basename(path))[0]


def find_model():
    pats = ['**/*.pt', '**/*.pth']
    models = []
    for p in pats:
        models += glob.glob(os.path.join(MODELS_FOLDER, p), recursive=True)
    return sorted(models)


@app.route('/')
def home():
    models = find_model()
    models = [(m, model_label(m)) for m in models]
    return render_template('landing.html', models=models)


@app.route('/dashboard')
def dashboard():
    examples = {'nano': [], 'small': [], 'medium': []}
    base = os.path.join('static', 'examples', 'object_detection')
    for size in examples.keys():
        folder = os.path.join(base, size)
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            examples[size] = sorted(files)[:3]
    models = find_model()
    models = [(m, model_label(m)) for m in models]
    return render_template('dashboard.html', examples=examples, models=models)


@app.route('/dataset')
def dataset():
    samples = {}
    base = os.path.join('static', 'dataset_samples')
    full_lists = {}
    for subset in ('train', 'valid', 'test'):
        folder = os.path.join(base, subset)
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            files_sorted = sorted(files)
            samples[subset] = files_sorted[:6]
            full_lists[subset] = files_sorted
        else:
            samples[subset] = []
            full_lists[subset] = []

    def infer_class(name):
        lname = name.lower()
        if 'frog' in lname:
            return 'frog-eye-leaf-spot'
        if 'rust' in lname:
            return 'rust'
        if 'healthy' in lname:
            return 'healthy'
        return 'unknown'

    classes = {}
    for subset, fl in full_lists.items():
        classes[subset] = {f: infer_class(f) for f in fl}

    return render_template('dataset.html', samples=samples, full_lists=full_lists, classes=classes)


@app.route('/project')
def project():
    graphs_dir = os.path.join('static', 'graphs')
    graphs = []
    if os.path.exists(graphs_dir):
        graphs = [f for f in os.listdir(graphs_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return render_template('project.html', graphs=sorted(graphs))


@app.route('/severity')
def severity():
    sev_dir = os.path.join('static', 'examples', 'severity')
    files = []
    if os.path.exists(sev_dir):
        files = [f for f in os.listdir(sev_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    return render_template('severity.html', files=sorted(files))


@app.route('/upload')
def upload():
    det_models = []
    seg_models = []
    for root, _, files in os.walk(os.path.join('models', 'object_detection')):
        for f in files:
            if f.endswith(('.pt', '.pth')):
                full = os.path.join(root, f)
                det_models.append((full, model_label(full)))
    for root, _, files in os.walk(os.path.join('models', 'segmentation')):
        for f in files:
            if f.endswith(('.pt', '.pth')):
                full = os.path.join(root, f)
                seg_models.append((full, model_label(full)))

    last = {
        'task': session.get('last_task', 'detection'),
        'det_model': session.get('last_det_model', ''),
        'seg_model': session.get('last_seg_model', ''),
        'pad': session.get('last_pad', 10),
        'multi_leaf': session.get('last_multi_leaf', '')
    }
    last_uploaded = session.get('last_uploaded', '')
    uploaded_rel = os.path.join('uploads', last_uploaded) if last_uploaded else ''
    uploaded_basename = last_uploaded
    uploaded = uploaded_rel
    return render_template('upload.html', det_models=det_models, seg_models=seg_models, last=last, uploaded_rel=uploaded_rel, uploaded_basename=uploaded_basename, uploaded=uploaded)


@app.route('/predict', methods=['POST'])
def predict():
    # Prefer uploaded file, otherwise existing_file form field or session fallback
    if 'file' in request.files and request.files['file'].filename:
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('upload'))
        if not (file and allowed_file(file.filename)):
            flash('Invalid file type')
            return redirect(url_for('upload'))
        filename = secure_filename(file.filename)
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(in_path)
        try:
            session['last_uploaded'] = filename
        except Exception:
            pass
        print(f"[PREDICT] Saved uploaded file to: {in_path}")
    else:
        existing = request.form.get('existing_file')
        if not existing:
            flash('No file part')
            return redirect(url_for('upload'))
        filename = secure_filename(os.path.basename(existing))
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(in_path):
            try:
                uploads_list = os.listdir(app.config['UPLOAD_FOLDER'])
            except Exception:
                uploads_list = []
            print(f"[PREDICT] existing_field='{existing}' basename='{filename}' in_path='{in_path}' uploads_list={uploads_list} session_last_uploaded={session.get('last_uploaded')}")
            match = None
            for c in uploads_list:
                if c == filename or c.endswith(filename) or filename in c:
                    match = c
                    break
            if match:
                print(f"[PREDICT] Flexible match found: {match}")
                filename = match
                in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            else:
                fallback = session.get('last_uploaded')
                if fallback and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], fallback)):
                    print(f"[PREDICT] Using session fallback last_uploaded={fallback}")
                    filename = fallback
                    in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                else:
                    print(f"[PREDICT] No match/fallback found; will request re-upload")
                    flash('Requested existing uploaded file not found on server. Please re-upload.')
                    return redirect(url_for('upload'))
        try:
            session['last_uploaded'] = filename
        except Exception:
            pass

    task = request.form.get('task', 'detection')
    det_model = request.form.get('det_model')
    seg_model = request.form.get('seg_model')
    pad = int(request.form.get('pad', 10)) if request.form.get('pad') else 10
    multi_leaf = True if request.form.get('multi_leaf') == 'on' else False

    try:
        from ultralytics import YOLO
        import numpy as np
        from PIL import Image
    except Exception:
        flash("Package 'ultralytics' (and dependencies) required. Install with: pip install ultralytics")
        return redirect(url_for('upload'))

    result_data = {}

    try:
        # Detection task
        if task == 'detection':
            if not det_model:
                models = find_model()
                det_model = models[0] if models else None
            if not det_model:
                flash('No detection model available')
                return redirect(url_for('upload'))
            if det_model in MODEL_CACHE['detection']:
                model = MODEL_CACHE['detection'][det_model]
            else:
                model = YOLO(det_model)
                MODEL_CACHE['detection'][det_model] = model
            res = model.predict(source=in_path, conf=0.25, imgsz=640)
            if not res:
                flash('Model returned no results')
                return redirect(url_for('upload'))
            r = res[0]
            ann = r.plot()
            try:
                import numpy as _np
                if ann.shape[2] == 3:
                    ann_rgb = _np.stack([ann[:, :, 2], ann[:, :, 1], ann[:, :, 0]], axis=2)
                else:
                    ann_rgb = ann
            except Exception:
                ann_rgb = ann
            img_out = Image.fromarray(ann_rgb.astype('uint8'))
            out_name = f"annotated_{filename}"
            out_path = os.path.join(app.config['RESULTS_FOLDER'], out_name)
            img_out.save(out_path)
            preds = []
            try:
                boxes = r.boxes.xyxy.cpu().numpy()
                cls = r.boxes.cls.cpu().numpy().astype(int)
                for c in cls:
                    preds.append(int(c))
            except Exception:
                pass
            result_data.update({'annotated': out_name, 'pred_classes': preds, 'task': 'detection'})

        # Segmentation task
        elif task == 'segmentation':
            if not seg_model:
                flash('No segmentation model selected')
                return redirect(url_for('upload'))
            if seg_model in MODEL_CACHE['segmentation']:
                model = MODEL_CACHE['segmentation'][seg_model]
            else:
                model = YOLO(seg_model)
                MODEL_CACHE['segmentation'][seg_model] = model
            res = model.predict(source=in_path, conf=0.25, imgsz=640)
            if not res:
                flash('Segmentation model returned no results')
                return redirect(url_for('upload'))
            r = res[0]
            ann = r.plot()
            try:
                import numpy as _np
                if ann.shape[2] == 3:
                    ann_rgb = _np.stack([ann[:, :, 2], ann[:, :, 1], ann[:, :, 0]], axis=2)
                else:
                    ann_rgb = ann
            except Exception:
                ann_rgb = ann
            img_out = Image.fromarray(ann_rgb.astype('uint8'))
            out_name = f"seg_annotated_{filename}"
            out_path = os.path.join(app.config['RESULTS_FOLDER'], out_name)
            img_out.save(out_path)
            result_data.update({'annotated': out_name, 'task': 'segmentation'})

        # Severity task
        elif task == 'severity':
            if not det_model:
                models = find_model()
                det_model = models[0] if models else None
            if not det_model or not seg_model:
                flash('Both detection and segmentation models are required for severity estimation')
                return redirect(url_for('upload'))
            if det_model in MODEL_CACHE['detection']:
                model_det = MODEL_CACHE['detection'][det_model]
            else:
                model_det = YOLO(det_model)
                MODEL_CACHE['detection'][det_model] = model_det
            det_res = model_det.predict(source=in_path, conf=0.25, imgsz=640)
            if not det_res:
                flash('Detection returned no results')
                return redirect(url_for('upload'))
            det_r = det_res[0]
            try:
                boxes = det_r.boxes.xyxy.cpu().numpy()
                dcls = det_r.boxes.cls.cpu().numpy().astype(int)
            except Exception:
                flash('Unable to extract detection boxes')
                return redirect(url_for('upload'))
            if len(boxes) == 0:
                flash('No detection boxes found')
                return redirect(url_for('upload'))
            idxs = list(range(len(boxes))) if multi_leaf else [int(np.argmax((boxes[:,2]-boxes[:,0]) * (boxes[:,3]-boxes[:,1])))]
            from PIL import ImageDraw
            img = Image.open(in_path).convert('RGB')
            W, H = img.size
            crop_overlays = []
            if seg_model in MODEL_CACHE['segmentation']:
                model_seg = MODEL_CACHE['segmentation'][seg_model]
            else:
                model_seg = YOLO(seg_model)
                MODEL_CACHE['segmentation'][seg_model] = model_seg
            for i_idx in idxs:
                x1, y1, x2, y2 = boxes[i_idx].astype(int)
                x1p = max(0, x1 - pad)
                y1p = max(0, y1 - pad)
                x2p = min(W, x2 + pad)
                y2p = min(H, y2 + pad)
                crop = img.crop((x1p, y1p, x2p, y2p))
                crop_path = os.path.join(app.config['UPLOAD_FOLDER'], f"crop_{i_idx}_{filename}")
                crop.save(crop_path)
                seg_res = model_seg.predict(source=crop_path, conf=0.25, imgsz=640)
                if not seg_res:
                    continue
                seg_r = seg_res[0]
                try:
                    masks = (seg_r.masks.data.cpu().numpy() > 0.5)
                    scls = seg_r.boxes.cls.cpu().numpy().astype(int)
                except Exception:
                    continue
                SEG_LEAF_IDS = [0, 2, 3]
                PAIR_LESION_ID = {0:1, 3:4}
                leaf_idxs = [j for j, c in enumerate(scls) if int(c) in SEG_LEAF_IDS]
                if not leaf_idxs:
                    continue
                import numpy as _np
                combined_leaf = None
                for j in leaf_idxs:
                    if combined_leaf is None:
                        combined_leaf = masks[j].copy()
                    else:
                        combined_leaf = combined_leaf | masks[j]
                if combined_leaf is None:
                    continue
                lesion_idxs_all = []
                for j in leaf_idxs:
                    leaf_class = int(scls[j])
                    if leaf_class in PAIR_LESION_ID:
                        lesion_id = PAIR_LESION_ID[leaf_class]
                        lesion_idxs_all += [k for k, c in enumerate(scls) if int(c) == lesion_id]
                combined_lesion = np.zeros_like(combined_leaf, dtype=bool)
                if lesion_idxs_all:
                    combined_lesion = np.any([masks[k] for k in lesion_idxs_all], axis=0)
                lesion_in_leaf = combined_lesion & combined_leaf
                leaf_px = int(combined_leaf.sum())
                lesion_px = int(lesion_in_leaf.sum())
                severity_pct = round(float((lesion_px / leaf_px * 100.0) if leaf_px > 0 else 0.0), 2)
                crop_arr = _np.array(crop)
                Hc, Wc = crop_arr.shape[:2]
                leaf_up = _np.array(Image.fromarray(combined_leaf.astype('uint8')*255).resize((Wc,Hc))).astype(bool)
                lesion_up = _np.array(Image.fromarray(combined_lesion.astype('uint8')*255).resize((Wc,Hc))).astype(bool)
                lesion_in_leaf_up = lesion_up & leaf_up
                overlay = crop_arr.copy()
                overlay[leaf_up] = (0.7*overlay[leaf_up] + 0.3*_np.array([0,255,0])).astype(_np.uint8)
                overlay[lesion_in_leaf_up] = _np.array([139,0,0], dtype=_np.uint8)
                out_name = f"severity_crop_{i_idx}_{filename}"
                out_path = os.path.join(app.config['RESULTS_FOLDER'], out_name)
                Image.fromarray(overlay).save(out_path)
                crop_overlays.append({'filename': out_name, 'severity': severity_pct, 'leaf_px': leaf_px, 'lesion_px': lesion_px})
            try:
                det_ann = det_r.plot()
                import numpy as _np
                if det_ann.shape[2] == 3:
                    det_ann_rgb = _np.stack([det_ann[:, :, 2], det_ann[:, :, 1], det_ann[:, :, 0]], axis=2)
                else:
                    det_ann_rgb = det_ann
                det_out = Image.fromarray(det_ann_rgb.astype('uint8'))
                det_name = f"det_annotated_{filename}"
                det_path = os.path.join(app.config['RESULTS_FOLDER'], det_name)
                det_out.save(det_path)
            except Exception:
                det_name = None
            result_data.update({'task': 'severity', 'crop_overlays': crop_overlays, 'detection_annotated': det_name})

        else:
            flash('Unknown task')
            return redirect(url_for('upload'))

    except Exception as e:
        print('[PREDICT] Exception during prediction:')
        traceback.print_exc()
        flash(f'Error during prediction: {e}')
        return redirect(url_for('upload'))

    # prepare model lists again
    det_models = []
    seg_models = []
    for root, _, files in os.walk(os.path.join('models', 'object_detection')):
        for f in files:
            if f.endswith(('.pt', '.pth')):
                full = os.path.join(root, f)
                det_models.append((full, model_label(full)))
    for root, _, files in os.walk(os.path.join('models', 'segmentation')):
        for f in files:
            if f.endswith(('.pt', '.pth')):
                full = os.path.join(root, f)
                seg_models.append((full, model_label(full)))

    uploaded_rel = os.path.join('uploads', filename)
    try:
        session['last_task'] = task
        session['last_det_model'] = det_model if det_model else ''
        session['last_seg_model'] = seg_model if seg_model else ''
        session['last_pad'] = int(pad)
        session['last_multi_leaf'] = 'on' if multi_leaf else ''
    except Exception:
        pass
    return render_template('upload.html', det_models=det_models, seg_models=seg_models, uploaded=uploaded_rel, result=result_data)


@app.route('/results')
def results():
    files = sorted(os.listdir(app.config['RESULTS_FOLDER']))
    return render_template('results.html', files=files)


@app.route('/results/<path:filename>')
def result(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
