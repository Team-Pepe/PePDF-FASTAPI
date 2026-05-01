from pathlib import Path
from unittest.mock import patch

import pytest

from app.module.convert_tools.pdf_to_word.schemas import UploadedPdfDocument
from app.module.convert_tools.pdf_to_word.services import convert_pdf_to_word


def test_convert_pdf_to_word_returns_docx() -> None:
    document = UploadedPdfDocument(
        filename="report.pdf",
        content_type="application/pdf",
        data=b"%PDF-1.4 fake",
    )

    def fake_converter(source_path: str):
        source = Path(source_path)

        class _FakeConverter:
            def convert(self, output_path: str, start=0, end=None):  # noqa: ARG002
                output = Path(output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"PK\x03\x04 fake-docx")

            def close(self):
                return None

        assert source.name == "report.pdf"
        return _FakeConverter()

    with patch("app.module.convert_tools.pdf_to_word.services.Converter", side_effect=fake_converter):
        docx = convert_pdf_to_word(document)

    assert docx.startswith(b"PK")


def test_convert_pdf_to_word_rejects_invalid_type() -> None:
    document = UploadedPdfDocument(filename="notes.txt", content_type="text/plain", data=b"hello")

    with pytest.raises(ValueError):
        convert_pdf_to_word(document)
