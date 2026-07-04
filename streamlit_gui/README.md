# Streamlit Thesis Demo

GUI demonstrasi interaktif untuk tesis:

`Few-Shot Object Detection for Apple Leaf Disease Severity Estimation Using Two-Stage Fine-Tuned YOLO`

## Menjalankan Demo

Dari root repository, gunakan salah satu opsi berikut.

Dengan environment Python/Conda/venv yang sudah aktif:

```bash
pip install -r streamlit_gui/requirements.txt
streamlit run streamlit_gui/app.py
```

Atau dengan `uv` tanpa membuat virtualenv di dalam repo:

```bash
uv run --with streamlit --with numpy --with pandas --with pillow --with ultralytics streamlit run streamlit_gui/app.py
```

## Fitur

- Pemilihan 3 kelas penyakit: `Healthy`, `Rust`, dan `Frog-eye Leaf Spot`.
- Pilihan sampel dari `streamlit_gui/dataset/images`.
- Ground Truth otomatis dibangun dari polygon YOLO di `streamlit_gui/dataset/labels`.
- Komparasi visual berdampingan untuk:
  - Ground Truth
  - Single-Stage Pipeline: model segmentation langsung pada citra penuh.
  - Two-Stage Pipeline: object detection daun terbesar, crop ROI, lalu segmentation daun dan lesi.
- Visualisasi tahapan pipeline:
  - Ground Truth: citra asli, masker referensi, nilai keparahan.
  - Single-Stage: citra asli, segmentasi langsung, nilai keparahan.
  - Two-Stage: citra asli, bounding box YOLOv12-Medium K=40, crop ROI, segmentasi YOLOv11-Nano 1024px, nilai keparahan.
- Kalkulasi otomatis severity:

```text
(jumlah piksel lesi / jumlah piksel daun) * 100%
```

- Panel kedekatan estimasi ke GT:
  - Menampilkan absolute error Single-Stage dan Two-Stage untuk sampel aktif.
  - Memberikan centang hijau pada pipeline yang paling dekat dengan GT.

## Model dan Label

App memakai model berikut:

- `streamlit_gui/model/object-detection/best.pt`
- `streamlit_gui/model/segmentation/best.pt`

Konfigurasi class mengikuti notebook `severity_estimation_experiment/notebook.ipynb`:

- Daun: class id `0`, `2`, `3`
- Lesi: class id `1`, `4`
- Object detection confidence: `0.25`
- Segmentation confidence: `0.10`
- Crop padding ratio: `0.30`
