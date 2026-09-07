"""Settings router."""
from fastapi import APIRouter, Depends
from app.api.v1.auth import get_current_user, require_role
from app.core.config import settings
from app.models.user import User

router = APIRouter()

@router.get("/system")
async def get_system_settings(current_user: User = Depends(require_role("admin"))):
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "app_env": settings.APP_ENV,
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.GEMINI_MODEL if settings.AI_PROVIDER == "gemini" else settings.AI_PROVIDER,
        "upload_dir": settings.UPLOAD_DIR,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
        "job_backend": settings.JOB_BACKEND,
        "enable_ml_models": settings.ENABLE_ML_MODELS,
        "cors_origins": settings.CORS_ORIGINS,
    }

@router.get("/ai-provider")
async def get_ai_provider_status(current_user: User = Depends(get_current_user)):
    from app.extraction.provider_factory import get_provider
    provider = get_provider()
    available = await provider.is_available()
    return {
        "provider": provider.name,
        "model_version": provider.model_version,
        "available": available,
    }
