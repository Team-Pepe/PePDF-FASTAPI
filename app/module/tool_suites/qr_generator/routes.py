from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from .schemas import QrBasicRequest, QrScanResult
from . import services

router = APIRouter(prefix="/tool-suites/qr-generator", tags=["QR Generator"])


@router.post("/basic")
async def create_basic_qr(request: QrBasicRequest):
    img_io = services.generate_basic_qr(data=request.data, size=request.size)
    return StreamingResponse(img_io, media_type="image/png")


@router.post("/advanced")
async def create_advanced_qr(
    data: str = Form(...),
    error_correction: str = Form("H"),
    logo_shape: str = Form("circular"),
    logo_size_percent: int = Form(30),
    white_margin: int = Form(3),
    logo: Optional[UploadFile] = File(None),
):
    logo_bytes = None
    if logo and logo.filename:
        logo_bytes = await logo.read()

    img_io = services.generate_advanced_qr(
        data=data,
        error_correction=error_correction,
        logo_shape=logo_shape,
        logo_size_percent=logo_size_percent,
        white_margin=white_margin,
        logo_bytes=logo_bytes,
    )
    return StreamingResponse(img_io, media_type="image/png")


@router.post("/scan", response_model=QrScanResult)
async def scan_qr(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    image_bytes = await file.read()
    decoded_value = services.decode_qr(image_bytes)

    if not decoded_value:
        raise HTTPException(
            status_code=400, detail="Could not decode QR code from image"
        )

    return QrScanResult(decoded_value=decoded_value, source=file.filename)
