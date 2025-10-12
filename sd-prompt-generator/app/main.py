from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db, create_tables
from app.api.routes import router
import time

app = FastAPI(
    title="SD Prompt Generator",
    description="Сервис для генерации промптов Stable Diffusion из литературных сцен",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "SD Prompt Generator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}
