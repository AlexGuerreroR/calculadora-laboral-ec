# app/tools/calcular_decimos.py · generado en el taller del 28-oct-2026 · Grupo 7
from decimal import Decimal
from pydantic import BaseModel, Field
from app.config import PARAMETROS   # lee config/parametros.yaml


class CalcularDecimosIn(BaseModel):
    meses_trabajados: int = Field(ge=1, le=12, description="meses trabajados")
    region: str = Field(description="region")


def calcular_decimos(datos: CalcularDecimosIn) -> dict:
    """Calcula décimos mediante codigo en Python.."""
    salario_basico_unificado = PARAMETROS["salario_basico_unificado"]   # Porque Cambia según el año.
    # TODO: implementación determinista (misma entrada → mismo resultado).
    #       Use Decimal para dinero y los valores de PARAMETROS, nunca números fijos.
    valor = ...
    return {"valor": valor, "fuente": "TODO: artículo o documento"}


ESQUEMA = {
    "type": "function",
    "function": {
        "name": "calcular_decimos",
        "description": "Calcula décimos mediante codigo en Python.",
        "parameters": CalcularDecimosIn.model_json_schema(),
    },
}
