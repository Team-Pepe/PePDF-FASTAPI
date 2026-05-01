from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.module.convert_tools.image_to_pdf.services import UploadedImage, create_pdf_from_images


router = APIRouter(prefix="/convert-tools", tags=["convert-tools"])

MAX_FILES = 10
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024


@router.post("/image-to-pdf", status_code=status.HTTP_200_OK)
async def image_to_pdf(files: Annotated[list[UploadFile], File(...)]) -> Response:
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one image is required")

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A maximum of {MAX_FILES} files is allowed",
        )

    images: list[UploadedImage] = []
    for file in files:
        raw = await file.read()
        if len(raw) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' exceeds {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB",
            )

        images.append(
            UploadedImage(
                filename=file.filename or "upload",
                content_type=file.content_type or "application/octet-stream",
                data=raw,
            )
        )

    try:
        pdf = create_pdf_from_images(images)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="images-converted.pdf"'},
    )
