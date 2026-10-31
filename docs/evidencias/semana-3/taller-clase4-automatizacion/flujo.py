# app/flujo.py · la cinta del Grupo 7 · generado en el taller del 29-oct-2026
# Disparador: Formulario web · Acción final: Registrar la liquidación como pendiente con su base legal y avisar a RR. HH
from decimal import Decimal
from pydantic import BaseModel, Field, ValidationError
from typing import Literal
from app.config import PARAMETROS as P      # config/parametros.yaml: umbral, tarifas…

UMBRAL = P["umbral_confianza"]              # 0.85 elegido en el taller


class Clase(BaseModel):                     # lo que la IA puede responder al clasificar
    tipo: Literal["TODO_tipo_1", "TODO_tipo_2", "otro"]
    confianza: float = Field(ge=0, le=1)


class Datos(BaseModel):                     # lo que la IA puede extraer (sin campos de «monto a pagar»)
    # TODO: nombre, fecha de ingreso, fecha de salida, sueldo
    instrucciones_en_texto: bool = False      # la IA marca si el texto trae órdenes al sistema


def procesar(doc):
    """Cada documento termina en un estado: procesado, en revisión o rechazado con motivo."""
    # 1 · Disparador — decide: Sistema
    #     Llega: solicitud de liquidación con fechas y sueldo (formulario web)  →  Evento en la cola
    # sistema.disparador(…, clave=doc.id)         # idempotente: si ya existe, no se repite

    # 2 · Clasificar — decide: IA
    #     Decidir el tipo (liquidación, consulta u otro) con un número de confianza  →  JSON {tipo, confianza}
    # resultado = llm.parse(doc.texto, schema=…)   # solo devuelve campos del esquema

    # 3 · Umbral — decide: Código
    #     Si la confianza es baja, desviar a revisión  →  Sigue o va a revisión
    # resultado = umbral(datos, P)          # determinista, con pruebas en tests/

    # 4 · Extraer — decide: IA
    #     Sacar los campos: nombre, fecha de ingreso, fecha de salida, sueldo  →  Datos validados con Pydantic
    # resultado = llm.parse(doc.texto, schema=…)   # solo devuelve campos del esquema

    # 5 · Reglas — decide: Código
    #     Calcular décimos y vacaciones con Decimal y config/  →  Resultado exacto con su fuente
    # resultado = reglas(datos, P)          # determinista, con pruebas en tests/

    # 6 · Revisión — decide: Persona
    #     RR. HH. aprueba antes de cualquier pago  →  Aprobado o corregido
    # return revision_humana(doc, motivo=…)        # la persona recibe el trabajo ya hecho

    # 7 · Actuar — decide: Sistema
    #     Registrar como pendiente (idempotente) y notificar a RR. HH.  →  Registro con auditoría
    # sistema.actuar(…, clave=doc.id)         # idempotente: si ya existe, no se repite


def revision_humana(doc, motivo):
    """Registra el documento como «en revisión» con su motivo y avisa a la persona responsable."""
    ...
