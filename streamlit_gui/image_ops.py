from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from data import DatasetSample


RGBImage = np.ndarray
BoolMask = np.ndarray

LEAF_CLASSES = {0, 2, 3}
LESION_CLASSES = {1, 4}
DETECTION_CONF = 0.25
SEGMENTATION_CONF = 0.10
PADDING_RATIO = 0.30


@dataclass(frozen=True)
class ScenarioResult:
    leaf_mask: BoolMask
    lesion_mask: BoolMask
    overlay: RGBImage
    severity: float
    status: str = "OK"


@dataclass(frozen=True)
class TwoStageResult:
    bbox: tuple[int, int, int, int]
    crop_bbox: tuple[int, int, int, int]
    bbox_image: RGBImage
    crop_image: RGBImage
    leaf_mask: BoolMask
    lesion_mask: BoolMask
    overlay: RGBImage
    severity: float
    detection_found: bool
    status: str = "OK"


def calculate_severity(leaf_mask: BoolMask, lesion_mask: BoolMask) -> float:
    leaf_pixels = int(np.count_nonzero(leaf_mask))
    if leaf_pixels == 0:
        return 0.0
    lesion_pixels = int(np.count_nonzero(lesion_mask & leaf_mask))
    return (lesion_pixels / leaf_pixels) * 100.0


def load_image_from_path(path: str | Path) -> RGBImage:
    image = Image.open(path).convert("RGB")
    return np.asarray(image)


def build_demo_case(sample: DatasetSample, model_od: Any, model_seg: Any) -> dict:
    original = load_image_from_path(sample.image_path)
    gt_leaf, gt_lesion = load_gt_masks(sample.label_path, original.shape[:2])

    gt = ScenarioResult(
        leaf_mask=gt_leaf,
        lesion_mask=gt_lesion,
        overlay=overlay_masks(original, gt_leaf, gt_lesion, reference=True),
        severity=calculate_severity(gt_leaf, gt_lesion),
        status="GT dari YOLO polygon label" if sample.label_path.exists() else "Label tidak ditemukan",
    )

    single_leaf, single_lesion, single_status = predict_segmentation_masks(original, model_seg)
    single = ScenarioResult(
        leaf_mask=single_leaf,
        lesion_mask=single_lesion,
        overlay=overlay_masks(original, single_leaf, single_lesion),
        severity=calculate_severity(single_leaf, single_lesion),
        status=single_status,
    )

    two_stage = run_two_stage_pipeline(original, model_od, model_seg)

    return {
        "sample": sample,
        "original": original,
        "gt": gt,
        "single": single,
        "two_stage": two_stage,
    }


def load_gt_masks(label_path: Path, shape: tuple[int, int]) -> tuple[BoolMask, BoolMask]:
    height, width = shape
    leaf_mask = np.zeros((height, width), dtype=bool)
    lesion_mask = np.zeros((height, width), dtype=bool)
    if not label_path.exists():
        return leaf_mask, lesion_mask

    for raw_line in label_path.read_text(encoding="utf-8").splitlines():
        parts = raw_line.strip().split()
        if len(parts) < 7:
            continue
        class_id = int(float(parts[0]))
        coords = [float(value) for value in parts[1:]]
        points = []
        for x_norm, y_norm in zip(coords[0::2], coords[1::2]):
            x = int(np.clip(round(x_norm * width), 0, width - 1))
            y = int(np.clip(round(y_norm * height), 0, height - 1))
            points.append((x, y))

        polygon_mask = polygon_to_mask(points, (height, width))
        if class_id in LEAF_CLASSES:
            leaf_mask |= polygon_mask
        elif class_id in LESION_CLASSES:
            lesion_mask |= polygon_mask

    return leaf_mask, lesion_mask & leaf_mask


