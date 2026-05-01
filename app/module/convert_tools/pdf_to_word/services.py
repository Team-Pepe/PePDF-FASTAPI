from __future__ import annotations

import tempfile
from pathlib import Path

from pdf2docx import Converter

from .schemas import UploadedPdfDocument

SUPPORTED_CONTENT_TYPES = {"application/pdf"}
SUPPORTED_EXTENSIONS = {".pdf"}


def _ensure_supported_pdf(document: UploadedPdfDocument) -> None:
    suffix = Path(document.filename).suffix.lower()
    if document.content_type not in SUPPORTED_CONTENT_TYPES and suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only PDF files are supported")


def convert_pdf_to_word(document: UploadedPdfDocument) -> bytes:
    _ensure_supported_pdf(document)
    source_name = Path(document.filename).name or "document.pdf"
    source_stem = Path(source_name).stem or "document"

    with tempfile.TemporaryDirectory(prefix="pdf-to-word-") as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"

        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        source_path = input_dir / source_name
        source_path.write_bytes(document.data)

        docx_path = output_dir / f"{source_stem}.docx"

        converter = Converter(str(source_path))
        try:
            converter.convert(str(docx_path), start=0, end=None)
        except Exception as exc:
            raise RuntimeError(f"PDF conversion failed: {exc}") from exc
        finally:
            converter.close()

        if not docx_path.exists():
            raise RuntimeError("pdf2docx did not produce a DOCX output")

        return docx_path.read_bytes()
