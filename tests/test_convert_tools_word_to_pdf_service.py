from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from app.module.convert_tools.word_to_pdf.schemas import UploadedWordDocument
from app.module.convert_tools.word_to_pdf.services import convert_word_to_pdf


def test_convert_word_to_pdf_returns_pdf() -> None:
    document = UploadedWordDocument(
        filename="report.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        data=b"fake-docx-bytes",
    )

    def fake_run(command, check, capture_output, text, timeout):
        outdir = Path(command[command.index("--outdir") + 1])
        source_path = Path(command[-1])
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / f"{source_path.stem}.pdf").write_bytes(b"%PDF-1.4\nfake pdf\n")
        return MagicMock(returncode=0, stdout="", stderr="")

    with patch("app.module.convert_tools.word_to_pdf.services.shutil.which", return_value="soffice"), patch(
        "app.module.convert_tools.word_to_pdf.services.subprocess.run",
        side_effect=fake_run,
    ):
        pdf = convert_word_to_pdf(document)

    assert pdf.startswith(b"%PDF")


def test_convert_word_to_pdf_rejects_invalid_type() -> None:
    document = UploadedWordDocument(filename="notes.txt", content_type="text/plain", data=b"hello")

    with pytest.raises(ValueError):
        convert_word_to_pdf(document)