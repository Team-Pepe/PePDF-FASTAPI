import tempfile
from pathlib import Path
from typing import List

import fitz  # PyMuPDF

from .schemas import UploadedPDF


def _ensure_is_pdf(content_type: str) -> None:
    """Validate that the file is a PDF."""
    if content_type != "application/pdf":
        raise ValueError(f"Unsupported file type: {content_type}. Only PDF files are accepted.")


def create_images_from_pdf(pdfs: List[UploadedPDF], dpi: int = 200) -> bytes:
    """
    Convert PDF pages to PNG images and return as a ZIP file.
    
    Args:
        pdfs: List of UploadedPDF objects containing PDF data
        dpi: Resolution in dots per inch (default 200 for balance between quality and size)
    
    Returns:
        ZIP file bytes containing all extracted images
    
    Raises:
        ValueError: If PDF is invalid or format not supported
    """
    import zipfile
    import io
    
    # Validate all PDFs first
    for pdf in pdfs:
        _ensure_is_pdf(pdf.content_type)
    
    zip_buffer = io.BytesIO()
    image_index = 1
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for pdf in pdfs:
                pdf_document = None
                try:
                    # Open PDF from bytes
                    pdf_document = fitz.open(stream=pdf.data, filetype="pdf")
                    
                    # Extract pages as images
                    for page_num in range(len(pdf_document)):
                        page = pdf_document[page_num]
                        
                        # Render page to image at specified DPI
                        # DPI scaling: 72 is default, so multiply by (dpi/72)
                        zoom = dpi / 72.0
                        matrix = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=matrix, alpha=False)
                        
                        # Save as PNG to bytes
                        image_data = pix.tobytes(output="png")
                        
                        # Generate filename (e.g., page_001.png, page_002.png, etc.)
                        filename = f"page_{image_index:04d}.png"
                        zip_file.writestr(filename, image_data)
                        image_index += 1
                        
                except Exception as e:
                    raise ValueError(f"Failed to process PDF '{pdf.filename}': {str(e)}")
                finally:
                    if pdf_document:
                        pdf_document.close()
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
        
    except Exception as e:
        raise ValueError(f"Failed to create ZIP archive: {str(e)}")
