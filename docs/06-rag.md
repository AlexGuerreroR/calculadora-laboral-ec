# RAG: base de conocimiento y recuperación

Proyecto: Calculadora Laboral EC · Caso 07 · Grupo 7 · Semana 3.

El sistema responde con el Código del Trabajo y cita el artículo; si no encuentra fuente, guarda silencio y deriva. Los montos nunca salen del modelo: los calculan las herramientas en código (ADR-002). La ficha de diseño de la clase del 26/10 está en [rag/ficha_rag_grupo_07.md](rag/ficha_rag_grupo_07.md).

## 1. Fuentes

| Documento | Archivo | Versión | ¿Se indexa? |
| --- | --- | --- | --- |
| Código del Trabajo | `data/raw/CODIGO_DEL_TRABAJO.pdf` (no se sube: restricción de redistribución) | Codificación 2005-017, última reforma RO 309-S, 12-05-2023 | Sí |
| Acuerdo MDT-2025-195 (SBU 2026) | `data/raw/acuerdo_sbu_2026_mdt-2025-195.pdf` | 18-12-2025 | No: el SBU es configuración (`config/parametros.yaml`) |
| Acuerdo MDT-2023-140 | `data/raw/mdt-2023-140_obligaciones_empleador.pdf` | 14-11-2023 | Todavía no |

Si el PDF del Código no está, `scripts/ingest.py` lo descarga de la URL oficial del Ministerio del Trabajo. La vigencia de los artículos usados en los cálculos debe contrastarse con una versión actualizada a 2026 (ver `docs/04-fuentes.md`, «Limitación de la fuente consultada»).

## 2. Estrategia de fragmentación

**Un artículo = un fragmento, con su cabecera** («Art. 188.- Indemnización por despido intempestivo…»). Sin tamaño fijo ni solapamiento.

| Decisión | Por qué |
| --- | --- |
| Cortar donde una línea empieza con `Art. N.-` | Cada respuesta debe citar el artículo. Un corte por tamaño fijo deja fragmentos «huérfanos» sin su número, que no se pueden citar (clase del 26/10) |
| Sin solapamiento | El artículo es una unidad completa de la norma; no hace falta repetir texto entre fragmentos |
| Quitar el pie de página del PDF | Aparece en las 199 hojas (`edicioneslegales.com.ec`, `Pág. N de 199`, «Todos los derechos reservados…») y quedaba en medio de los artículos; en el Art. 125 aparecía incluso pegado al final de una línea |
| Quitar las «Notas:» editoriales | No son texto de la ley y traen valores desactualizados: la nota tras el Art. 187 fija el SBU de 2024 en USD 460 |
| Guardar los artículos derogados con `vigente = false` | El significado no distingue una norma vigente de una derogada; el filtro sí (clase del 27/10) |
| Artículos innumerados (`Art. ...-`, `Art. (...).-`) | Se identifican por el último artículo con número: «s/n tras 42 (1)» |
| Cortar al llegar a «DISPOSICIONES …» | El texto de las disposiciones generales y transitorias no se pega al último artículo |

**Resultado con el PDF real (28/10/2026, PyMuPDF):** 692 artículos detectados: 610 vigentes y 82 derogados. Los artículos de nuestras preguntas quedan completos y con su ubicación; por ejemplo, el Art. 188 en «Capítulo X · Del desahucio y del despido». El corte se prueba sin internet en `tests/test_normativa.py`.

**Límite conocido:** el modelo de embeddings lee como máximo 512 tokens. Los artículos muy largos (el Art. 438 tiene unos 18 700 caracteres) se representan solo por su inicio; ninguno de los artículos de nuestros cálculos supera unos 2 200 caracteres.

## 3. Etiquetas (metadatos)

| Etiqueta | Ejemplo | Para qué |
| --- | --- | --- |
| `documento` | Código del Trabajo | La cita que ve el usuario |
| `articulo` | 188 | La cita y la medición del hit@5 |
| `tema` | despido | Filtrar antes de buscar: jornada (Arts. 47–68), vacaciones (69–78), remuneracion (79–110), decimos (111–114), despido (169–195), otros |
| `vigente` | true | Excluir los artículos derogados |
| `capitulo` | Capítulo X · Del desahucio y del despido | Ubicar el artículo en el Código |
| `fuente`, `version` | URL oficial · reforma 2023 | Trazabilidad |

