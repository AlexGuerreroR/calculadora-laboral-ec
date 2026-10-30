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

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

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


class EntradaHorasExtra(Estricto):
    """Horas trabajadas sobre la jornada de 8 horas en el mes (Art. 55)."""
    remuneracion_mensual: float = Field(gt=0, le=SUELDO_MAXIMO, description="Sueldo mensual en USD")
    horas_suplementarias: float = Field(
        default=0, ge=0, le=48,
        description="Horas extra del día o hasta las 24h00 (recargo 50 %). Máximo 12 por semana: 48 al mes")
    horas_extraordinarias: float = Field(
        default=0, ge=0, le=200,
        description="Horas entre las 24h00 y las 06h00, o en sábado o domingo (recargo 100 %)")

    @model_validator(mode="after")
    def alguna_hora(self) -> "EntradaHorasExtra":
        if self.horas_suplementarias == 0 and self.horas_extraordinarias == 0:
            raise ValueError("indique al menos una hora suplementaria o extraordinaria")
        return self


class EntradaLiquidacion(Estricto):
    """Datos para estimar la liquidación al terminar la relación laboral."""
    remuneracion_mensual: float = Field(gt=0, le=SUELDO_MAXIMO, description="Último sueldo mensual en USD")
    fecha_ingreso: date = Field(description="Fecha en que empezó a trabajar")
    fecha_salida: date = Field(description="Último día de trabajo")
    motivo: Literal["despido_intempestivo", "desahucio", "acuerdo_partes"] = Field(
        description="despido_intempestivo: lo despidieron sin causa legal; desahucio: aviso escrito "
                    "de terminar el contrato (incluye la renuncia con aviso); acuerdo_partes: terminación de mutuo acuerdo")
    region: Literal["costa_galapagos", "sierra_amazonia"] = Field(description="Región para el décimo cuarto")
    decimos_mensualizados: bool = Field(
        default=False, description="true si recibía los décimos cada mes; entonces no hay décimos pendientes")

    @model_validator(mode="after")
    def fechas_coherentes(self) -> "EntradaLiquidacion":
        if self.fecha_ingreso >= self.fecha_salida:
            raise ValueError("la fecha de salida debe ser posterior a la de ingreso")
        if self.fecha_salida > date.today():
            raise ValueError("la fecha de salida no puede estar en el futuro")
        return self


# ======================================================================
# 2. RESULTADO de un cálculo (lo produce el código)
# ======================================================================
class ResultadoCalculo(Estricto):
    tipo: Literal["decimo_tercero", "decimo_cuarto", "vacaciones", "horas_extra", "liquidacion"]
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


# ======================================================================
# 4. SOLICITUD del endpoint POST /calculos/decimos
#    Un solo endpoint para los dos décimos (como define docs/03-arquitectura.md):
#    el campo «tipo» indica cuál calcular y qué datos son obligatorios.
# ======================================================================
class SolicitudDecimos(Estricto):
    tipo: Literal["decimo_tercero", "decimo_cuarto"]
    remuneraciones: list[float] | None = Field(default=None, description="Solo para el décimo tercero")
    meses_trabajados: int | None = Field(default=None, description="Solo para el décimo cuarto")
    region: Literal["costa_galapagos", "sierra_amazonia"] | None = Field(default=None, description="Solo para el décimo cuarto")

    @model_validator(mode="after")
    def datos_segun_tipo(self) -> "SolicitudDecimos":
        try:
            if self.tipo == "decimo_tercero":
                if self.remuneraciones is None:
                    raise ValueError("para el décimo tercero envíe 'remuneraciones'")
                if self.meses_trabajados is not None or self.region is not None:
                    raise ValueError("'meses_trabajados' y 'region' solo aplican al décimo cuarto")
                EntradaDecimoTercero(remuneraciones=self.remuneraciones)
            else:
                if self.meses_trabajados is None or self.region is None:
                    raise ValueError("para el décimo cuarto envíe 'meses_trabajados' y 'region'")
                if self.remuneraciones is not None:
                    raise ValueError("'remuneraciones' solo aplica al décimo tercero")
                EntradaDecimoCuarto(meses_trabajados=self.meses_trabajados, region=self.region)
        except ValidationError as e:  # se devuelve como 422 con el detalle del campo
            raise ValueError("; ".join(f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors())) from None
        return self
