"""Punto de entrada del backend · Calculadora Laboral EC (caso 07).

Ejecutar:  uvicorn app.main:app --reload     y abrir http://127.0.0.1:8000/docs
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()  # lee el .env local (la clave nunca está en el código)

from app.errores import registrar_manejadores  # noqa: E402
from app.routers import calculos, explicar, agente, resumen  # noqa: E402

app = FastAPI(
    title="Calculadora Laboral EC",
    version="0.2.0",
    description="El código calcula; la IA explica. Caso 07 · Grupo 7 · UNIANDES.",
)

# CORS cerrado: solo el origen del frontend, nunca «*»
origenes = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origenes, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

registrar_manejadores(app)
app.include_router(calculos.router)
app.include_router(explicar.router)
app.include_router(agente.router)
app.include_router(resumen.router)


@app.get("/health")
def health() -> dict:
    """Permite comprobar que el servicio está en línea."""
    return {"status": "ok"}


# Frontend propio (HTML + JavaScript), servido por el mismo backend: una sola URL y sin CORS
# abierto. Se monta al final para que /calculos, /explicar, /health y /docs tengan prioridad.
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
