"""Resumen PDF local de una instantánea ya confirmada. No llama a un modelo.

Devuelve bytes; la aplicación no guarda el documento en disco ni lo envía a
terceros. ReportLab se importa solo al generar, nunca al preparar la vista previa.
"""
from datetime import date, datetime
from decimal import Decimal
from html import escape
from io import BytesIO

NOMBRES = {"decimo_tercero": "Décimo tercero", "decimo_cuarto": "Décimo cuarto", "vacaciones": "Vacaciones",
           "horas_extra": "Horas adicionales", "liquidacion": "Liquidación estimada"}
ETIQUETAS = {
    "remuneraciones": "Remuneraciones del período (USD)", "remuneracion_mensual": "Remuneración mensual",
    "meses_trabajados": "Meses trabajados", "region": "Región", "fecha_ingreso": "Fecha de ingreso",
    "fecha_corte": "Fecha de corte", "fecha_salida": "Fecha de salida", "anios_completos": "Años completos",
    "motivo_salida": "Motivo de salida informado", "salario_pendiente": "Salario pendiente",
    "base_acumulada_decimo_tercero": "Base del décimo tercero pendiente",
    "dias_decimo_cuarto_pendientes": "Días pendientes de décimo cuarto",
    "dias_vacaciones_base_pendientes": "Días base de vacaciones pendientes",
    "dias_vacaciones_adicionales_pendientes": "Días adicionales de vacaciones pendientes",
    "horas_suplementarias": "Horas suplementarias", "horas_extraordinarias": "Horas extraordinarias",
    "horas_suplementarias_pendientes": "Horas suplementarias pendientes",
    "horas_extraordinarias_pendientes": "Horas extraordinarias pendientes",
    "descuentos_confirmados": "Descuentos verificados", "criterios_confirmados": "Criterios y saldos confirmados",
}
DINERO = {"remuneracion_mensual", "salario_pendiente", "base_acumulada_decimo_tercero", "descuentos_confirmados"}


def monto(valor):
    texto = f"{Decimal(str(valor)):,.2f}"
    return "USD " + texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _valor(campo, valor):
    if valor is None:
        return "No informada; se aplicó la fecha actual del cálculo" if campo == "fecha_corte" else "No informado"
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if campo in DINERO:
        return monto(valor)
    if campo.startswith("fecha_"):
        return date.fromisoformat(str(valor)).strftime("%d/%m/%Y")
    if isinstance(valor, list):
        return "; ".join(monto(v).replace("USD ", "") for v in valor)
    return str(valor).replace("_", " ")


def datos_para_vista(calculo):
    return [ETIQUETAS.get(campo, campo.replace("_", " ")) + ": " + _valor(campo, valor)
            for campo, valor in calculo.entradas.items()]


