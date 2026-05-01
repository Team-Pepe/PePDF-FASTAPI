from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_word_to_pdf_success() -> None:
    with patch(
        "app.module.convert_tools.word_to_pdf.routes.convert_word_to_pdf",
        return_value=b"%PDF-1.4\nfake pdf\n",
    ):
        response = client.post(
            "/convert-tools/word-to-pdf",
            files=[("file", ("report.docx", b"fake-docx-bytes", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_word_to_pdf_rejects_invalid_file() -> None:
    response = client.post(
        "/convert-tools/word-to-pdf",
        files=[("file", ("notes.txt", b"hello", "text/plain"))],
    )

    assert response.status_code == 400