from typing import Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.config import get_settings
from app.database import Base, engine
from app.routers import accounts, auth, scan


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        detail = getattr(e, "orig", None) or str(e)
        raise RuntimeError(
            "Cannot connect to PostgreSQL. From the repo root run `docker compose up -d`, "
            "or point DATABASE_URL in backend/.env at a running Postgres instance. "
            f"Details: {detail!r}"
        ) from e
    yield


app = FastAPI(title="Zenith Privacy API", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(accounts.router)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