def generar_resumen(pendiente) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                   KeepTogether)

    verde = colors.HexColor("#116B55")
    oscuro = colors.HexColor("#173F35")
    suave = colors.HexColor("#52675F")
    borde = colors.HexColor("#DCE5E0")
    fondo = colors.HexColor("#EDF5F0")
    ancho = A4[0] - 88
    estilos = {
        "normal": ParagraphStyle("normal", fontName="Helvetica", fontSize=9.5, leading=14, textColor=oscuro, spaceAfter=6),
        "pequeno": ParagraphStyle("pequeno", fontName="Helvetica", fontSize=8, leading=11, textColor=suave, spaceAfter=5),
        "titulo": ParagraphStyle("titulo", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=oscuro, spaceAfter=8),
        "seccion": ParagraphStyle("seccion", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=verde, spaceBefore=14, spaceAfter=8, keepWithNext=True),
        "etiqueta": ParagraphStyle("etiqueta", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=oscuro),
        "valor": ParagraphStyle("valor", fontName="Helvetica", fontSize=9.5, leading=13, textColor=oscuro),
        "total": ParagraphStyle("total", fontName="Helvetica-Bold", fontSize=25, leading=31, textColor=verde, alignment=TA_RIGHT),
    }
    def p(texto, estilo="normal"):
        # Las entradas son texto, no marcado ReportLab ni instrucciones.
        return Paragraph(escape(str(texto)), estilos[estilo])

    calculo = pendiente.calculo
    fecha = datetime.fromisoformat(pendiente.preparado_en)
    salida = BytesIO()
    doc = SimpleDocTemplate(salida, pagesize=A4, leftMargin=44, rightMargin=44,
                            topMargin=87, bottomMargin=55, title="Resumen - " + NOMBRES[calculo.tipo],
                            author="Calculadora Laboral EC", pageCompression=1)

    def pagina(canvas, documento):
        canvas.saveState()
        canvas.setFillColor(verde)
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawString(44, A4[1] - 40, "Calculadora Laboral EC")
        canvas.setFillColor(suave)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(44, A4[1] - 55, "Resumen de beneficios y saldos laborales | Ecuador")
        canvas.setStrokeColor(borde)
        canvas.line(44, A4[1] - 66, A4[0] - 44, A4[1] - 66)
        canvas.line(44, 42, A4[0] - 44, 42)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(44, 28, "Orientación informativa. No es un acta de finiquito ni un dictamen legal.")
        canvas.drawRightString(A4[0] - 44, 28, f"Página {documento.page}")
        canvas.restoreState()

    historia = [p(NOMBRES[calculo.tipo], "titulo"),
                p("Preparado el " + fecha.strftime("%d/%m/%Y a las %H:%M") + " (Ecuador continental).", "pequeno")]
    total = Table([[p("TOTAL DEL CÁLCULO" if calculo.tipo != "liquidacion" else "TOTAL NETO ESTIMADO", "etiqueta"),
                    p(monto(calculo.total), "total")]], colWidths=[ancho * .43, ancho * .57])
    total.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), fondo), ("BOX", (0, 0), (-1, -1), .6, borde),
                              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 14),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 14),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 14)]))
    historia += [Spacer(1, 7), total,
                 p("Revise los datos y el desglose. Los saldos informados y el motivo de salida requieren comprobación antes de un uso real.", "pequeno"),
                 p("Datos utilizados", "seccion")]
    filas = [[p("Dato", "etiqueta"), p("Valor", "etiqueta")]]
    for campo, valor in calculo.entradas.items():
        filas.append([p(ETIQUETAS.get(campo, campo.replace("_", " ")), "etiqueta"), p(_valor(campo, valor), "valor")])
    tabla = Table(filas, colWidths=[ancho * .42, ancho * .58], repeatRows=1, hAlign="LEFT")
    tabla.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), fondo),
                              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAF9")]),
                              ("LINEBELOW", (0, 0), (-1, 0), .6, borde),
                              ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                              ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    historia += [tabla, p("Detalle del cálculo", "seccion")]
    for i, paso in enumerate(calculo.desglose, 1):
        historia.append(p(f"{i}. {paso}"))
    historia += [p("Fundamento y fuentes", "seccion"), p(calculo.fundamento)]
    if pendiente.advertencia_fuentes:
        historia.append(p(pendiente.advertencia_fuentes))
    for fuente in pendiente.fuentes:
        historia.append(KeepTogether([p(f"{fuente.documento}, Art. {fuente.articulo}", "etiqueta"),
                                     p("Versión: " + fuente.version, "pequeno"), p(fuente.fuente, "pequeno")]))
    historia += [p("Alcance del resumen", "seccion"),
        p("Consulte la versión y fecha de corte de las fuentes citadas. Este resumen conserva los datos y montos revisados en la vista previa. No certifica ausencia de reformas posteriores al corte, que el motivo de salida sea legal ni que los saldos declarados sean correctos."),
        p("Ante una disputa o datos desconocidos, consulte a la Inspectoría del Ministerio del Trabajo. No utilice esta estimación para negar derechos o sustituir asesoría profesional.")]
    doc.build(historia, onFirstPage=pagina, onLaterPages=pagina)
    return salida.getvalue()