def predict_segmentation_masks(image: RGBImage, model_seg: Any) -> tuple[BoolMask, BoolMask, str]:
    height, width = image.shape[:2]
    leaf_mask = np.zeros((height, width), dtype=bool)
    lesion_mask = np.zeros((height, width), dtype=bool)

    result = model_seg(image, verbose=False, conf=SEGMENTATION_CONF)[0]
    if result.masks is None:
        return leaf_mask, lesion_mask, "Tidak ada mask segmentasi"

    polygons = result.masks.xy
    classes = result.boxes.cls.cpu().numpy().astype(int)
    instance_masks = [polygon_to_mask(poly, (height, width)) for poly in polygons]

    leaf_indices = [i for i, class_id in enumerate(classes) if class_id in LEAF_CLASSES]
    lesion_indices = [i for i, class_id in enumerate(classes) if class_id in LESION_CLASSES]

    if not leaf_indices and instance_masks:
        # Fallback untuk model yang class id-nya ter-reset: anggap instance terbesar sebagai daun.
        leaf_indices = [int(np.argmax([np.count_nonzero(mask) for mask in instance_masks]))]

    if leaf_indices:
        leaf_areas = [np.count_nonzero(instance_masks[i]) for i in leaf_indices]
        best_leaf_idx = leaf_indices[int(np.argmax(leaf_areas))]
        leaf_mask = instance_masks[best_leaf_idx]

    for idx in lesion_indices:
        lesion_mask |= instance_masks[idx]

    return leaf_mask, lesion_mask & leaf_mask, "OK"


