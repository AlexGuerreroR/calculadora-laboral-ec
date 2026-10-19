"""Punto de entrada del backend. Semana 1: solo el endpoint de salud."""
from fastapi import FastAPI

app = FastAPI(title="Calculadora laboral EC", version="0.1.0")


@app.get("/health")
def health() -> dict:
    """Permite comprobar que el servicio está en línea."""
    return {"status": "ok"}
