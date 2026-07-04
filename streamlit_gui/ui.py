from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from image_ops import error_map_image, reference_mask_image


MAX_DISPLAY_SIDE = 1400


def _image(target, image, caption: str) -> None:
    image = _prepare_display_image(image)
    try:
        target.image(image, caption=caption, width="stretch")
    except TypeError:
        target.image(image, caption=caption, use_container_width=True)


def _dataframe(table) -> None:
    try:
        st.dataframe(table, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(table, use_container_width=True, hide_index=True)


def _prepare_display_image(image):
    if not isinstance(image, np.ndarray) or image.ndim < 2:
        return image
    height, width = image.shape[:2]
    longest_side = max(height, width)
    if longest_side <= MAX_DISPLAY_SIDE:
        return image
    scale = MAX_DISPLAY_SIDE / longest_side
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return np.asarray(Image.fromarray(image).resize(new_size, Image.Resampling.LANCZOS))


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2.5rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid #E6E8EC;
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            background: #FFFFFF;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.45rem;
        }
        .small-note {
            color: #4B5563;
            font-size: 0.92rem;
            line-height: 1.35;
        }
        .winner-card {
            border: 2px solid #16A34A;
            background: #F0FDF4;
            border-radius: 8px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.75rem;
        }
        .comparison-card {
            border: 1px solid #E6E8EC;
            background: #FFFFFF;
            border-radius: 8px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
        }
        .check-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.25rem;
            height: 1.25rem;
            border-radius: 999px;
            background: #16A34A;
            color: white;
            font-weight: 800;
            margin-right: 0.45rem;
        }
        .error-bar-track {
            height: 0.55rem;
            border-radius: 999px;
            background: #E5E7EB;
            overflow: hidden;
            margin-top: 0.45rem;
        }
        .error-bar-fill {
            height: 100%;
            border-radius: 999px;
            background: #2563EB;
        }
        .error-bar-fill.winner {
            background: #16A34A;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.title("Few-Shot Object Detection for Apple Leaf Disease Severity Estimation")
    st.caption("Demo interaktif: Ground Truth vs Single-Stage Pipeline vs Two-Stage Pipeline")


def severity_table(case: dict) -> pd.DataFrame:
    gt = case["gt"].severity
    single = case["single"].severity
    two_stage = case["two_stage"].severity
    single_error = abs(single - gt)
    two_stage_error = abs(two_stage - gt)
    best_label = closest_pipeline_label(case)
    return pd.DataFrame(
        {
            "Skenario": [
                "Ground Truth",
                "Single-Stage Pipeline",
                "Two-Stage Pipeline",
            ],
            "Estimasi Keparahan (%)": [gt, single, two_stage],
            "Absolute Error vs GT (%)": [0.0, single_error, two_stage_error],
            "Kedekatan ke GT": [
                "Referensi",
                "✓ Terdekat" if best_label == "Single-Stage Pipeline" else "",
                "✓ Terdekat" if best_label == "Two-Stage Pipeline" else "",
            ],
        }
    )


def closest_pipeline_label(case: dict) -> str:
    gt = case["gt"].severity
    errors = {
        "Single-Stage Pipeline": abs(case["single"].severity - gt),
        "Two-Stage Pipeline": abs(case["two_stage"].severity - gt),
    }
    return min(errors, key=errors.get)


def render_metric_strip(case: dict) -> None:
    gt = case["gt"].severity
    single = case["single"].severity
    two_stage = case["two_stage"].severity
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GT Severity", f"{gt:.2f}%")
    c2.metric("Single-Stage", f"{single:.2f}%", delta=f"{single - gt:+.2f}% vs GT")
    c3.metric("Two-Stage", f"{two_stage:.2f}%", delta=f"{two_stage - gt:+.2f}% vs GT")
    best_label = closest_pipeline_label(case).replace(" Pipeline", "")
    best_error = min(abs(single - gt), abs(two_stage - gt))
    c4.metric("Terdekat ke GT", f"✓ {best_label}", delta=f"error {best_error:.2f}%")


def render_visual_comparison(case: dict) -> None:
    st.subheader("Komparasi Visual Tiga Skenario")
    col_gt, col_single, col_two = st.columns(3)
    with col_gt:
        _image(st, case["gt"].overlay, "Ground Truth: masker referensi daun dan lesi")
        st.metric("Severity GT", f"{case['gt'].severity:.2f}%")
        st.caption(case["gt"].status)
    with col_single:
        _image(st, case["single"].overlay, "Single-Stage: direct segmentation full image")
        st.metric("Severity Single-Stage", f"{case['single'].severity:.2f}%")
        st.caption(case["single"].status)
    with col_two:
        _image(st, case["two_stage"].full_overlay, "Two-Stage: detection-guided segmentation ROI")
        st.metric("Severity Two-Stage", f"{case['two_stage'].severity:.2f}%")
        st.caption(case["two_stage"].status)


def render_pipeline_tabs(case: dict) -> None:
    st.subheader("Visualisasi Tahapan Output")
    tab_gt, tab_single, tab_two = st.tabs(["Ground Truth", "Single-Stage Pipeline", "Two-Stage Pipeline"])

    with tab_gt:
        cols = st.columns(3)
        _image(cols[0], case["original"], "Citra asli")
        _image(
            cols[1],
            reference_mask_image(case["gt"].leaf_mask, case["gt"].lesion_mask),
            "Masker referensi daun dan lesi",
        )
        cols[2].metric("Nilai keparahan asli", f"{case['gt'].severity:.2f}%")

    with tab_single:
        cols = st.columns(3)
        _image(cols[0], case["original"], "Citra asli")
        _image(cols[1], case["single"].overlay, "Masking daun dan lesi langsung")
        cols[2].metric("Nilai akhir keparahan", f"{case['single'].severity:.2f}%")
        st.caption("Model: segmentation best.pt dijalankan langsung pada citra penuh sebagai baseline Single-Stage.")

    with tab_two:
        cols = st.columns(5)
        _image(cols[0], case["original"], "Citra asli")
        _image(cols[1], case["two_stage"].bbox_image, "Bounding box daun terbesar")
        _image(cols[2], case["two_stage"].crop_image, "Cropping ROI")
        _image(cols[3], case["two_stage"].overlay, "Masking daun dan lesi ROI")
        cols[4].metric("Nilai akhir keparahan", f"{case['two_stage'].severity:.2f}%")
        st.caption("Model: YOLOv12-Medium K=40 untuk deteksi ROI terbesar, lalu YOLOv11-Nano 1024px untuk segmentasi daun dan lesi.")


def render_error_analysis(case: dict) -> None:
    st.subheader("Analisis Miss Detection dan Wrong Detection")
    st.caption("Hijau: lesi benar terdeteksi | Biru: miss detection | Kuning: wrong detection")
    cols = st.columns(3)
    with cols[0]:
        _image(
            st,
            reference_mask_image(case["gt"].leaf_mask, case["gt"].lesion_mask),
            "Ground Truth: masker referensi daun dan lesi",
        )
    with cols[1]:
        _image(
            st,
            error_map_image(case["original"], case["gt"].lesion_mask, case["single"].lesion_mask),
            "Single-Stage: miss/wrong detection lesi",
        )
    with cols[2]:
        _image(
            st,
            error_map_image(case["original"], case["gt"].lesion_mask, case["two_stage"].full_lesion_mask),
            "Two-Stage: miss/wrong detection lesi",
        )


def render_upload_inference_results(cases: list[dict]) -> None:
    st.subheader("Ringkasan Severity Gambar Upload")
    rows = []
    for index, case in enumerate(cases, start=1):
        rows.append(
            {
                "Gambar": index,
                "Nama File": case["image_name"],
                "Single-Stage Severity (%)": case["single"].severity,
                "Two-Stage Severity (%)": case["two_stage"].severity,
                "Selisih Single vs Two (%)": abs(case["single"].severity - case["two_stage"].severity),
            }
        )
    table = pd.DataFrame(rows)
    _dataframe(
        table.style.format(
            {
                "Single-Stage Severity (%)": "{:.2f}",
                "Two-Stage Severity (%)": "{:.2f}",
                "Selisih Single vs Two (%)": "{:.2f}",
            }
        )
    )

    for index, case in enumerate(cases, start=1):
        with st.expander(f"Gambar {index}: {case['image_name']}", expanded=index == 1):
            st.markdown(
                f"**Single-Stage:** {case['single'].severity:.2f}% | "
                f"**Two-Stage:** {case['two_stage'].severity:.2f}%"
            )
            cols = st.columns(4)
            _image(cols[0], case["original"], "Citra upload")
            _image(cols[1], case["single"].overlay, "Single-Stage segmentation")
            _image(cols[2], case["two_stage"].bbox_image, "Two-Stage detection dan crop area")
            _image(cols[3], case["two_stage"].full_overlay, "Two-Stage segmentation")


def render_result_table(case: dict) -> None:
    st.subheader("Komparasi Nilai Estimasi Keparahan")
    table = severity_table(case)
    _dataframe(
        table.style.format(
            {
                "Estimasi Keparahan (%)": "{:.2f}",
                "Absolute Error vs GT (%)": "{:.2f}",
            }
        )
    )


def render_closeness_panel(case: dict) -> None:
    st.subheader("Kedekatan Estimasi ke GT")
    gt = case["gt"].severity
    rows = [
        ("Single-Stage Pipeline", case["single"].severity, abs(case["single"].severity - gt)),
        ("Two-Stage Pipeline", case["two_stage"].severity, abs(case["two_stage"].severity - gt)),
    ]
    best_label = closest_pipeline_label(case)
    max_error = max(row[2] for row in rows) or 1.0

    winner = next(row for row in rows if row[0] == best_label)
    st.markdown(
        f"""
        <div class="winner-card">
            <div><span class="check-badge">✓</span><strong>{winner[0]}</strong> paling dekat dengan GT.</div>
            <div class="small-note">GT {gt:.2f}% | Estimasi {winner[1]:.2f}% | Absolute error {winner[2]:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for label, severity, error in rows:
        is_winner = label == best_label
        icon = '<span class="check-badge">✓</span>' if is_winner else ""
        card_class = "winner-card" if is_winner else "comparison-card"
        fill_class = "error-bar-fill winner" if is_winner else "error-bar-fill"
        width = max(4.0, (error / max_error) * 100.0)
        st.markdown(
            f"""
            <div class="{card_class}">
                <div>{icon}<strong>{label}</strong></div>
                <div class="small-note">Severity {severity:.2f}% | Error ke GT {error:.2f}%</div>
                <div class="error-bar-track">
                    <div class="{fill_class}" style="width: {width:.1f}%"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
