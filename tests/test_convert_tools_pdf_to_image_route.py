import io
import zipfile
from pathlib import Path

import fitz
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def sample_pdf():
    """Create a simple PDF with 2 pages for testing."""
    pdf_doc = fitz.open()
    for i in range(2):
        page = pdf_doc.new_page()
        page.insert_text((50, 50), f"Page {i + 1}")
    
    pdf_bytes = pdf_doc.write()
    pdf_doc.close()
    return pdf_bytes


def test_pdf_to_image_success(sample_pdf):
    """Test successful PDF to image conversion."""
    files = [
        ("files", ("test.pdf", io.BytesIO(sample_pdf), "application/pdf")),
    ]
    
    response = client.post("/convert-tools/pdf-to-image", files=files)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.headers["content-disposition"] == 'attachment; filename="pdf-pages.zip"'
    
    # Verify ZIP contents
    zip_buffer = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        file_list = zip_file.namelist()
        assert len(file_list) == 2
        assert all(name.endswith('.png') for name in file_list)
        assert "page_0001.png" in file_list
        assert "page_0002.png" in file_list


def test_pdf_to_image_rejects_invalid_file():
    """Test that non-PDF files are rejected."""
    files = [
        ("files", ("test.txt", io.BytesIO(b"Not a PDF"), "text/plain")),
    ]
    
    response = client.post("/convert-tools/pdf-to-image", files=files)
    
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_pdf_to_image_no_files():
    """Test that at least one file is required."""
    response = client.post("/convert-tools/pdf-to-image", files=[])
    
    # FastAPI returns 422 for missing required parameters
    assert response.status_code == 422


def test_pdf_to_image_exceeds_max_files(sample_pdf):
    """Test that max 5 files are allowed."""
    files = [
        ("files", ("test1.pdf", io.BytesIO(sample_pdf), "application/pdf")),
        ("files", ("test2.pdf", io.BytesIO(sample_pdf), "application/pdf")),
        ("files", ("test3.pdf", io.BytesIO(sample_pdf), "application/pdf")),
        ("files", ("test4.pdf", io.BytesIO(sample_pdf), "application/pdf")),
        ("files", ("test5.pdf", io.BytesIO(sample_pdf), "application/pdf")),
        ("files", ("test6.pdf", io.BytesIO(sample_pdf), "application/pdf")),  # 6th file
    ]
    
    response = client.post("/convert-tools/pdf-to-image", files=files)
    
    assert response.status_code == 400
    assert "Maximum 5 files allowed" in response.json()["detail"]
