"""
view.py

2x2 comparison viewer for images with identical filenames.

Panels:
  TL: original image with YOLO-format labels drawn (labels from dataset/object_detection/train/labels)
  TR: prediction image from results/object_detection/predict/nano/
  BL: prediction image from results/object_detection/predict/small/
  BR: prediction image from results/object_detection/predict/medium/

Controls:
  Right arrow / n / d  -> next image
  Left arrow  / p / a  -> previous image
  q                   -> quit

Usage (from repo root):
  python view.py

You can override directories via command-line arguments. Designed for Windows (cmd.exe) but portable.
"""

import os
import cv2
import numpy as np
import argparse
import re


def draw_yolo_boxes(img, label_path, class_names=None, color=(0, 200, 0), thickness=2):
    """Draw YOLO-format boxes (class x_center y_center w h normalized) onto a copy of img.
    class_names: optional list mapping class index -> name. If provided, label text will use name.
    Returns the annotated copy. If label file missing, returns original copy.
    """
    out = img.copy()
    h, w = out.shape[:2]
    # dynamic font scale/thickness based on image height
    font_scale = max(0.4, min(2.0, h / 600.0))
    t_thickness = max(1, int(thickness * (h / 400.0)))

    if not os.path.exists(label_path):
        return out
    try:
        with open(label_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue
                cls = parts[0]
                try:
                    x_c = float(parts[1]) * w
                    y_c = float(parts[2]) * h
                    bw = float(parts[3]) * w
                    bh = float(parts[4]) * h
                except Exception:
                    continue
                x1 = int(max(0, x_c - bw / 2))
                y1 = int(max(0, y_c - bh / 2))
                x2 = int(min(w - 1, x_c + bw / 2))
                y2 = int(min(h - 1, y_c + bh / 2))
                cv2.rectangle(out, (x1, y1), (x2, y2), color, t_thickness)
                # map class index to name if provided
                lbl = str(cls)
                try:
                    idx = int(float(cls))
                    if class_names and 0 <= idx < len(class_names):
                        lbl = class_names[idx]
                except Exception:
                    pass
                (tw, th), _ = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, font_scale, t_thickness)
                # draw filled rectangle for label background
                y_top = max(0, y1 - th - 8)
                cv2.rectangle(out, (x1, y_top), (x1 + tw + 8, y1), color, -1)
                cv2.putText(out, lbl, (x1 + 4, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), t_thickness, cv2.LINE_AA)
    except Exception as e:
        print(f"[draw_yolo_boxes] error reading {label_path}: {e}")
    return out


