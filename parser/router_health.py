from fastapi import APIRouter
from parser.loader import load_profiles
import os

router = APIRouter()

@router.get("/healthz")
def healthz():
    return {"status": "ok"}

@router.get("/readyz")
def readyz():
    """
    Readiness probe: ensures profiles are loaded.
    """
    profiles_dir = os.environ.get("PROFILES_PATH", "profiles")
    
    if load_profiles(profiles_dir):
        return {"status": "ready"}
    return {"status": "not_ready"}, 503
