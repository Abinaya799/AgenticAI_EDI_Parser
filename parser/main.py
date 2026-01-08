from fastapi import FastAPI
from contextlib import asynccontextmanager
from loader import load_profiles
from dotenv import load_dotenv
import os
from router_parse import router as parse_router
from router_health import router as health_router

load_dotenv()
profiles_dir = os.environ.get("PROFILES_PATH", "profiles")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.is_ready = load_profiles(profiles_dir)
    print("Profiles loaded")
    yield


app = FastAPI(title="EDI 210 Parser", version="1.0.0", lifespan=lifespan)
app.include_router(health_router)


# Register routes
app.include_router(parse_router, prefix="/v1/edi210")
app.include_router(health_router)
