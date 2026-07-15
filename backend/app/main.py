"""
FastAPI application entrypoint.

Mounts API routers and configures CORS for the Vite dev server. No database
setup here -- session state lives entirely in app/session_store.py (in-memory).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.api.routes import upload, transactions, subscriptions, insights
app = FastAPI(
    title="SpendSense API",
    description="Transaction categorization, subscription detection, and spending insights engine.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(transactions.router, prefix="/api", tags=["transactions"])
app.include_router(subscriptions.router, prefix="/api", tags=["subscriptions"])
app.include_router(insights.router, prefix="/api", tags=["insights"])

@app.get("/api/health")
def health_check():
    """Simple liveness check -- also useful for confirming the frontend can reach the backend."""
    return {"status": "ok"}