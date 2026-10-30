"""Pruebas del corte por artículo y de la detección de citas (sin internet ni modelo)."""
from app.services.normativa import cortar, limpiar, tema_de
from app.services.retriever import articulos_citados

MUESTRA = """Título I
Capítulo X
DEL DESAHUCIO Y DEL DESPIDO
Art. 185.- Bonificaciones por desahucio.- En los casos de terminación de la relación
laboral por desahucio, el empleador bonificará al trabajador con el veinticinco por
https://edicioneslegales.com.ec/

Pág. 72 de 199

Todos los derechos reservados. Prohibida su reproducción parcial o total.
Piense en el medio ambiente. Imprima solo de ser necesario.

ciento del equivalente a la última remuneración mensual por cada uno de los años.
Notas:
- Conforme al Acuerdo MDT-2023-175 se fija el salario básico en $ 460,00.
Art. 186.-(Derogado por el Art. 32 de la Ley s/n, R.O. 483-3S, 20-IV-2015).
Art. ... (1).- Artículo agregado sin número.
Art. 188.- Indemnización por despido intempestivo.- El empleador que despidiere
intempestivamente al trabajador, será condenado a indemnizarlo.
DISPOSICIONES GENERALES
Primera.- Texto que no es un artículo.
"""


def test_un_fragmento_por_articulo_con_su_cabecera():
    fr = cortar(MUESTRA)
    assert [f.articulo for f in fr] == ["185", "186", "s/n tras 186 (1)", "188"]
    assert all(f.texto.startswith("Art.") for f in fr)  # ninguno huérfano


def test_quita_el_pie_de_pagina_que_partia_el_articulo():
    art185 = cortar(MUESTRA)[0].texto
    assert "edicioneslegales" not in art185 and "Pág." not in art185
    assert "veinticinco por ciento" in art185  # el artículo quedó completo


def test_quita_las_notas_editoriales_con_valores_viejos():
    assert all("460,00" not in f.texto for f in cortar(MUESTRA))


def test_derogado_queda_no_vigente():
    vigencia = {f.articulo: f.metadatos["vigente"] for f in cortar(MUESTRA)}
    assert vigencia["186"] is False and vigencia["188"] is True


def test_etiquetas_de_la_ficha_y_capitulo():
    m = cortar(MUESTRA, fuente="url", version="2023")[-1].metadatos
    assert m["documento"] == "Código del Trabajo" and m["articulo"] == "188"
    assert m["tema"] == "despido" and m["vigente"] is True
    assert m["capitulo"] == "Capítulo X · Del desahucio y del despido"


def test_lo_que_sigue_a_las_disposiciones_no_se_pega_al_articulo():
    assert "Primera.-" not in cortar(MUESTRA)[-1].texto


def test_temas_por_rango():
    assert [tema_de(n) for n in ("55", "69", "111", "188", "16.1", "300")] == \
        ["jornada", "vacaciones", "decimos", "despido", "otros", "otros"]


def test_limpiar_quita_url_pegada_al_final_de_una_linea():
    assert limpiar("R.O. 483-3S, 20-IVhttps://edicioneslegales.com.ec/") == ["R.O. 483-3S, 20-IV"]


def test_busqueda_hibrida_detecta_el_articulo_nombrado():
    assert articulos_citados("¿Qué dice el Art. 188 y el artículo 69?") == ["188", "69"]
    assert articulos_citados("Me botaron sin aviso") == []
