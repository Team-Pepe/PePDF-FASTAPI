from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.module.auth import router as auth_router
from app.module.tool_suites.qr_generator import router as qr_router
from app.module.tool_suites.protect import router as protect_router

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
)

# Configure CORS BEFORE other middleware
cors_origins = settings.get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=600,
)

# Include routers
app.include_router(auth_router)
app.include_router(qr_router, prefix="/api")
app.include_router(protect_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "PePDF API", "version": settings.api_version}


@app.get("/health")
def health_check():
    return {"status": "ok"}