def run_two_stage_pipeline(original: RGBImage, model_od: Any, model_seg: Any) -> TwoStageResult:
    height, width = original.shape[:2]
    bbox = detect_biggest_bbox(original, model_od)
    detection_found = bbox is not None
    if bbox is None:
        bbox = (0, 0, width, height)

    crop_bbox = add_padding_to_bbox(bbox, width, height, PADDING_RATIO)
    x1, y1, x2, y2 = crop_bbox
    crop_image = original[y1:y2, x1:x2].copy()

    bbox_image = original.copy()
    bx1, by1, bx2, by2 = bbox
    draw_rectangle(bbox_image, bx1, by1, bx2, by2, (37, 99, 235), thickness=max(3, width // 220))
    draw_rectangle(bbox_image, x1, y1, x2, y2, (245, 158, 11), thickness=max(2, width // 320))

    leaf_mask, lesion_mask, seg_status = predict_segmentation_masks(crop_image, model_seg)
    overlay = overlay_masks(crop_image, leaf_mask, lesion_mask)
    status = seg_status if detection_found else "OD tidak menemukan box; fallback memakai full image"

    return TwoStageResult(
        bbox=bbox,
        crop_bbox=crop_bbox,
        bbox_image=bbox_image,
        crop_image=crop_image,
        leaf_mask=leaf_mask,
        lesion_mask=lesion_mask,
        overlay=overlay,
        severity=calculate_severity(leaf_mask, lesion_mask),
        detection_found=detection_found,
        status=status,
    )


def detect_biggest_bbox(image: RGBImage, model_od: Any) -> tuple[int, int, int, int] | None:
    result = model_od(image, verbose=False, conf=DETECTION_CONF)[0]
    if result.boxes is None or len(result.boxes) == 0:
        return None

    boxes = result.boxes.xyxy.cpu().numpy()
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    best = boxes[int(np.argmax(areas))]
    height, width = image.shape[:2]
    x1, y1, x2, y2 = best.astype(int).tolist()
    return (
        int(np.clip(x1, 0, width - 1)),
        int(np.clip(y1, 0, height - 1)),
        int(np.clip(x2, 1, width)),
        int(np.clip(y2, 1, height)),
    )


def add_padding_to_bbox(
    bbox: tuple[int, int, int, int],
    image_width: int,
    image_height: int,
    padding_ratio: float,
) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox
    box_width = max(1, x2 - x1)
    box_height = max(1, y2 - y1)
    pad_x = int(box_width * padding_ratio)
    pad_y = int(box_height * padding_ratio)
    return (
        max(0, x1 - pad_x),
        max(0, y1 - pad_y),
        min(image_width, x2 + pad_x),
        min(image_height, y2 + pad_y),
    )


def polygon_to_mask(points: Any, shape: tuple[int, int]) -> BoolMask:
    height, width = shape
    if points is None or len(points) < 3:
        return np.zeros((height, width), dtype=bool)
    normalized_points = [(int(round(float(x))), int(round(float(y)))) for x, y in points]
    image = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(image)
    draw.polygon(normalized_points, outline=1, fill=1)
    return np.asarray(image, dtype=bool)


def overlay_masks(
    image: RGBImage,
    leaf_mask: BoolMask,
    lesion_mask: BoolMask,
    alpha: float = 0.42,
    reference: bool = False,
) -> RGBImage:
    overlay = image.copy()
    leaf_color = np.array([26, 188, 156] if reference else [39, 174, 96], dtype=np.uint8)
    lesion_color = np.array([192, 57, 43] if reference else [214, 48, 49], dtype=np.uint8)

    if np.any(leaf_mask):
        overlay[leaf_mask] = ((1 - alpha) * overlay[leaf_mask] + alpha * leaf_color).astype(np.uint8)
    lesion_pixels = lesion_mask & leaf_mask
    if np.any(lesion_pixels):
        overlay[lesion_pixels] = ((1 - 0.68) * overlay[lesion_pixels] + 0.68 * lesion_color).astype(np.uint8)

    contoured = overlay.copy()
    draw_mask_contour(contoured, leaf_mask, (18, 120, 72), thickness=2)
    draw_mask_contour(contoured, lesion_pixels, (178, 34, 34), thickness=1)
    return contoured


def reference_mask_image(leaf_mask: BoolMask, lesion_mask: BoolMask) -> RGBImage:
    canvas = np.zeros((*leaf_mask.shape, 3), dtype=np.uint8)
    canvas[:] = np.array([245, 247, 250], dtype=np.uint8)
    canvas[leaf_mask] = np.array([46, 204, 113], dtype=np.uint8)
    canvas[lesion_mask & leaf_mask] = np.array([231, 76, 60], dtype=np.uint8)
    draw_mask_contour(canvas, leaf_mask, (22, 100, 62), thickness=2)
    return canvas


def draw_mask_contour(image: RGBImage, mask: BoolMask, color: tuple[int, int, int], thickness: int) -> None:
    if not np.any(mask):
        return
    edge = mask_edge(mask, max(3, thickness * 2 + 1))
    image[edge] = np.array(color, dtype=np.uint8)


def mask_edge(mask: BoolMask, kernel_size: int) -> BoolMask:
    dilated = morph(mask, "dilate", kernel_size)
    eroded = morph(mask, "erode", kernel_size)
    return dilated & ~eroded


def morph(mask: BoolMask, operation: str, kernel_size: int) -> BoolMask:
    radius = kernel_size // 2
    padded = np.pad(mask.astype(bool), radius, mode="constant", constant_values=False)
    shifted_masks = []
    for dy in range(kernel_size):
        for dx in range(kernel_size):
            shifted_masks.append(padded[dy : dy + mask.shape[0], dx : dx + mask.shape[1]])
    stack = np.stack(shifted_masks, axis=0)
    if operation == "erode":
        return np.all(stack, axis=0)
    if operation == "dilate":
        return np.any(stack, axis=0)
    raise ValueError(operation)


def draw_rectangle(
    image: RGBImage,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    image[y1 : min(y1 + thickness, image.shape[0]), x1:x2] = color
    image[max(y2 - thickness, 0) : y2, x1:x2] = color
    image[y1:y2, x1 : min(x1 + thickness, image.shape[1])] = color
    image[y1:y2, max(x2 - thickness, 0) : x2] = color
