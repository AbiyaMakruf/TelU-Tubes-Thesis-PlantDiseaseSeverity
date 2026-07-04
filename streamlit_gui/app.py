from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data import DISEASE_CLASSES, discover_samples
from image_ops import build_demo_case
from ui import (
    inject_css,
    render_closeness_panel,
    render_header,
    render_metric_strip,
    render_pipeline_tabs,
    render_result_table,
    render_visual_comparison,
)


st.set_page_config(
    page_title="Apple Leaf Disease Severity Demo",
    layout="wide",
)


MODEL_OD_PATH = APP_DIR / "model" / "object-detection" / "best.pt"
MODEL_SEG_PATH = APP_DIR / "model" / "segmentation" / "best.pt"


@st.cache_resource(show_spinner="Memuat model YOLO...")
def load_models():
    from ultralytics import YOLO

    if not MODEL_OD_PATH.exists():
        raise FileNotFoundError(f"Model object detection tidak ditemukan: {MODEL_OD_PATH}")
    if not MODEL_SEG_PATH.exists():
        raise FileNotFoundError(f"Model segmentation tidak ditemukan: {MODEL_SEG_PATH}")
    return YOLO(MODEL_OD_PATH), YOLO(MODEL_SEG_PATH)


def sidebar_controls():
    st.sidebar.header("Pengaturan Sampel")
    samples_by_class = discover_samples()
    available_classes = [disease_class for disease_class in DISEASE_CLASSES if samples_by_class[disease_class]]
    if not available_classes:
        st.sidebar.error("Tidak ada gambar ditemukan di streamlit_gui/dataset/images.")
        st.stop()

    if "disease_class" not in st.session_state or st.session_state.disease_class not in available_classes:
        st.session_state.disease_class = available_classes[0]
    if "sample_index_by_class" not in st.session_state:
        st.session_state.sample_index_by_class = {}

    disease_class = st.sidebar.selectbox(
        "Kelas penyakit",
        available_classes,
        index=available_classes.index(st.session_state.disease_class),
        key="disease_class_select",
    )
    if disease_class != st.session_state.disease_class:
        st.session_state.disease_class = disease_class
        st.session_state.sample_index_by_class[disease_class] = 0

    samples = samples_by_class[disease_class]
    sample_names = [sample.display_name for sample in samples]
    current_index = int(st.session_state.sample_index_by_class.get(disease_class, 0))
    current_index = max(0, min(current_index, len(samples) - 1))

    prev_col, index_col, next_col = st.sidebar.columns([1, 1.35, 1])
    with prev_col:
        if st.button("Sebelumnya", use_container_width=True, disabled=current_index == 0):
            current_index -= 1
    with next_col:
        if st.button("Berikutnya", use_container_width=True, disabled=current_index == len(samples) - 1):
            current_index += 1

    st.session_state.sample_index_by_class[disease_class] = current_index
    with index_col:
        st.markdown(
            f"<div style='text-align:center; padding-top:0.45rem;'>Gambar {current_index + 1}/{len(samples)}</div>",
            unsafe_allow_html=True,
        )

    selected_name = st.sidebar.selectbox(
        "Sampel uji",
        sample_names,
        index=current_index,
    )
    selected_index = sample_names.index(selected_name)
    if selected_index != current_index:
        current_index = selected_index
        st.session_state.sample_index_by_class[disease_class] = current_index

    sample = samples[current_index]

    st.sidebar.divider()
    st.sidebar.caption("Model aktif")
    st.sidebar.code(f"OD: {MODEL_OD_PATH.relative_to(APP_DIR)}")
    st.sidebar.code(f"SEG: {MODEL_SEG_PATH.relative_to(APP_DIR)}")

    return disease_class, sample, current_index + 1, len(samples)


def main() -> None:
    inject_css()
    render_header()
    _, sample, image_number, image_total = sidebar_controls()

    try:
        model_od, model_seg = load_models()
    except Exception as exc:
        st.error(f"Gagal memuat model YOLO: {exc}")
        st.stop()

    with st.spinner("Menjalankan object detection, cropping ROI, dan segmentation..."):
        case = build_demo_case(sample, model_od=model_od, model_seg=model_seg)

    st.markdown(
        f"**Gambar ke-{image_number} dari {image_total}** | **Sampel aktif:** {sample.display_name} | **Kelas:** {sample.disease_class} | "
        "rasio keparahan dihitung sebagai `(jumlah piksel lesi / jumlah piksel daun) * 100%`."
    )
    st.caption(f"GT label: `{sample.label_path.name}`")

    render_metric_strip(case)
    render_visual_comparison(case)
    render_pipeline_tabs(case)

    left, right = st.columns([1.05, 0.95])
    with left:
        render_result_table(case)
    with right:
        render_closeness_panel(case)


if __name__ == "__main__":
    main()
