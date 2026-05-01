from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from .services import encrypt_pdf, unlock_pdf, set_permissions_pdf

router = APIRouter()


@router.post("/tool-suites/protect/encrypt")
async def encrypt_endpoint(file: UploadFile = File(...), password: str = Form(...)):
    try:
        content = await file.read()
        output_stream = encrypt_pdf(content, password)
        return StreamingResponse(
            output_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=encrypted_{file.filename}"
            },
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal server error while encrypting PDF"
        )


@router.post("/tool-suites/protect/permissions")
async def permissions_endpoint(
    file: UploadFile = File(...),
    owner_password: str = Form(...),
    user_password: Optional[str] = Form(""),
    block_print: Optional[str] = Form("false"),
    block_print_high_res: Optional[str] = Form("false"),
    block_modify: Optional[str] = Form("false"),
    block_copy: Optional[str] = Form("false"),
    block_annotate: Optional[str] = Form("false"),
    block_fill_forms: Optional[str] = Form("false"),
    block_assemble: Optional[str] = Form("false"),
):
    try:
        content = await file.read()

        # Convertir strings 'true'/'false' a booleanos
        print_blocked = str(block_print).lower() == "true"
        print_high_res_blocked = str(block_print_high_res).lower() == "true"
        modify_blocked = str(block_modify).lower() == "true"
        copy_blocked = str(block_copy).lower() == "true"
        annotate_blocked = str(block_annotate).lower() == "true"
        fill_forms_blocked = str(block_fill_forms).lower() == "true"
        assemble_blocked = str(block_assemble).lower() == "true"

        # Si el user_password llega como 'null' o 'undefined' o None
        actual_user_password = (
            user_password
            if user_password and user_password not in ["null", "undefined"]
            else ""
        )

        output_stream = set_permissions_pdf(
            file_bytes=content,
            owner_password=owner_password,
            user_password=actual_user_password,
            block_print=print_blocked,
            block_modify=modify_blocked,
            block_copy=copy_blocked,
            block_annotate=annotate_blocked,
            block_fill_forms=fill_forms_blocked,
            block_assemble=assemble_blocked,
            block_print_high_res=print_high_res_blocked,
        )

        return StreamingResponse(
            output_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=permissions_{file.filename}"
            },
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import logging

        logging.error(f"Error in permissions_endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while setting PDF permissions: {str(e)}",
        )


@router.post("/tool-suites/protect/unlock")
async def unlock_endpoint(file: UploadFile = File(...), password: str = Form(...)):
    try:
        content = await file.read()
        output_stream = unlock_pdf(content, password)
        return StreamingResponse(
            output_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=unlocked_{file.filename}"
            },
        )
    except ValueError as ve:
        # Podríamos devolver 401 para "Contraseña incorrecta", pero 400 es genéricamente seguro
        status_code = 401 if "Contraseña incorrecta" in str(ve) else 400
        raise HTTPException(status_code=status_code, detail=str(ve))
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal server error while unlocking PDF"
        )
