from fastapi import APIRouter
from app.module.convert_tools.image_to_pdf.routes import router as image_to_pdf_router
from app.module.convert_tools.pdf_to_image.routes import router as pdf_to_image_router

# Combine both routers
router = APIRouter()
router.include_router(image_to_pdf_router)
router.include_router(pdf_to_image_router)

__all__ = ["router"]
