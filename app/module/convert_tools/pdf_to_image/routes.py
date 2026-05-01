from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import Response
from typing import Annotated

from .schemas import UploadedPDF
from .services import create_images_from_pdf

router = APIRouter(prefix="/convert-tools", tags=["convert-tools"])

# Configuration
MAX_FILES = 5
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/pdf-to-image", status_code=status.HTTP_200_OK)
async def pdf_to_image(files: Annotated[list[UploadFile], File(...)]) -> Response:
    """
    Convert PDF pages to individual PNG images.
    
    - **files**: PDF files to convert (max 5 files, 20MB each)
    - Returns: ZIP file containing all extracted pages as PNG images
    
    File naming: page_0001.png, page_0002.png, etc.
    DPI: 200 (good balance between quality and file size)
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one PDF is required"
        )
    
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_FILES} files allowed"
        )
    
    uploaded_pdfs: list[UploadedPDF] = []
    
    # Read and validate all files (don't catch HTTPException here)
    for file in files:
        # Validate content type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' is not a PDF. Only PDF files are accepted."
            )
        
        # Validate file size
        file_data = await file.read()
        if len(file_data) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' exceeds {MAX_FILE_SIZE_MB}MB limit"
            )
        
        uploaded_pdfs.append(UploadedPDF(
            filename=file.filename or "upload.pdf",
            content_type=file.content_type or "application/pdf",
            data=file_data
        ))
    
    try:
        # Convert PDFs to images (returns ZIP)
        zip_data = create_images_from_pdf(uploaded_pdfs)
        
        # Return ZIP file as response
        return Response(
            content=zip_data,
            media_type="application/zip",
            headers={"Content-Disposition": 'attachment; filename="pdf-pages.zip"'},
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        ) from e
