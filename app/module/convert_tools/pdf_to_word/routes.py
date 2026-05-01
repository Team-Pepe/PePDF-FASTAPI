from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from .schemas import UploadedPdfDocument
from .services import convert_pdf_to_word


router = APIRouter(prefix="/convert-tools", tags=["convert-tools"])

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


@router.post("/pdf-to-word", status_code=status.HTTP_200_OK)
async def pdf_to_word(file: Annotated[UploadFile, File(...)]) -> Response:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A PDF document is required")

    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PDF document exceeds 20MB")

    uploaded = UploadedPdfDocument(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        data=raw,
    )

    try:
        docx = convert_pdf_to_word(uploaded)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    output_name = f"{file.filename.rsplit('.', 1)[0]}.docx" if "." in file.filename else "converted.docx"
    return Response(
        content=docx,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )
