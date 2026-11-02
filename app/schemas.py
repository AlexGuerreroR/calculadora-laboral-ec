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
from decimal import Decimal
from calendar import monthrange
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


# ======================================================================
# 2. RESULTADO de un cálculo (lo produce el código)
# ======================================================================
class EntradaHoras(Estricto):
    """Horas agregadas de un período, con sueldo mensual de jornada completa."""
    remuneracion_mensual: Decimal = Field(gt=0, le=SUELDO_MAXIMO)
    horas_suplementarias: Decimal = Field(ge=0)
    horas_extraordinarias: Decimal = Field(ge=0)

    @model_validator(mode="after")
    def horas_presentes(self) -> "EntradaHoras":
        if self.horas_suplementarias + self.horas_extraordinarias == 0:
            raise ValueError("indique al menos una hora adicional")
        return self


class EntradaLiquidacion(Estricto):
    """Saldos informados explícitamente: un cero significa pagado o no pendiente."""
    remuneracion_mensual: Decimal = Field(gt=0, le=SUELDO_MAXIMO)
    fecha_ingreso: date
    fecha_salida: date
    motivo_salida: Literal["renuncia_con_desahucio", "despido_intempestivo"]
    region: Literal["costa_galapagos", "sierra_amazonia"]
    salario_pendiente: Decimal = Field(ge=0)
    base_acumulada_decimo_tercero: Decimal = Field(ge=0, description="Remuneraciones del período cuyo décimo tercero aún no se pagó")
    dias_decimo_cuarto_pendientes: Decimal = Field(ge=0)
    dias_vacaciones_base_pendientes: Decimal = Field(ge=0, description="Saldo de días base no gozados ni pagados")
    dias_vacaciones_adicionales_pendientes: Decimal = Field(ge=0)
    horas_suplementarias_pendientes: Decimal = Field(ge=0)
    horas_extraordinarias_pendientes: Decimal = Field(ge=0)
    descuentos_confirmados: Decimal = Field(ge=0)
    criterios_confirmados: Literal[True] = Field(description="El usuario confirmó el motivo y los saldos; no es un dictamen legal")

    @model_validator(mode="after")
    def datos_coherentes(self) -> "EntradaLiquidacion":
        from app.tools.parametros import cargar_parametros
        calendario = cargar_parametros()["calendario"]
        dias_mes, dias_anio = calendario["dias_mes"], calendario["dias_anio"]
        if self.fecha_salida < self.fecha_ingreso:
            raise ValueError("la salida no puede ser anterior al ingreso")
        if self.fecha_salida > date.today():
            raise ValueError("la fecha de salida no puede estar en el futuro")
        if self.dias_decimo_cuarto_pendientes > dias_anio:
            raise ValueError("los días del décimo cuarto superan un período anual; revise pagos anteriores")
        def dia_comercial(fecha):
            return dias_mes if fecha.day == monthrange(fecha.year, fecha.month)[1] else min(fecha.day, dias_mes)
        comercial = ((self.fecha_salida.year - self.fecha_ingreso.year) * dias_anio
                     + (self.fecha_salida.month - self.fecha_ingreso.month) * dias_mes
                     + dia_comercial(self.fecha_salida) - dia_comercial(self.fecha_ingreso) + 1)
        # Un febrero completo puede representar 30 días comerciales aunque
        # tenga 28/29 días naturales. Esta comprobación es solo de coherencia.
        duracion = Decimal(max((self.fecha_salida - self.fecha_ingreso).days + 1, comercial))
        if self.dias_decimo_cuarto_pendientes > duracion:
            raise ValueError("los días pendientes del décimo cuarto superan la duración del empleo")
        if self.dias_vacaciones_base_pendientes + self.dias_vacaciones_adicionales_pendientes > duracion:
            raise ValueError("el saldo de vacaciones supera la duración del empleo")
        return self


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
class FuenteRAG(Estricto):
    id: str
    documento: str
    articulo: str
    texto: str
    fuente: str
    version: str


