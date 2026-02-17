from fastapi import FastAPI
from app.api.imports import router as import_router
from app.api.snapshots import router as snapshot_router
from app.core.database import Base, engine
from app.api.portfolio import router as portfolio_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="XTB Portfolio Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(import_router, prefix="/imports")
app.include_router(snapshot_router)
app.include_router(portfolio_router)

@app.get("/health")
def health():
    return {"status": "ok"}

Base.metadata.create_all(bind=engine)