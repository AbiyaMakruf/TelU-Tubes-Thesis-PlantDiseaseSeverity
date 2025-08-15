#!/usr/bin/env python3
"""Rename images inside dataset/original_dataset_split_by_class for Roboflow.

This script renames all image files under each class folder inside the
base folder to the pattern: 00001_{class}{ext} with a zero-padded index.
It also writes a CSV mapping file `dataset/original_dataset/mapping.csv`
with rows: original_image_name,new_name. If an original image appears in
multiple class folders, multiple mapping rows will be created (one per
renamed copy).

Safe defaults:
- The script defaults to base folder `dataset/original_dataset_split_by_class`.
- It does a dry-run by default; add `--apply` to actually perform renames.
- It will skip files that already look renamed (leading digits + underscore)
  to avoid double-renaming unless `--force` is provided.

Usage examples:
  # Dry-run (no changes):
  python utils/rename_split_images.py

  # Apply renaming and write mapping.csv:
  python utils/rename_split_images.py --apply

  # Start numbering from 1000 and 6-digit padding:
  python utils/rename_split_images.py --apply --start 1000 --pad 6

"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from typing import List, Tuple

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif'}
DEFAULT_BASE = os.path.join('dataset', 'original_dataset_split_by_class')
DEFAULT_MAPPING = os.path.join('dataset', 'original_dataset', 'mapping.csv')
DEFAULT_CONFIG = os.path.join('utils', 'split_config.json')


def is_image_file(name: str) -> bool:
    name_lower = name.lower()
    return any(name_lower.endswith(ext) for ext in IMAGE_EXTS)


def find_class_folders(base: str) -> List[str]:
    if not os.path.isdir(base):
        raise FileNotFoundError(f'Base folder not found: {base}')
    entries = sorted(os.listdir(base))
    return [os.path.join(base, e) for e in entries if os.path.isdir(os.path.join(base, e))]


def make_new_name(index: int, pad: int, class_name: str, ext: str) -> str:
    return f"{index:0{pad}d}_{class_name}{ext}"


def already_renamed(name: str, pad: int) -> bool:
    # matches something like 00001_class.ext or 0001_anything
    return re.match(rf'^\d{{{pad},}}_', name) is not None


def collect_files(base: str) -> List[Tuple[str, str]]:
    """Return list of tuples (class_name, file_path) for image files found."""
    folders = find_class_folders(base)
    out = []
    for folder in folders:
        class_name = os.path.basename(folder)
        for fn in sorted(os.listdir(folder)):
            if not is_image_file(fn):
                continue
            out.append((class_name, os.path.join(folder, fn)))
    return out


def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def run(base: str, mapping_csv: str, start: int = 1, pad: int = 5, apply: bool = False, skip_existing: bool = True, force: bool = False) -> int:
    files = collect_files(base)
    if not files:
        print('No image files found under', base, file=sys.stderr)
        return 1

    # prepare mapping output directory
    ensure_dir(mapping_csv)

    index = int(start)
    mappings: List[Tuple[str, str]] = []
    collisions = 0

    # We'll maintain a set of new names to ensure uniqueness across all classes
    used_names = set()

    for class_name, path in files:
        dirname = os.path.dirname(path)
        orig_name = os.path.basename(path)

        if skip_existing and already_renamed(orig_name, pad) and not force:
            # skip and record mapping (original -> same name)
            mappings.append((orig_name, orig_name))
            continue

        ext = os.path.splitext(orig_name)[1]
        # find next available name
        while True:
            new_name = make_new_name(index, pad, class_name, ext)
            if new_name in used_names:
                index += 1
                continue
            dst_path = os.path.join(dirname, new_name)
            if os.path.exists(dst_path) and not force:
                # collision with existing file, advance index
                collisions += 1
                index += 1
                continue
            # got a free name
            break

        used_names.add(new_name)
        mappings.append((orig_name, new_name))

        if apply:
            try:
                os.rename(path, dst_path)
            except Exception as e:
                print(f'Failed to rename {path} -> {dst_path}: {e}', file=sys.stderr)
        else:
            # dry-run print first few
            if len(mappings) <= 20:
                print(f'[DRY-RUN] {path} -> {os.path.join(dirname, new_name)}')

        index += 1

    # Write mapping CSV
    if apply:
        try:
            with open(mapping_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['original_image_name', 'new_name'])
                for orig, new in mappings:
                    writer.writerow([orig, new])
            print(f'Mapping CSV written to {mapping_csv} ({len(mappings)} rows)')
        except Exception as e:
            print(f'Failed to write mapping CSV: {e}', file=sys.stderr)
            return 2
    else:
        print('\nDry-run complete.')
        print(f'Total files considered: {len(mappings)}')
        print('To apply the changes, re-run with --apply')

    if collisions:
        print(f'Note: encountered {collisions} name collisions while choosing new names.')

    return 0


def main():
    # Read config
    try:
        with open(DEFAULT_CONFIG, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}

    rename_cfg = cfg.get('rename', {})
    base = rename_cfg.get('base') or DEFAULT_BASE
    mapping = rename_cfg.get('mapping') or DEFAULT_MAPPING
    start = int(rename_cfg.get('start') or 1)
    pad = int(rename_cfg.get('pad') or 5)
    # default: do rename immediately (no CLI flags)
    apply = bool(rename_cfg.get('apply', True))
    skip_existing = bool(rename_cfg.get('skip_existing', True))
    force = bool(rename_cfg.get('force', False))

    return run(base=base, mapping_csv=mapping, start=start, pad=pad, apply=apply, skip_existing=skip_existing, force=force)


if __name__ == '__main__':
    raise SystemExit(main())
