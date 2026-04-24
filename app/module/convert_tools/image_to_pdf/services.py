from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Iterable

import img2pdf
from PIL import Image, ImageOps


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
}


@dataclass(slots=True)
class UploadedImage:
    filename: str
    content_type: str
    data: bytes


def _ensure_is_supported_image(image: UploadedImage) -> None:
    if image.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported file type for '{image.filename}'")

    if not image.data:
        raise ValueError(f"File '{image.filename}' is empty")


def _normalize_image(source: Path) -> Path:
    """
    Normalize alpha channel cases to avoid conversion errors.
    Returns the final path that should be sent to img2pdf.
    """
    with Image.open(source) as img:
        img = ImageOps.exif_transpose(img)
        mode = img.mode

        if mode not in {"RGBA", "LA", "P"}:
            return source

        bg = Image.new("RGB", img.size, (255, 255, 255))
        if mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1])

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            normalized_path = Path(tmp.name)
        bg.save(normalized_path, format="PNG")

    return normalized_path


def create_pdf_from_images(images: Iterable[UploadedImage]) -> bytes:
    temp_paths: list[Path] = []
    normalized_paths: list[Path] = []

    try:
        for image in images:
            _ensure_is_supported_image(image)
            suffix = Path(image.filename).suffix or ".img"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(image.data)
                source_path = Path(tmp.name)
            temp_paths.append(source_path)

            normalized_path = _normalize_image(source_path)
            normalized_paths.append(normalized_path)

        if not normalized_paths:
            raise ValueError("At least one image is required")

        return img2pdf.convert([str(path) for path in normalized_paths])
    except img2pdf.ImageOpenError as exc:
        raise ValueError("One or more files are not valid images") from exc
    finally:
        for path in normalized_paths:
            if path.exists() and path not in temp_paths:
                path.unlink(missing_ok=True)
        for path in temp_paths:
            path.unlink(missing_ok=True)
