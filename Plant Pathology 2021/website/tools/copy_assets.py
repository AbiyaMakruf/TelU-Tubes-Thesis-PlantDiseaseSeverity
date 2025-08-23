import os
import glob
import random
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def copy_samples():
    src_base = os.path.join(ROOT, 'dataset', 'object_detection')
    dst_base = os.path.join(ROOT, 'website', 'static', 'dataset_samples')
    os.makedirs(dst_base, exist_ok=True)
    for subset in ('train', 'valid', 'test'):
        src = os.path.join(src_base, subset, 'images')
        dst = os.path.join(dst_base, subset)
        os.makedirs(dst, exist_ok=True)
        if os.path.exists(src):
            files = [f for f in os.listdir(src) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            # pick up to 6 examples
            pick = files[:6]
            for f in pick:
                shutil.copy(os.path.join(src, f), os.path.join(dst, f))

def copy_graphs():
    dst = os.path.join(ROOT, 'website', 'static', 'graphs')
    os.makedirs(dst, exist_ok=True)
    # object_detection graphs
    od_src = os.path.join(ROOT, 'results', 'object_detection', 'graph')
    if os.path.exists(od_src):
        for p in glob.glob(os.path.join(od_src, '*.png')):
            shutil.copy(p, os.path.join(dst, os.path.basename(p)))
    # mask_lesi_and_leaf graphs
    seg_src = os.path.join(ROOT, 'results', 'mask_lesi_and_leaf', 'graph')
    if os.path.exists(seg_src):
        for p in glob.glob(os.path.join(seg_src, '*.png')):
            shutil.copy(p, os.path.join(dst, os.path.basename(p)))

if __name__ == '__main__':
    copy_samples()
    copy_graphs()
    print('Assets copied to website/static (dataset_samples, graphs)')
