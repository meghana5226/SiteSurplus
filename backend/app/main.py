import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import listings, requirements, matching, transactions, reuse, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ConstructionWaste Exchange API",
    description="Match surplus construction material between sites: listings, requirements, "
                "a deterministic weighted matching engine, logistics estimation, and a "
                "transaction lifecycle through to reuse confirmation.",
    version="1.0.0",
)

# CORS: allow the React frontend (dev server + deployed Vercel URL)
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(listings.router)
app.include_router(requirements.router)
app.include_router(matching.router)
app.include_router(transactions.router)
app.include_router(reuse.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"service": "ConstructionWaste Exchange API", "status": "ok", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
