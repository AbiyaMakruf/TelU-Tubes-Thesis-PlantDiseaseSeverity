#!/usr/bin/env python3
"""Create subset folders with limited images per class and split into train/valid/test.

Reads configuration from utils/split_config.json by default. It will:
- For each class folder under `base_split_dir`, take the first N images (sorted)
  where N is `per_class_limit` (250 by default).
- Split them sequentially into train/valid/test using ratios (70/10/20 default).
- Copy images into `out_dir/{subset}/{class}` preserving extensions.
- Write a mapping CSV `mapping_csv` with columns: original_path,new_path,subset

The script does not attempt to deduplicate images that are present in multiple
class folders; each file found under a class folder is treated independently
(as they are separate files/copies in class folders).
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys
from typing import Dict, List, Tuple

DEFAULT_CONFIG = os.path.join('utils', 'split_config.json')


def load_config(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def is_image_file(name: str) -> bool:
    return os.path.splitext(name)[1].lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif'}


def collect_class_images(base_split_dir: str) -> Dict[str, List[str]]:
    classes = {}
    if not os.path.isdir(base_split_dir):
        raise FileNotFoundError(base_split_dir)
    for entry in sorted(os.listdir(base_split_dir)):
        folder = os.path.join(base_split_dir, entry)
        if not os.path.isdir(folder):
            continue
        images = [f for f in sorted(os.listdir(folder)) if is_image_file(f)]
        classes[entry] = [os.path.join(folder, f) for f in images]
    return classes


def split_counts(total: int, ratios: Dict[str, float]) -> Dict[str, int]:
    # Ratios expected to sum to ~1.0, e.g. {'train':0.7,'valid':0.1,'test':0.2}
    train_n = int(math.floor(total * ratios.get('train', 0.7)))
    valid_n = int(math.floor(total * ratios.get('valid', 0.1)))
    test_n = total - train_n - valid_n
    return {'train': train_n, 'valid': valid_n, 'test': test_n}


def run(config_path: str = DEFAULT_CONFIG, dry_run: bool = False) -> int:
    cfg = load_config(config_path)
    subset_cfg = cfg.get('subset', {})
    base_split_dir = subset_cfg.get('base_split_dir')
    out_dir = subset_cfg.get('out_dir')
    per_class_limit = int(subset_cfg.get('per_class_limit', 250))
    ratios = subset_cfg.get('ratios', {'train': 0.7, 'valid': 0.1, 'test': 0.2})
    mapping_csv = subset_cfg.get('mapping_csv')

    if not (base_split_dir and out_dir and mapping_csv):
        print('Invalid subset config in', config_path, file=sys.stderr)
        return 2

    classes = collect_class_images(base_split_dir)
    all_mappings: List[Tuple[str, str, str]] = []  # orig, new, subset

    for cls, paths in classes.items():
        selected = paths[:per_class_limit]
        counts = split_counts(len(selected), ratios)
        # sequential split
        idx = 0
        for subset_name in ('train', 'valid', 'test'):
            n = counts[subset_name]
            for i in range(n):
                if idx >= len(selected):
                    break
                src = selected[idx]
                fname = os.path.basename(src)
                # place files directly under out_dir/{subset} (no per-class subfolders)
                dst_dir = os.path.join(out_dir, subset_name)
                ensure_dir(dst_dir)

                # use original filename (no class prefix)
                dst_path = os.path.join(dst_dir, fname)

                # if collision occurs (unlikely per your note), append a counter
                if os.path.exists(dst_path):
                    base, ext = os.path.splitext(fname)
                    counter = 1
                    while True:
                        new_name = f"{base}_{counter}{ext}"
                        dst_path = os.path.join(dst_dir, new_name)
                        if not os.path.exists(dst_path):
                            fname = new_name
                            break
                        counter += 1

                all_mappings.append((src, dst_path, subset_name))
                if not dry_run:
                    try:
                        shutil.copy2(src, dst_path)
                    except Exception as e:
                        print(f'Failed to copy {src} -> {dst_path}: {e}', file=sys.stderr)
                idx += 1

    # Write mapping CSV
    if not dry_run:
        try:
            parent_dir = os.path.dirname(mapping_csv) or '.'
            ensure_dir(parent_dir)
            with open(mapping_csv, 'w', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.writer(f)
                # concise mapping: filename in subset, subset name
                writer.writerow(['name_file', 'subset'])
                for orig, new, subset in all_mappings:
                    writer.writerow([os.path.basename(new), subset])
            print(f'Mapping CSV written to {mapping_csv} ({len(all_mappings)} rows)')
        except Exception as e:
            print(f'Failed to write mapping CSV: {e}', file=sys.stderr)
            return 3
    else:
        print('Dry-run complete. Files selected (examples):')
        for entry in all_mappings[:20]:
            print(' ', entry)
        print(f'Total files to copy: {len(all_mappings)}')

    return 0


if __name__ == '__main__':
    # default run (not dry-run)
    raise SystemExit(run())
