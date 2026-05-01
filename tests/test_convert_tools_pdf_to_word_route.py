from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_pdf_to_word_success() -> None:
    with patch(
        "app.module.convert_tools.pdf_to_word.routes.convert_pdf_to_word",
        return_value=b"PK\x03\x04 fake-docx",
    ):
        response = client.post(
            "/convert-tools/pdf-to-word",
            files=[("file", ("report.pdf", b"%PDF-1.4 fake", "application/pdf"))],
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert response.content.startswith(b"PK")


def test_pdf_to_word_rejects_invalid_file() -> None:
    response = client.post(
        "/convert-tools/pdf-to-word",
        files=[("file", ("notes.txt", b"hello", "text/plain"))],
    )

    assert response.status_code == 400
