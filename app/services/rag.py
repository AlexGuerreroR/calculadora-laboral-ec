"""Recuperación, contexto y comprobación de citas para explicar cálculos reales."""
import json
import re
from decimal import Decimal

from app.schemas import ExplicacionRAG, FuenteRAG, ResultadoCalculo
from app.services import retriever
from app.services.llm import SalidaInvalida, cargar_prompt
from app.tools.parametros import cargar_parametros

SIN_RESPALDO = ("No encontré respaldo suficiente en las fuentes cargadas para explicar este resultado. "
                "Puede consultar al Ministerio del Trabajo. El cálculo sigue visible por separado.")


def recuperar_calculo(resultado: ResultadoCalculo) -> list[FuenteRAG]:
    config = cargar_parametros()["rag"]
    articulos = [str(a) for a in config["articulos_calculo"].get(resultado.tipo, [])]
    if resultado.tipo == "liquidacion":
        extras = config["articulos_liquidacion_adicionales"]
        articulos += extras.get(resultado.entradas.get("motivo_salida"), [])
        if any(Decimal(str(resultado.entradas.get(k, 0))) > 0 for k in
               ("horas_suplementarias_pendientes", "horas_extraordinarias_pendientes")):
            articulos += extras["horas_extra"]
        articulos = list(dict.fromkeys(articulos))
    if not articulos:
        return []
    pregunta = "Fundamento de " + resultado.tipo + ": " + "; ".join("Art. " + a for a in articulos)
    hits = retriever.buscar(pregunta, k=max(config["top_k"], len(articulos)))
    # Para un cálculo conocido exigimos todos los artículos configurados, no
    # solo un vecino semánticamente cercano. La selección de fuente es del código.
    fuentes = [FuenteRAG(id=h["id"], documento=h["documento"], articulo=h["articulo"],
                        texto=h["texto"], fuente=h["fuente"], version=h["version"])
               for h in hits if h["articulo"] in articulos and h.get("vigente") is True
               and all(h.get(k) for k in ("id", "texto", "documento", "fuente", "version"))]
    return fuentes if set(articulos) <= {f.articulo for f in fuentes} else []


def construir_contexto(resultado: ResultadoCalculo, fuentes: list[FuenteRAG]) -> str:
    # JSON serializa los fragmentos: un texto con </contexto> no rompe delimitadores.
    return json.dumps({"resultado": resultado.model_dump(mode="json"),
                       "fragmentos": [f.model_dump() for f in fuentes]}, ensure_ascii=False)


def validar_explicacion(exp: ExplicacionRAG, fuentes: list[FuenteRAG], resultado: ResultadoCalculo) -> list[FuenteRAG]:
    if exp.estado != "ok":
        if exp.explicacion or exp.pasos or exp.citas:
            raise SalidaInvalida()
        return []
    por_id = {f.id: f for f in fuentes}
    if not exp.explicacion.strip() or not exp.citas or not set(exp.citas) <= por_id.keys():
        raise SalidaInvalida()
    usadas = [por_id[i] for i in dict.fromkeys(exp.citas)]
    texto = " ".join([exp.explicacion, *exp.pasos, *exp.advertencias])
    articulos = set(retriever.articulos_citados(texto))
    if not articulos or not articulos <= {f.articulo for f in usadas}:
        raise SalidaInvalida()
    # Solo dinero explícito: «Art. 111» jamás habilita un monto USD 111.00.
    # Los valores permitidos vienen de entradas numéricas, desglose y total;
    # nunca del fundamento ni del corpus legal.
    permitidos = {Decimal(str(resultado.total))}
    def agregar(valor):
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            permitidos.add(Decimal(str(valor)))
        elif isinstance(valor, list):
            for item in valor:
                agregar(item)
    for valor in resultado.entradas.values():
        agregar(valor)
    for paso in resultado.desglose:
        permitidos.update(Decimal(n) for n in re.findall(r"(?<![\w.])\d+(?:\.\d+)?", paso))
    # El prompt exige formato USD; otras notaciones monetarias se rechazan.
    if re.search(r"[$€]|\b(?:EUR|euros?|d[oó]lares?)\b", texto, re.I):
        raise SalidaInvalida()
    montos = re.findall(r"\bUSD\s*([+-]?\d[\d.,]*)", texto, re.I)
    if len(montos) != len(re.findall(r"\bUSD", texto, re.I)):
        raise SalidaInvalida()
    for n in montos:
        n = n.rstrip(".,")  # puntuación final de la oración
        if not re.fullmatch(r"\d+(?:\.\d{1,2})?", n) or Decimal(n) not in permitidos:
            raise SalidaInvalida()
    return usadas


def explicar_calculo(llm, resultado, fuentes):
    prompt = cargar_parametros()["rag"]["prompt"]
    r = llm.generar_json(cargar_prompt(prompt), construir_contexto(resultado, fuentes), ExplicacionRAG)
    usadas = validar_explicacion(r.datos, fuentes, resultado)
    return r, usadas
