Plant Pathology 2021 — Website (Flask)

This is a lightweight Flask-based website alternative to the Streamlit demo. It provides pages:
- Home
- Dataset
- Project
- Upload & Predict
- Results

How to run

1. Create a virtual environment and activate it.
2. Install dependencies:
   pip install -r requirements.txt
3. Place your object-detection model (.pt/.pth) under:
   website/models/object_detection/
4. Run the app:
   python app.py

Notes
- The app tries to load the first model it finds under models/object_detection if you don't select one.
- The app requires the `ultralytics` package to load YOLO models. If you don't want inference, you can still browse the pages.
