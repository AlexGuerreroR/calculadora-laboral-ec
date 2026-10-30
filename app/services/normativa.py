"""Corte y etiquetado del Código del Trabajo para el RAG (semana 3).

Funciones puras: reciben texto y devuelven fragmentos. No leen archivos ni llaman a
ningún modelo, por eso se prueban sin internet (tests/test_normativa.py).

Decisiones (justificadas en docs/06-rag.md):
- Un artículo = un fragmento, con su cabecera «Art. N.-» (nunca por tamaño fijo).
- Se quita el pie de página del PDF, que aparece en cada hoja y partía los artículos.
- Se quitan las «Notas:» editoriales: no son texto de la ley y traen valores viejos
  (por ejemplo, el salario básico de 2024).
- Los artículos derogados se guardan con vigente=False: el filtro los excluye.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

DOCUMENTO = "Código del Trabajo"

# Pie de página que el PDF repite en las 199 hojas.
_PIE = re.compile(
    r"^(https://edicioneslegales\.com\.ec/?|Pág\. \d+ de \d+|Todos los derechos reservados\..*"
    r"|Piense en el medio ambiente\..*)$"
)
# Cabecera de artículo al inicio de una línea:
#   «Art. 188.-», «Art. 16.1.-», «Art. ... (2).-», «Art. (...).-», «Art. … .-»
_CABECERA = re.compile(
    r"^Art\.\s*(?P<num>\d+(?:\.\d+)?|\(\.\.\.\)|\.\.\.|…)\s*(?:\(\d+\))?\s*\.?\s*-"
)
_DIVISION = re.compile(r"^(Título|Capítulo|Parágrafo)\s+\S+$")
_FIN_ARTICULADO = re.compile(r"^DISPOSICI(ONES|ÓN)\s+[A-ZÁÉÍÓÚÑ ]+$")

# Tema de cada rango de artículos (filtro antes de buscar). Los rangos siguen los
# capítulos del Código; lo que no está aquí queda como «otros».
TEMAS: list[tuple[int, int, str]] = [
    (47, 68, "jornada"),        # jornada, descanso y horas suplementarias (Art. 55)
    (69, 78, "vacaciones"),     # Arts. 69 a 78
    (79, 110, "remuneracion"),  # salarios y utilidades
    (111, 114, "decimos"),      # décima tercera y décima cuarta
    (169, 195, "despido"),      # terminación, desahucio, visto bueno, despido
]


@dataclass
class Fragmento:
    id: str
    articulo: str          # «188», «16.1» o «s/n tras 42»
    texto: str
    metadatos: dict = field(default_factory=dict)


def limpiar(texto: str) -> list[str]:
    """Quita el pie de página y las líneas vacías; devuelve las líneas útiles."""
    lineas = (ln.replace("https://edicioneslegales.com.ec/", "").strip() for ln in texto.splitlines())
    return [ln for ln in lineas if ln and not _PIE.match(ln)]


def tema_de(numero: str) -> str:
    try:
        n = int(float(numero))
    except ValueError:
        return "otros"
    return next((t for a, b, t in TEMAS if a <= n <= b), "otros")


def cortar(texto: str, fuente: str = "", version: str = "") -> list[Fragmento]:
    """Corta el texto por artículo y etiqueta cada fragmento."""
    fragmentos: list[Fragmento] = []
    actual: list[str] | None = None   # líneas del artículo en curso
    num_actual = ""
    ultimo_numerado = "0"
    innumerados = 0
    capitulo = ""          # «Capítulo X · Del desahucio y del despido»
    paragrafo = ""         # «Parágrafo 3ro.», dentro del capítulo
    en_nota = False
    esperar_nombre = False

    def cerrar() -> None:
        if not actual:
            return
        cuerpo = " ".join(actual).strip()
        derogado = bool(re.search(r"^Art\.[^-]*-\s*\(Derogado", cuerpo))
        ident = f"art-{num_actual}".replace(" ", "-").replace("/", "")
        if any(f.id == ident for f in fragmentos):  # el PDF repite algún número
            ident = f"{ident}-b{sum(f.id.startswith(ident) for f in fragmentos)}"
        fragmentos.append(Fragmento(
            id=ident, articulo=num_actual, texto=cuerpo,
            metadatos={"documento": DOCUMENTO, "articulo": num_actual,
                       "tema": tema_de(num_actual), "vigente": not derogado,
                       "capitulo": " · ".join(x for x in (capitulo, paragrafo) if x),
                       "fuente": fuente, "version": version}))

    for linea in limpiar(texto):
        m = _CABECERA.match(linea)
        if m:
            cerrar()
            en_nota = esperar_nombre = False
            num = m.group("num")
            if num[0].isdigit():
                num_actual, ultimo_numerado, innumerados = num, num, 0
            else:  # artículo innumerado: se ubica por el último artículo con número
                innumerados += 1
                num_actual = f"s/n tras {ultimo_numerado} ({innumerados})"
            actual = [linea]
            continue
        if _FIN_ARTICULADO.match(linea):
            cerrar()
            actual, en_nota = None, False
            continue
        if _DIVISION.match(linea):
            cerrar()
            actual, en_nota = None, False
            if linea.startswith("Parágrafo"):
                paragrafo = linea
            else:  # un Título o Capítulo nuevo reinicia la ubicación
                capitulo, paragrafo = linea, ""
                esperar_nombre = linea.startswith("Capítulo")
            continue
        if esperar_nombre:  # la línea que sigue a «Capítulo X» es su nombre
            capitulo, esperar_nombre = f"{capitulo} · {linea.capitalize()}", False
            continue
        if linea.startswith(("Notas:", "Nota:")):
            en_nota = True
            continue
        if en_nota or actual is None:
            continue
        actual.append(linea)
    cerrar()
    return fragmentos
