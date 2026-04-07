from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db

app = FastAPI(
    title="BRVM Tracker API",
    description="API Gateway pour les données de la Bourse Régionale des Valeurs Mobilières (UEMOA)",
    version="1.0.0"
)

# Configuration CORS pour autoriser le frontend Next.js en local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import market, actions, macro

app.include_router(market.router, prefix="/api/v1")
app.include_router(actions.router, prefix="/api/v1")
app.include_router(macro.router, prefix="/api/v1/macro", tags=["Macro"])

@app.get("/health", tags=["System"])
async def health_check():
    """Route de vérification de santé pour s'assurer que l'API est en ligne."""
    return {"status": "ok", "service": "BRVM API Gateway"}
