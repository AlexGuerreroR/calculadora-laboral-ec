"""Esquemas (Pydantic) del caso 07 · Calculadora Laboral EC.

Tres grupos:
  1. ENTRADAS de los cálculos: lo que llena el usuario en el formulario.
     Si algo es inválido, FastAPI responde 422 y nunca se llama al modelo.
  2. RESULTADO de un cálculo: lo que devuelve el código (no el modelo).
     Es también la entrada de POST /explicar.
  3. EXPLICACIÓN: lo que el MODELO debe devolver (JSON con esquema).

Regla del kit para el modo estricto de Gemini y Groq: extra="forbid" en lo que
devuelve el modelo, y las reglas finas van en validadores de Python.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SUELDO_MAXIMO = 100_000  # tope de cordura para rechazar errores de digitación


class Estricto(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


# ======================================================================
# 1. ENTRADAS (formulario del usuario)
# ======================================================================
class EntradaDecimoTercero(Estricto):
    """Remuneraciones mensuales del período (1 de diciembre a 30 de noviembre)."""
    remuneraciones: list[float] = Field(
        min_length=1, max_length=12,
        description="Lo percibido en cada mes trabajado del período; de 1 a 12 valores",
    )

    @field_validator("remuneraciones")
    @classmethod
    def montos_validos(cls, v: list[float]) -> list[float]:
        for monto in v:
            if monto <= 0:
                raise ValueError("cada remuneración debe ser mayor que 0")
            if monto > SUELDO_MAXIMO:
                raise ValueError(f"cada remuneración debe ser menor que {SUELDO_MAXIMO}")
        return v


class EntradaDecimoCuarto(Estricto):
    meses_trabajados: int = Field(ge=1, le=12, description="Meses trabajados en el período de la región")
    region: Literal["costa_galapagos", "sierra_amazonia"]


class EntradaVacaciones(Estricto):
    remuneracion_mensual: float = Field(gt=0, le=SUELDO_MAXIMO)
    fecha_ingreso: date
    fecha_corte: date | None = Field(default=None, description="Fecha del cálculo; si falta, se usa la de hoy")

    @model_validator(mode="after")
    def fechas_coherentes(self) -> "EntradaVacaciones":
        corte = self.fecha_corte or date.today()
        if self.fecha_ingreso > corte:
            raise ValueError("la fecha de ingreso no puede ser posterior a la fecha de corte")
        if self.fecha_corte and self.fecha_corte > date.today():
            raise ValueError("la fecha de corte no puede estar en el futuro")
        return self


# ======================================================================
# 2. RESULTADO de un cálculo (lo produce el código)
# ======================================================================
class ResultadoCalculo(Estricto):
    tipo: Literal["decimo_tercero", "decimo_cuarto", "vacaciones"]
    entradas: dict
    desglose: list[str]
    total: float
    dias: float | None = None
    fundamento: str


# ======================================================================
# 3. EXPLICACIÓN (lo que devuelve el MODELO en POST /explicar)
#    Los nombres coinciden con app/prompts/system_v3.md.
# ======================================================================
class Explicacion(Estricto):
    estado: Literal["ok", "no_disponible"]
    explicacion: str = Field(description="Texto breve en lenguaje sencillo; vacío si no_disponible")
    pasos: list[str] = Field(description="Cada paso del desglose explicado con sus valores")
    advertencias: list[str] = Field(description="Inconsistencias o instrucciones sospechosas detectadas")
    faltantes: list[str] = Field(description="Datos que faltan si estado es no_disponible")

    @field_validator("explicacion")
    @classmethod
    def explicacion_corta(cls, v: str) -> str:
        if len(v) > 1200:
            raise ValueError("la explicación debe tener máximo 1200 caracteres")
        return v
