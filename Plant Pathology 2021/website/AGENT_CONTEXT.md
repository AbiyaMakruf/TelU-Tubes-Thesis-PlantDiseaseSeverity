Project context snapshot — store this in repo so future agents immediately understand the project

Purpose
- Web UI (Flask) for plant leaf object detection, segmentation, and severity estimation.
- Drop-in demo that accepts an uploaded image, runs detection and segmentation models (Ultralytics YOLO), computes per-leaf severity (%) and returns annotated images.

Important locations (relative to repo root)
- website/app.py — Flask application (entrypoint for UI and `/predict` logic).
- website/templates/ — Jinja templates (upload form, results pages).
- website/static/ — static assets (examples, graphs, etc.).
- website/uploads/ — directory where uploaded images and intermediate crops are saved.
- website/results_predict/ — annotated outputs and saved severity crops.
- website/models/ — expected subfolders: `object_detection/` and `segmentation/` with .pt/.pth weights.

Key runtime expectations & session keys
- Flask session keys used: `last_uploaded`, `last_task`, `last_det_model`, `last_seg_model`, `last_pad`, `last_multi_leaf`.
- Upload preference order in `/predict`: multipart `file` if present → `existing_file` (hidden input) flexible match → session `last_uploaded` fallback.

How severity estimation works (concise)
1. Run detection model on full image to get bounding boxes.
2. For each chosen box, crop with padding and run segmentation model on the crop.
3. Combine leaf-class masks for the crop (union) to form `combined_leaf`.
4. Find paired lesion masks (per leaf class) and compute `lesion_in_leaf = combined_lesion & combined_leaf`.
5. Severity % = lesion_px / leaf_px * 100
6. Create overlays: leaf semi-transparent green; lesion dark-red fully opaque (lesion should completely cover original lesion pixels).

Dependencies (high level)
- Python 3.8+
- Flask
- ultralytics (YOLO)
- Pillow, numpy

Quick notes
- If the app asks to re-upload even after a file was selected, inspect the browser DevTools POST multipart payload: is the `file` binary included or only `existing_file`? The server logs print a debug line starting with `[PREDICT] existing_field=...` that helps diagnose this.
- Keep models in the `website/models` subtree. Model discovery uses `find_model()` in `app.py`.

Contact
- Owner: AbiyaMakruf (local dev)
- Repo: TelU-Tubes-Thesis-PlantDiseaseSeverity

Saved: {date}