## 4. Base vectorial y búsqueda

| Decisión | Valor | Por qué |
| --- | --- | --- |
| Base vectorial | ChromaDB, en `data/chroma/` (`CHROMA_PATH`, fuera del repositorio) | Librería de Python, sin servidor |
| Modelo de embeddings | `intfloat/multilingual-e5-small` (`EMBEDDING_MODEL`) | Entiende español. El de ChromaDB por defecto (`all-MiniLM-L6-v2`) está entrenado en inglés y no da error: solo trae artículos equivocados |
| Prefijos | `passage: ` al guardar, `query: ` al buscar | Así se entrenó la familia E5 |
| Distancia | Coseno | Por defecto ChromaDB usa l2 |
| Top-k | 5 | Lo que mide el hit@5 |
| Filtro | `vigente = true` siempre; `tema` cuando se conoce | Se aplica antes del top-k |
| Búsqueda híbrida | Si la pregunta nombra un artículo («Art. 188»), ese artículo se trae por coincidencia exacta y va primero | El significado no distingue «Art. 52» de «Art. 53» |
| Mismo modelo para guardar y buscar | La colección guarda el nombre del modelo; si no coincide, el buscador se detiene con un mensaje | Guardar con un modelo y buscar con otro es «buscar una dirección de Quito en el mapa de Lima» |

## 5. Medición

`eval/run_eval.py` mide la **recuperación correcta (hit@5)** con las 20 preguntas de `eval/preguntas.csv` y guarda el detalle en `eval/resultados_recuperacion.json`. Objetivo de la guía: ≥ 85 %. También registra la distancia del mejor resultado en las preguntas que deben abstenerse, para fijar el umbral de silencio.

| Fecha | Modelo | hit@5 | Observaciones |
| --- | --- | --- | --- |
| 28/10/2026 (línea base) | multilingual-e5-small, sin filtro de tema | **12/13 = 92 %** | Único fallo: P07 (combinada, despido + vacaciones) |

### Diagnóstico de la línea base

| Pregunta | Resultado | Diagnóstico |
| --- | --- | --- |
| P07 · «Me despidieron después de 4 años y nunca tomé vacaciones» | ✗ Esperaba Arts. 188 y 71; recuperó 75, 190, 72, 69 y 74 | **Falla de recuperación** en una pregunta combinada: la parte de vacaciones domina la dirección de la pregunta y desplaza al Art. 188 |
| P11 · «Me botaron sin visto bueno después de 3 años» | ✓ Art. 188 en el puesto 3 | Encuentra el artículo sin compartir palabras con él; el Art. 172 (visto bueno) queda antes |
| P12 · vacaciones no gozadas | ✓ Art. 71 en el puesto 5 | Recuperado al límite: los Arts. 72, 77, 75 y 74 (también de vacaciones) quedan antes |

**Umbral de silencio.** En las preguntas que deben abstenerse (P13–P19), el mejor resultado quedó a una distancia de 0,126 a 0,186, igual o más cerca que muchas preguntas con respuesta. El modelo E5 produce distancias muy juntas, por lo que **un umbral de distancia no basta para decidir el silencio**: la abstención se decidirá en la generación (el modelo indica si los fragmentos responden la pregunta) y con la verificación de que el artículo citado esté entre los recuperados.

**Mejoras previstas (jueves 29), una por una y medidas:** 1) quitar del texto que se convierte en vector las anotaciones de reforma («(Sustituido por el Art. 21 de la Ley s/n…)») y anteponer el capítulo; 2) filtrar por el alcance del producto (jornada, vacaciones, remuneración, décimos, despido) antes del top-k.

## Cómo reconstruir

```powershell
pip install -r requirements.txt
py scripts/ingest.py
py eval/run_eval.py
```

La primera vez se descarga el modelo de embeddings (unos 470 MB). Hay que volver a correr `ingest.py` si cambia el PDF o el modelo.
