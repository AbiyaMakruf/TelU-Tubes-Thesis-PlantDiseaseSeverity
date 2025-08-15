#!/usr/bin/env python3
"""Split images into class folders based on train.csv labels.

Usage example:
  python utils/split_by_class.py \
    --csv dataset/original_dataset/train.csv \
    --images dataset/original_dataset/train_images \
    --out dataset/original_dataset_split_by_class

This script copies images that belong to any of the target classes
('healthy', 'rust', 'frog_eye_leaf_spot') into corresponding
subfolders under the output folder. If an image has multiple labels,
it will be copied into each matching class folder.
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
import json
from typing import Iterable, List, Set


DEFAULT_CLASSES = ["healthy", "rust", "frog_eye_leaf_spot"]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_labels_field(field: str) -> List[str]:
    """Parse the labels field into a list of label tokens.

    Common label formats are space-separated tokens (e.g. "healthy rust").
    We split on whitespace and strip tokens.
    """
    if field is None:
        return []
    return [tok.strip() for tok in field.split() if tok.strip()]


def split_by_class(csv_path: str, images_dir: str, out_dir: str, classes: Iterable[str]) -> dict:
    """Read CSV and copy images to class folders.

    Returns a summary dict with counts and missing files.
    """
    classes = list(classes)
    class_set: Set[str] = set(classes)

    # Prepare output folders
    for cls in classes:
        ensure_dir(os.path.join(out_dir, cls))

    counts = {cls: 0 for cls in classes}
    missing_files: List[str] = []
    processed_images: Set[str] = set()

    # Read CSV
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Expect headers 'image' and 'labels'
        if 'image' not in reader.fieldnames or 'labels' not in reader.fieldnames:
            raise ValueError("CSV must contain 'image' and 'labels' headers")
from __future__ import annotations

import csv
import json
import os
import shutil
import sys
from typing import Iterable, List, Set


DEFAULT_CLASSES = ["healthy", "rust", "frog_eye_leaf_spot"]
DEFAULT_CONFIG = os.path.join('utils', 'split_config.json')


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_labels_field(field: str) -> List[str]:
    if field is None:
        return []
    return [tok.strip() for tok in field.split() if tok.strip()]


def split_by_class(csv_path: str, images_dir: str, out_dir: str, classes: Iterable[str]) -> dict:
    classes = list(classes)
    class_set: Set[str] = set(classes)

    # Prepare output folders
    for cls in classes:
        ensure_dir(os.path.join(out_dir, cls))

    counts = {cls: 0 for cls in classes}
    missing_files: List[str] = []
    processed_images: Set[str] = set()

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if 'image' not in reader.fieldnames or 'labels' not in reader.fieldnames:
            raise ValueError("CSV must contain 'image' and 'labels' headers")

        for row in reader:
            image_name = row.get('image')
            labels_field = row.get('labels', '')
            if not image_name:
                continue

            labels = parse_labels_field(labels_field)
            matches = [lbl for lbl in labels if lbl in class_set]
            if not matches:
                continue

            src_path = os.path.join(images_dir, image_name)
            if not os.path.isfile(src_path):
                missing_files.append(src_path)
                continue

            for cls in matches:
                dst_dir = os.path.join(out_dir, cls)
                ensure_dir(dst_dir)
                dst_path = os.path.join(dst_dir, image_name)
                try:
                    if os.path.isfile(dst_path):
                        if os.path.getsize(dst_path) == os.path.getsize(src_path):
                            counts[cls] += 1
                            continue
                    shutil.copy2(src_path, dst_path)
                    counts[cls] += 1
                except Exception:
                    missing_files.append(src_path)

            processed_images.add(image_name)

    summary = {
        'counts': counts,
        'processed_images': len(processed_images),
        'missing_files': missing_files,
    }
    return summary


def read_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main() -> int:
    # Read config from utils/split_config.json
    try:
        cfg = read_config(DEFAULT_CONFIG)
    except Exception as e:
        print(f'Failed to read config {DEFAULT_CONFIG}: {e}', file=sys.stderr)
        return 2

    csv_path = cfg.get('csv')
    images_path = cfg.get('images')
    out_path = cfg.get('out')
    classes_cfg = cfg.get('classes')
    classes = classes_cfg if isinstance(classes_cfg, list) else (classes_cfg.split(',') if isinstance(classes_cfg, str) else DEFAULT_CLASSES)

    if not (csv_path and images_path and out_path):
        print('csv, images, and out must be set in utils/split_config.json', file=sys.stderr)
        return 2

    summary = split_by_class(csv_path, images_path, out_path, classes)

    print('\nSplit summary:')
    for cls, cnt in summary['counts'].items():
        print(f'  {cls}: {cnt}')
    print(f"Processed unique images: {summary['processed_images']}")
    if summary['missing_files']:
        print(f"Missing or failed copies: {len(summary['missing_files'])} (examples):")
        for pth in summary['missing_files'][:10]:
            print('   ', pth)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
