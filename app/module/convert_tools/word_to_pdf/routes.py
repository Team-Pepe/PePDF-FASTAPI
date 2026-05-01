from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from .schemas import UploadedWordDocument
from .services import convert_word_to_pdf


router = APIRouter(prefix="/convert-tools", tags=["convert-tools"])

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


@router.post("/word-to-pdf", status_code=status.HTTP_200_OK)
async def word_to_pdf(file: Annotated[UploadFile, File(...)]) -> Response:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A Word document is required")

    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word document exceeds 20MB")

    uploaded = UploadedWordDocument(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        data=raw,
    )

    try:
        pdf = convert_word_to_pdf(uploaded)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    output_name = f"{file.filename.rsplit('.', 1)[0]}.pdf" if "." in file.filename else "converted.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )