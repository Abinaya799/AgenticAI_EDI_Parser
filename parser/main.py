from fastapi import FastAPI
from router_parse import router as parse_router
from router_health import router as health_router

app = FastAPI(title="EDI 210 Parser", version="1.0.0")

# Register routes
app.include_router(parse_router, prefix="/v1/edi210")
app.include_router(health_router)
