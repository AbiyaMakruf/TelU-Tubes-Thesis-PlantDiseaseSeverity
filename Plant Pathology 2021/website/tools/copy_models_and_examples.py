"""Utility to copy models and example prediction images into website folders.

This script copies:
1) Object detection models from results/object_detection/training/{nano,small,medium}/weights/best.pt
   -> website/models/object_detection/{nano,best.pt}
2) Segmentation models from results/mask_lesi_and_leaf/training/{nano,small,medium}/weights/best.pt
   -> website/models/segmentation/{nano,best.pt}
3) Example prediction images: take 3 random images per {nano,small,medium} from
   Plant Pathology 2021/results/object_detection/predict/{nano,small,medium}/ -> website/static/examples/object_detection/{size}/
4) Copy severity example overlays if available (from results/severity_estimation/*)

Run this script from repository root (python website/tools/copy_models_and_examples.py)
"""
import os
import shutil
import random

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# The repository has a top-level folder named 'Plant Pathology 2021' under ROOT.
# If this script runs from website/tools, ROOT points to repo root; set SRC accordingly.
SRC = os.path.join(ROOT, 'Plant Pathology 2021')
if os.path.basename(ROOT).lower().startswith('plant pathology'):
    # If ROOT already is the 'Plant Pathology 2021' folder, avoid duplicating it
    SRC = ROOT
# paths inside repo
OBJ_MODEL_SRC = os.path.join(SRC, 'results', 'object_detection', 'training')
SEG_MODEL_SRC = os.path.join(SRC, 'results', 'mask_lesi_and_leaf', 'training')
PREDICT_SRC = os.path.join(SRC, 'results', 'object_detection', 'predict')
SEV_SRC = os.path.join(SRC, 'results', 'severity_estimation')

DST_MODELS_OBJ = os.path.join(ROOT, 'website', 'models', 'object_detection')
DST_MODELS_SEG = os.path.join(ROOT, 'website', 'models', 'segmentation')
DST_EXAMPLES_OD = os.path.join(ROOT, 'website', 'static', 'examples', 'object_detection')
DST_EXAMPLES_SEV = os.path.join(ROOT, 'website', 'static', 'examples', 'severity')

os.makedirs(DST_MODELS_OBJ, exist_ok=True)
os.makedirs(DST_MODELS_SEG, exist_ok=True)
os.makedirs(DST_EXAMPLES_OD, exist_ok=True)
os.makedirs(DST_EXAMPLES_SEV, exist_ok=True)

sizes = ['nano', 'small', 'medium']

# 1) copy models (object detection)
for s in sizes:
    src_weights = os.path.join(OBJ_MODEL_SRC, s, 'weights', 'best.pt')
    if os.path.exists(src_weights):
        dst_dir = os.path.join(DST_MODELS_OBJ, s)
        os.makedirs(dst_dir, exist_ok=True)
        dst_path = os.path.join(dst_dir, 'best.pt')
        shutil.copy2(src_weights, dst_path)
        print(f'Copied OD model: {src_weights} -> {dst_path}')
    else:
        print(f'OD model not found for {s}: {src_weights}')

# 2) copy segmentation models
for s in sizes:
    src_weights = os.path.join(SEG_MODEL_SRC, s, 'weights', 'best.pt')
    if os.path.exists(src_weights):
        dst_dir = os.path.join(DST_MODELS_SEG, s)
        os.makedirs(dst_dir, exist_ok=True)
        dst_path = os.path.join(dst_dir, 'best.pt')
        shutil.copy2(src_weights, dst_path)
        print(f'Copied SEG model: {src_weights} -> {dst_path}')
    else:
        print(f'SEG model not found for {s}: {src_weights}')

# 3) copy 3 random prediction images per size
for s in sizes:
    src_pred_dir = os.path.join(PREDICT_SRC, s)
    dst_dir = os.path.join(DST_EXAMPLES_OD, s)
    os.makedirs(dst_dir, exist_ok=True)
    if os.path.exists(src_pred_dir):
        imgs = [f for f in os.listdir(src_pred_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not imgs:
            print(f'No prediction images found for {s} in {src_pred_dir}')
            continue
        sel = random.sample(imgs, min(3, len(imgs)))
        for im in sel:
            shutil.copy2(os.path.join(src_pred_dir, im), os.path.join(dst_dir, im))
        print(f'Copied {len(sel)} example images for {s} to {dst_dir}')
    else:
        print(f'Prediction folder not found for {s}: {src_pred_dir}')

# 4) copy severity overlays (if any)
if os.path.exists(SEV_SRC):
    # copy all jpg/png from the severity results folder recursively
    for root, _, files in os.walk(SEV_SRC):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                srcf = os.path.join(root, f)
                dstf = os.path.join(DST_EXAMPLES_SEV, f)
                shutil.copy2(srcf, dstf)
    print('Copied severity example images if any.')
else:
    print('No severity_estimation results folder found; skipping severity copy')

print('Done.')
