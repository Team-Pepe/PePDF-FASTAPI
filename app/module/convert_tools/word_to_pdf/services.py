from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from .schemas import UploadedWordDocument

SUPPORTED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}
SUPPORTED_EXTENSIONS = {".doc", ".docx"}


def _ensure_supported_word(document: UploadedWordDocument) -> None:
    suffix = Path(document.filename).suffix.lower()
    if document.content_type not in SUPPORTED_CONTENT_TYPES and suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only Word documents (.doc, .docx) are supported")


def _find_soffice() -> str:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("LibreOffice is not installed in the execution environment")
    return soffice


def convert_word_to_pdf(document: UploadedWordDocument) -> bytes:
    _ensure_supported_word(document)

    soffice = _find_soffice()
    source_name = Path(document.filename).name or "document.docx"
    source_stem = Path(source_name).stem or "document"

    with tempfile.TemporaryDirectory(prefix="word-to-pdf-") as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        profile_dir = temp_path / "profile"

        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        profile_dir.mkdir(parents=True, exist_ok=True)

        source_path = input_dir / source_name
        source_path.write_bytes(document.data)

        command = [
            soffice,
            "--headless",
            "--nologo",
            "--nolockcheck",
            "--nodefault",
            "--nofirststartwizard",
            f"-env:UserInstallation={profile_dir.as_uri()}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(source_path),
        ]

        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=180)
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip() or "Unknown LibreOffice error"
            raise RuntimeError(f"Word conversion failed: {stderr}")

        pdf_path = output_dir / f"{source_stem}.pdf"
        if not pdf_path.exists():
            candidates = list(output_dir.glob("*.pdf"))
            if len(candidates) != 1:
                raise RuntimeError("LibreOffice did not produce a PDF output")
            pdf_path = candidates[0]

        return pdf_path.read_bytes()