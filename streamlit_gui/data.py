from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
DATASET_DIR = APP_DIR / "dataset"
IMAGE_DIR = DATASET_DIR / "images"
LABEL_DIR = DATASET_DIR / "labels"

DISEASE_CLASSES = ("Healthy", "Rust", "Frog-eye Leaf Spot")


@dataclass(frozen=True)
class DatasetSample:
    disease_class: str
    image_path: Path
    label_path: Path

    @property
    def sample_id(self) -> str:
        return self.image_path.stem

    @property
    def display_name(self) -> str:
        return self.image_path.name


def infer_disease_class(path: Path) -> str | None:
    name = path.name.lower()
    if "healthy" in name:
        return "Healthy"
    if "rust" in name:
        return "Rust"
    if "frog_eye_leaf_spot" in name or "frog-eye" in name or "frogeye" in name:
        return "Frog-eye Leaf Spot"
    return None


def discover_samples() -> dict[str, list[DatasetSample]]:
    samples: dict[str, list[DatasetSample]] = {disease_class: [] for disease_class in DISEASE_CLASSES}
    if not IMAGE_DIR.exists():
        return samples

    image_paths = sorted(
        path
        for path in IMAGE_DIR.iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    )
    for image_path in image_paths:
        disease_class = infer_disease_class(image_path)
        if disease_class is None:
            continue
        label_path = LABEL_DIR / f"{image_path.stem}.txt"
        samples[disease_class].append(DatasetSample(disease_class, image_path, label_path))
    return samples


def get_sample_names(disease_class: str) -> list[str]:
    return [sample.display_name for sample in discover_samples()[disease_class]]


def get_sample_by_name(disease_class: str, display_name: str) -> DatasetSample:
    for sample in discover_samples()[disease_class]:
        if sample.display_name == display_name:
            return sample
    raise KeyError(f"Sample '{display_name}' is not available for '{disease_class}'.")
