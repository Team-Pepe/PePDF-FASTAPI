from fastapi import FastAPI
from app.config import settings
from app.module.auth import router as auth_router

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
)

# Include routers
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "PePDF API", "version": settings.api_version}


@app.get("/health")
def health_check():
    return {"status": "ok"}