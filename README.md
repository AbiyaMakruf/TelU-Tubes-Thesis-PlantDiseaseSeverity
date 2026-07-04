# Few-Shot Object Detection for Apple Leaf Disease Severity Estimation Using Two-Stage Fine-Tuned YOLO

![Research overview](README/fig_appendix_overview_of_the_proposed_research.png)

This repository contains the implementation, thesis materials, and interactive Streamlit demonstration for a master's thesis on apple leaf disease severity estimation. The research focuses on improving severity estimation under limited annotated data by combining few-shot object detection with detection-guided segmentation.

The central idea is to localize the most relevant apple leaf first, crop it as a region of interest, and then segment the leaf and disease lesions inside that crop. This two-stage pipeline is compared against a direct single-stage segmentation pipeline to evaluate whether localization before segmentation improves disease severity estimation.

## Thesis Overview

| Item | Description |
| --- | --- |
| Thesis title | Few-Shot Object Detection for Apple Leaf Disease Severity Estimation Using Two-Stage Fine-Tuned YOLO |
| Domain | Computer vision for plant disease severity estimation |
| Disease classes | Healthy, Rust, Frog-eye Leaf Spot |
| Detection model family | YOLOv12 |
| Segmentation model family | YOLOv11 |
| Main pipeline | Detection-guided segmentation |
| Severity formula | `(lesion pixels / leaf pixels) * 100%` |
| Main result | Two-stage pipeline reduced MAE from `1.49%` to `0.66%` |

## Chapter I: Introduction

Chapter I motivates the problem of estimating apple leaf disease severity from field images. Visual disease assessment is important for crop monitoring, but manual scoring is subjective, time-consuming, and difficult to scale. Apple leaf images also contain natural variation in disease pattern, lighting, background complexity, and leaf placement.

The thesis frames severity estimation as a pixel-ratio problem: the diseased lesion area must be measured relative to the visible leaf area. This makes accurate leaf and lesion segmentation essential, especially when images contain multiple leaves or complex backgrounds.

![Disease progression illustration](README/fig_disease_progression_ai_generated.png)

![Simple and complex apple leaf backgrounds](README/fig_examples_simple_and_complex_background.png)

The research problem is therefore not only classification of disease type, but also accurate localization and segmentation for estimating how severe the infection is.

## Chapter II: Literature Review

Chapter II reviews prior work in plant disease analysis, disease severity estimation, YOLO-based object detection, segmentation, and few-shot learning. Earlier studies show that deep learning is effective for plant disease recognition, but many systems still depend on large labeled datasets or controlled image conditions.

![State of the art in plant disease analysis](README/fig_sota_plant_disease_analysis.png)

The chapter identifies a research gap at the intersection of three needs:

- robust apple leaf disease severity estimation in realistic image conditions,
- limited-data adaptation through few-shot learning,
- pipeline design that separates leaf localization from lesion segmentation.

Few-shot object detection is especially relevant because the detection model must adapt to apple leaf disease images with only a small number of annotated examples.

![Few-shot object detection taxonomy](README/fing_fsod_taxonomy.png)

Based on this review, the thesis proposes a two-stage fine-tuning strategy and a detection-guided segmentation pipeline as an alternative to direct segmentation.

## Chapter III: Research Methodology

Chapter III explains the complete research workflow, dataset preparation, annotation design, severity computation, model training, and pipeline construction.

The dataset is organized into three classes: Healthy, Rust, and Frog-eye Leaf Spot. The annotation process includes bounding boxes for leaf detection and polygon masks for leaf and lesion segmentation.

![Dataset class comparison](README/fig_class_comparison.png)

![Dataset diversity](README/fig_dataset_diversity.png)

The study uses empirical subset analysis to select representative few-shot samples. This supports the few-shot training setting by controlling how many examples are used for model adaptation.

![Empirical subset saturation](README/fig_empirical_subset_saturation.png)

For the annotation targets, object detection labels are used to localize apple leaves, while segmentation labels are used to distinguish leaf area and lesion area.

![Bounding box annotation examples](README/fig_bounding_box_examples.png)

![Leaf mask examples](README/fig_leaf_mask_examples.png)

![Lesion mask examples](README/fig_lesion_mask_examples_.png)

Severity is computed from the segmentation masks using the ratio between lesion pixels and leaf pixels.

![Severity computation illustration](README/fig_illustrate_severity_computation.jpg)

Two inference pipelines are compared:

- Single-stage pipeline: the original image is passed directly into a segmentation model.
- Two-stage pipeline: a detection model first localizes the largest apple leaf, then the cropped region is segmented.

![Single-stage pipeline](README/fig_single_stage_pipeline.png)

![Two-stage pipeline](README/fig_two_stage_pipeline.png)

The proposed method also applies two-stage fine-tuning for few-shot object detection, where a base model is first trained and then adapted using limited samples.

