Quick start for an assistant agent (placed in `website/`)

Goal
- Help the user run or improve the Flask app that performs detection, segmentation and severity estimation on plant leaf images.

What to read first
- `AGENT_CONTEXT.md` — high-level project snapshot.
- `AGENT_CONTEXT.json` — machine-friendly summary.
- `app.py` — main Flask app and inference logic.
- `templates/upload.html` — UI behavior for upload / existing_file handling.

Quick run (developer machine)
1. Create and activate a Python environment (Windows cmd example):

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

2. Start the Flask app (from repo root):

   set FLASK_APP=website/app.py
   set FLASK_ENV=development
   python -m flask run

3. Visit http://127.0.0.1:5000/upload

Debugging tips
- If the UI keeps asking for re-upload: open browser DevTools -> Network -> POST /predict -> inspect Form Data. If `file` is missing but `existing_file` is present, the client JS may only populate the hidden field and not include the binary when the user intended to upload.
- Check Flask logs for lines starting with `[PREDICT]` which include debug context about `existing_field`, `uploads_list`, and `session_last_uploaded`.

If you add or remove models, ensure they are placed under `website/models/object_detection` or `website/models/segmentation`.

When making changes
- Run `python -m py_compile website/app.py` to check syntax quickly.
- Run a small POST test using `website/upload_test.py` (exists) to simulate a multipart upload.

Contact
- Owner: AbiyaMakruf