class ExplicacionRAG(Explicacion):
    citas: list[str] = Field(description="Identificadores exactos de los fragmentos usados; vacío si se abstiene")


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


# Agente: consulta sin historial enviado por el cliente; el servidor construye el bucle.
class ConsultaAgente(Estricto):
    mensaje: str = Field(min_length=1, max_length=10000)
    calculo: ResultadoCalculo | None = None
    confirmar_liquidacion: bool = False

    @field_validator("mensaje")
    @classmethod
    def mensaje_no_vacio(cls, valor):
        if not valor.strip():
            raise ValueError("escriba su consulta")
        return valor.strip()


class EntradaConsultaNormativa(Estricto):
    pregunta: str = Field(min_length=3, max_length=1500)


class EntradaDiasVacaciones(Estricto):
    anios_servicio: int = Field(ge=0, le=100, strict=True)


class EntradaJornada(Estricto):
    horas_diarias: Decimal = Field(gt=0, le=24, allow_inf_nan=False)


class ResultadoJornada(Estricto):
    horas_declaradas: float
    referencia_diaria: float
    exceso_sobre_referencia: float
    fundamento: str


class ResultadoDiasVacaciones(Estricto):
    anios_servicio: int
    dias_base: int
    dias_adicionales: int
    dias_anuales: int
    fundamento: str


class EntradaExplicarAgente(Estricto):
    calculo_id: str = Field(pattern=r"^calculo-\d+$")


class EntradaSolicitarDatos(Estricto):
    tipo_calculo: Literal["decimo_tercero", "decimo_cuarto", "vacaciones", "horas_extra", "liquidacion"]


class TextoNormativo(Estricto):
    estado: Literal["ok", "no_disponible"]
    respuesta: str = Field(description="Explicación normativa sin cálculos ni montos; vacía si no hay respaldo")
    citas: list[str] = Field(description="Identificadores de los fragmentos usados")


class PasoAgente(Estricto):
    herramienta: str
    estado: str


class CalculoAgente(Estricto):
    id: str
    resultado: ResultadoCalculo


class ExplicacionAgente(Estricto):
    calculo_id: str
    explicacion: ExplicacionRAG
    fuentes: list[FuenteRAG]


class NormativaAgente(Estricto):
    respuesta: str
    fuentes: list[FuenteRAG]
    calculo_dias: ResultadoDiasVacaciones | None = None
    calculo_jornada: ResultadoJornada | None = None


class SolicitudResumen(Estricto):
    calculo: ResultadoCalculo


class TokenResumen(Estricto):
    token: str = Field(min_length=32, max_length=128)


class ConfirmacionResumen(TokenResumen):
    confirmar: Literal[True]

    @field_validator("confirmar", mode="before")
    @classmethod
    def confirmacion_booleana(cls, valor):
        if valor is not True:
            raise ValueError("confirme explícitamente la generación del PDF")
        return valor


class VistaPreviaResumen(Estricto):
    token: str
    nombre_archivo: str
    calculo: ResultadoCalculo
    datos: list[str]
    fuentes: list[FuenteRAG]
    advertencia_fuentes: str
    preparado_en: str
    vence_en_segundos: int
    mensaje: str


class RespuestaAgente(Estricto):
    estado: Literal["completado", "pedir_datos", "rechazado", "abstencion", "limite", "requiere_confirmacion"]
    mensaje: str
    calculos: list[CalculoAgente] = Field(default_factory=list)
    explicaciones: list[ExplicacionAgente] = Field(default_factory=list)
    normativa: list[NormativaAgente] = Field(default_factory=list)
    pasos: list[PasoAgente] = Field(default_factory=list)
    faltantes: list[str] = Field(default_factory=list)
    resumen_confirmacion: list[str] = Field(default_factory=list)
    iteraciones: int = 0
    llamadas_modelo: int = 0
    resumen_pdf: VistaPreviaResumen | None = None
    # Puente interno al router: no se serializa ni se devuelve al modelo.
    calculo_para_resumen: ResultadoCalculo | None = Field(default=None, exclude=True)