![Two-stage fine-tuning scheme 1](README/fig_two_stage_finetuning_scheme_1.png)

![Two-stage fine-tuning scheme 2](README/fig_two_stage_finetuning_scheme_2.png)

## Chapter IV: Results and Discussion

Chapter IV reports the experimental results for object detection, segmentation, few-shot adaptation, and final severity estimation.

For object detection, YOLOv12 variants are evaluated to select the detector used in the two-stage pipeline. The selected detector is responsible for finding the apple leaf region before segmentation.

![YOLOv8 to YOLOv12 detection comparison on training set](README/fig_yolo_v8-v12_comparison_train_set.png)

![YOLOv8 to YOLOv12 detection comparison on test set](README/fig_yolo_v8-v12_comparison_test_set.png)

![YOLOv12 detection size comparison on test set](README/fig_yolo_v12_comparison_for_detection_test_set.png)

For segmentation, YOLOv11 variants are compared under different object classes and image sizes. The segmentation model must predict both leaf and lesion masks because both are required for severity calculation.

![YOLOv8, YOLOv11, and YOLOv12 segmentation comparison on test set](README/fig_yolo_v8_v11_v12_comparison_for_segmentation_test_set.png)

![YOLOv11 leaf and lesion segmentation comparison on test set](README/fig_yolo_v11_comparison_segmentation_leaf_and_lesion_class_test_set.png)

![Segmentation image size effect](README/fig_segmentation_image_size_effect.png)

The few-shot object detection experiment studies the influence of model size and shot count. The K=40 medium configuration is highlighted as the best few-shot detection setting in the thesis, achieving strong detection performance while supporting the downstream two-stage severity pipeline.

![Few-shot heatmap comparison, medium model](README/fig_heatmap_comparison_medium.png)

![Few-shot K=40 medium confusion matrix](README/fig_confusion_matrix_few_shot_k40_medium.png)

The final severity estimation comparison shows the main contribution of the thesis: detection-guided segmentation reduces severity estimation error compared with direct segmentation.

![MAE comparison between single-stage and two-stage pipelines](README/fig_mae_pipeline_comparison.png)

![Comparative analysis of single-stage and two-stage severity estimation](README/fig_comparative_analysis_single_vs_two_stage.png)

![Inference results](README/fig_inference_results.png)

The two-stage pipeline improves Mean Absolute Error from `1.49%` in the single-stage pipeline to `0.66%`. The thesis also reports a Wilcoxon statistical test with `p = 1.23 x 10^-12`, supporting that the improvement is statistically significant.

## Chapter V: Conclusion and Recommendations

Chapter V concludes that separating leaf localization from leaf-lesion segmentation improves apple leaf disease severity estimation. The two-stage pipeline is especially useful when the original image contains multiple leaves, irrelevant background, or scale variation that can reduce direct segmentation accuracy.

The main conclusions are:

- YOLO-based few-shot detection can provide reliable apple leaf localization with limited annotated samples.
- Detection-guided cropping helps the segmentation model focus on the relevant leaf region.
- Severity estimation based on leaf and lesion pixel ratios becomes more accurate after localization.
- The two-stage pipeline achieves lower MAE than the single-stage pipeline.

The thesis also notes several limitations:

- the pipeline assumes the largest detected leaf is the target leaf,
- ground-truth masks still depend on manual annotation quality,
- the experiments use a fixed few-shot sampling design,
- the study focuses on pipeline-level improvement rather than modifying YOLO internals.

Recommended future work includes multi-leaf region selection, weakly supervised or semi-supervised annotation strategies, broader field validation, newer detector backbones, and repeated few-shot experiments with multiple random seeds.

## Repository Structure

```text
.
├── README.md
├── README/
│   └── thesis figures used by this README
├── TelU-BukuThesis/
│   └── thesis manuscript, LaTeX chapters, figures, and references
├── streamlit_gui/
│   ├── app.py
│   ├── data.py
│   ├── image_ops.py
│   ├── ui.py
│   ├── dataset/
│   │   ├── images/
│   │   └── labels/
│   └── model/
│       ├── object-detection/
│       └── segmentation/
└── severity_estimation_experiment/
    └── experimental notebook and supporting materials
```

## Streamlit Demonstration

The `streamlit_gui/` folder contains an interactive thesis demonstration application. It supports:

- browsing test images by disease class,
- comparing Ground Truth, Single-Stage, and Two-Stage outputs,
- visualizing detection, cropping, segmentation, and severity computation,
- moving between images using buttons without reopening the dropdown,
- uploading 1 to 5 custom images for inference,
- comparing which pipeline is closer to the ground-truth severity value.

Run the app from the project root:

```bash
cd streamlit_gui
streamlit run app.py
```

## Notes

The figures displayed in this README were copied from the thesis material into the root-level `README/` folder so that the documentation is self-contained and renders correctly on GitHub or local Markdown viewers.
