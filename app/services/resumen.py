"""Resumen descargable en PDF (función que pide el caso 07: «generar resumen PDF»).

El PDF se arma SOLO con datos del servidor: los cálculos que hicieron las herramientas
y los artículos recuperados y citados. Nada de lo que escribe el modelo entra al PDF,
salvo la respuesta ya verificada. No se guarda en disco: se genera en memoria al descargarlo.
"""
from __future__ import annotations

import io
from datetime import date
from xml.sax.saxutils import escape

AVISO = ("Este resumen es una orientación generada por Calculadora Laboral EC. Los montos los calcula el "
         "sistema con parámetros de configuración; el valor oficial lo determina el empleador conforme a la ley. "
         "Ante un conflicto laboral, acuda al Ministerio del Trabajo. No contiene datos personales.")
NOMBRES = {"decimo_tercero": "Décimo tercero", "decimo_cuarto": "Décimo cuarto", "vacaciones": "Vacaciones",
           "horas_extra": "Horas extra", "liquidacion": "Liquidación estimada"}


def _usd(valor: float) -> str:
    return f"USD {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def generar_pdf(calculos: list[dict], fuentes: list[dict], respuesta: str = "",
                hoy: date | None = None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    if not calculos:
        raise ValueError("No hay cálculos para resumir.")
    est = getSampleStyleSheet()
    p = lambda texto, estilo="BodyText": Paragraph(escape(texto), est[estilo])  # noqa: E731
    hoy = hoy or date.today()
    partes = [p("Calculadora Laboral EC · Resumen", "Title"),
              p(f"Fecha de generación: {hoy.isoformat()}"), Spacer(1, 0.4 * cm)]
    if respuesta:
        partes += [p("Explicación", "Heading2"), p(respuesta), Spacer(1, 0.3 * cm)]
    for c in calculos:
        partes += [p(f"{NOMBRES.get(c['tipo'], c['tipo'])}: {_usd(c['total'])}", "Heading2")]
        partes += [p(f"{i}. {linea}") for i, linea in enumerate(c["desglose"], 1)]
        partes += [p(f"Fundamento: {c['fundamento']}", "Italic"), Spacer(1, 0.3 * cm)]
    if fuentes:
        partes += [p("Fuentes del Código del Trabajo", "Heading2")]
        for f in fuentes:
            texto = f["texto"].replace("<fragmento>", "").replace("</fragmento>", "")
            partes += [p(f"Art. {f['articulo']}" + (f" · {f['capitulo']}" if f.get("capitulo") else ""), "Heading4"),
                       p(texto[:1500])]
    partes += [Spacer(1, 0.5 * cm), p(AVISO, "Italic")]

    salida = io.BytesIO()
    SimpleDocTemplate(salida, pagesize=A4, title="Resumen Calculadora Laboral EC",
                      leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm).build(partes)
    return salida.getvalue()
