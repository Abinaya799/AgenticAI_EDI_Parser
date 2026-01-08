from fastapi import APIRouter, Request
from fastapi.responses import Response


router = APIRouter()

@router.get("/healthz")
def healthz():
    return {"status": "ok"}

@router.get("/readyz")
def readyz(request: Request):
    """
    Readiness probe: ensures profiles are loaded.
    """
    if not getattr(request.app.state, "is_ready", False):
        return Response(status_code=503)
    return {"status": "ready"}
