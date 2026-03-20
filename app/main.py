from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.module.auth import router as auth_router

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "PePDF API", "version": settings.api_version}


@app.get("/health")
def health_check():
    return {"status": "ok"}