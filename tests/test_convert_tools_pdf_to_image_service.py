import io
import zipfile

import fitz
import pytest

from app.module.convert_tools.pdf_to_image.schemas import UploadedPDF
from app.module.convert_tools.pdf_to_image.services import create_images_from_pdf


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


def test_create_images_from_pdf_returns_zip(sample_pdf):
    """Test that PDF to images conversion returns valid ZIP."""
    pdf = UploadedPDF(
        filename="test.pdf",
        content_type="application/pdf",
        data=sample_pdf
    )
    
    zip_data = create_images_from_pdf([pdf])
    
    # Verify it's a valid ZIP
    zip_buffer = io.BytesIO(zip_data)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        file_list = zip_file.namelist()
        assert len(file_list) == 2
        assert "page_0001.png" in file_list
        assert "page_0002.png" in file_list


def test_create_images_from_pdf_rejects_invalid_type():
    """Test that non-PDF content type raises ValueError."""
    pdf = UploadedPDF(
        filename="test.txt",
        content_type="text/plain",
        data=b"Not a PDF"
    )
    
    with pytest.raises(ValueError) as exc_info:
        create_images_from_pdf([pdf])
    
    assert "Unsupported file type" in str(exc_info.value)


def test_create_images_from_pdf_multiple_pdfs(sample_pdf):
    """Test conversion of multiple PDFs in one batch."""
    pdfs = [
        UploadedPDF(
            filename="test1.pdf",
            content_type="application/pdf",
            data=sample_pdf
        ),
        UploadedPDF(
            filename="test2.pdf",
            content_type="application/pdf",
            data=sample_pdf
        ),
    ]
    
    zip_data = create_images_from_pdf(pdfs)
    
    # Should have 4 pages total (2 PDFs × 2 pages each)
    zip_buffer = io.BytesIO(zip_data)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        file_list = zip_file.namelist()
        assert len(file_list) == 4
        assert "page_0001.png" in file_list
        assert "page_0004.png" in file_list