def load_or_placeholder(path, target_size=None, text=None):
    if path and os.path.exists(path):
        im = cv2.imread(path)
        if im is None:
            im = np.zeros((256, 256, 3), dtype=np.uint8)
            cv2.putText(im, 'UNREADABLE', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    else:
        im = np.zeros((256, 256, 3), dtype=np.uint8)
        if text:
            cv2.putText(im, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    if target_size is not None:
        im = cv2.resize(im, target_size)
    return im


def make_grid(im_tl, im_tr, im_bl, im_br):
    # Resize others to match top-left
    th, tw = im_tl.shape[:2]
    im_tr_r = cv2.resize(im_tr, (tw, th))
    im_bl_r = cv2.resize(im_bl, (tw, th))
    im_br_r = cv2.resize(im_br, (tw, th))
    top = np.hstack([im_tl, im_tr_r])
    bottom = np.hstack([im_bl_r, im_br_r])
    grid = np.vstack([top, bottom])
    return grid


def gather_files(orig_dir):
    files = [f for f in os.listdir(orig_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    files.sort()
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--orig_dir', default=os.path.join('dataset', 'object_detection', 'test', 'images'))
    parser.add_argument('--labels_dir', default=os.path.join('dataset', 'object_detection', 'test', 'labels'))
    parser.add_argument('--pred_root', default=os.path.join('results', 'object_detection', 'predict'))
    parser.add_argument('--sort', choices=['name', 'size'], default='name', help='sorting method for files: name (natural) or size')
    parser.add_argument('--start', type=int, default=0, help='start index (0-based)')
    args = parser.parse_args()

    pred_folders = {
        'nano': os.path.join(args.pred_root, 'nano'),
        'small': os.path.join(args.pred_root, 'small'),
        'medium': os.path.join(args.pred_root, 'medium')
    }

    if not os.path.exists(args.orig_dir):
        raise SystemExit(f'Original images folder not found: {args.orig_dir}')
    files = gather_files(args.orig_dir)
    # sorting: default is natural name order; optional size sort
    def natural_key(s):
        # split numeric parts so '10' > '2'
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    if args.sort == 'size':
        files_with_size = []
        for f in files:
            p = os.path.join(args.orig_dir, f)
            try:
                sz = os.path.getsize(p)
            except Exception:
                sz = 0
            files_with_size.append((f, sz))
        files_with_size.sort(key=lambda x: x[1])
        files = [t[0] for t in files_with_size]
    else:
        files.sort(key=natural_key)
    if not files:
        raise SystemExit(f'No images found in {args.orig_dir}')

    idx = max(0, min(args.start, len(files) - 1))
    print(f'Found {len(files)} images. Controls: right/n/d -> next, left/p/a -> prev, q -> quit')

    window_name = '4-way viewer'
    # create window once and set fullscreen
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    try:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    except Exception:
        # Some OpenCV builds/platforms may not support fullscreen property; continue gracefully
        pass

    while True:
        fname = files[idx]
        orig_path = os.path.join(args.orig_dir, fname)
        label_name = os.path.splitext(fname)[0] + '.txt'
        label_path = os.path.join(args.labels_dir, label_name)

        orig_img = cv2.imread(orig_path)
        if orig_img is None:
            orig_img = np.zeros((512, 512, 3), dtype=np.uint8)
            cv2.putText(orig_img, 'UNREADABLE ORIGINAL', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        orig_annot = draw_yolo_boxes(orig_img, label_path, color=(0, 200, 0), thickness=2)

        nano_path = os.path.join(pred_folders['nano'], fname)
        small_path = os.path.join(pred_folders['small'], fname)
        medium_path = os.path.join(pred_folders['medium'], fname)

        target_size = (orig_annot.shape[1], orig_annot.shape[0])
        im_nano = load_or_placeholder(nano_path, target_size=target_size, text='MISSING nano')
        im_small = load_or_placeholder(small_path, target_size=target_size, text='MISSING small')
        im_medium = load_or_placeholder(medium_path, target_size=target_size, text='MISSING medium')

        # Helper to draw small footer label at bottom-right of an image
        def add_footer_text(img, text, pad=6, bg_color=(0, 0, 0), alpha=0.6):
            out = img.copy()
            h, w = out.shape[:2]
            # dynamic font scale
            font_scale = max(5, min(1.2, h / 800.0))
            t_thickness = max(1, int(h / 500.0))
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, t_thickness)
            x1 = w - tw - pad - 6
            y1 = h - th - pad - 6
            x2 = w - pad
            y2 = h - pad
            # draw semi-transparent rectangle
            overlay = out.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
            cv2.addWeighted(overlay, alpha, out, 1 - alpha, 0, out)
            # put text in white
            cv2.putText(out, text, (x1 + 4, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), t_thickness, cv2.LINE_AA)
            return out

        # annotate each panel with its source folder
        # orig_label = f'orig: {os.path.relpath(args.orig_dir)}'
        # nano_label = f'nano: {os.path.relpath(pred_folders["nano"]) }'
        # small_label = f'small: {os.path.relpath(pred_folders["small"]) }'
        # medium_label = f'medium: {os.path.relpath(pred_folders["medium"]) }'

        orig_label = f'original'
        nano_label = f'nano'
        small_label = f'small'
        medium_label = f'medium'

        # load class names from data.yaml (if available) to map class indices -> names
        def load_class_names(yaml_path=os.path.join('dataset', 'object_detection', 'data.yaml')):
            names = None
            # try to use pyyaml if available
            try:
                import yaml
                if os.path.exists(yaml_path):
                    with open(yaml_path, 'r') as fh:
                        doc = yaml.safe_load(fh)
                        if isinstance(doc, dict) and 'names' in doc:
                            names = doc['names']
            except Exception:
                # fallback to manual parse
                try:
                    if os.path.exists(yaml_path):
                        with open(yaml_path, 'r') as fh:
                            lines = fh.readlines()
                        for i, L in enumerate(lines):
                            if L.strip().startswith('names:'):
                                # attempt to process next lines if list
                                rest = ''.join(lines[i:])
                                # naive attempt: find '[' and ']' inline
                                if '[' in rest and ']' in rest:
                                    s = rest[rest.index('['):rest.index(']') + 1]
                                    import ast
                                    try:
                                        names = ast.literal_eval(s)
                                    except Exception:
                                        names = None
                                break
                except Exception:
                    names = None
            return names

        class_names = load_class_names()
        # if class_names is None, proceed with indices
        orig_annot = add_footer_text(orig_annot, orig_label)
        im_nano = add_footer_text(im_nano, nano_label)
        im_small = add_footer_text(im_small, small_label)
        im_medium = add_footer_text(im_medium, medium_label)

        # try to find label file in several likely label folders if not present
        def find_label_file(label_basename):
            candidates = [label_path,  # current constructed path
                          os.path.join('dataset', 'object_detection', 'test', 'labels', label_basename),
                          os.path.join('dataset', 'object_detection', 'train', 'labels', label_basename),
                          os.path.join('dataset', 'object_detection', 'labels', label_basename)]
            for c in candidates:
                if os.path.exists(c):
                    return c
            # fallback: search any labels folder under dataset/object_detection
            root = os.path.join('dataset', 'object_detection')
            for dirpath, dirnames, filenames in os.walk(root):
                if os.path.basename(dirpath).lower() == 'labels':
                    cand = os.path.join(dirpath, label_basename)
                    if os.path.exists(cand):
                        return cand
            return label_path

        # redraw boxes on orig_annot using possibly better-found label file and class names
        label_basename = os.path.splitext(fname)[0] + '.txt'
        found_label = find_label_file(label_basename)
        orig_annot = draw_yolo_boxes(orig_img, found_label, class_names, color=(0, 200, 0), thickness=2)
        # add footer after drawing boxes to ensure label area not overwritten
        orig_annot = add_footer_text(orig_annot, orig_label)

        grid = make_grid(orig_annot, im_nano, im_small, im_medium)
        # prepare display filename: trim extensions and trailing '_jpg'/'_png' tokens
        base = os.path.splitext(fname)[0]
        # remove common trailing tokens like '_jpg', '_jpeg', '_png' and anything after them
        for tok in ('_jpg', '_jpeg', '_png'):
            pos = base.find(tok)
            if pos != -1:
                base = base[:pos]
                break

        # draw centered title at top of grid
        gh, gw = grid.shape[:2]
        title_text = base
        font_scale_title = max(0.6, min(2.5, gh / 600.0))
        t_th = max(1, int(gh / 400.0))
        (tw, th), _ = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale_title, t_th)
        # place text at top-center with slight background for readability
        x_center = (gw - tw) // 2
        y_top = int(10 + th)
        overlay = grid.copy()
        cv2.rectangle(overlay, (x_center - 8, y_top - th - 8), (x_center + tw + 8, y_top + 6), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, grid, 0.5, 0, grid)
        cv2.putText(grid, title_text, (x_center, y_top), cv2.FONT_HERSHEY_SIMPLEX, font_scale_title, (255, 255, 255), t_th, cv2.LINE_AA)

        title = f'[{idx+1}/{len(files)}] {fname}  --  q=quit, arrows/n/p=nav'
        cv2.imshow(window_name, grid)
        key = cv2.waitKey(0)

        # key mapping: q or Q to quit; right arrow(83) next, left arrow(81) prev.
        if key in (ord('q'), ord('Q')):
            break
        if key in (83, ord('n'), ord('d')):
            idx = (idx + 1) % len(files)
            continue
        if key in (81, ord('p'), ord('a')):
            idx = (idx - 1) % len(files)
            continue

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
