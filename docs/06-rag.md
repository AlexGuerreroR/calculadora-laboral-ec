# RAG: base de conocimiento y recuperación

Proyecto: Calculadora Laboral EC · Caso 07 · Grupo 7 · Semana 3.

## Estado comprobado en la copia · 30/10/2026

Corpus activo actualizado: Código de Defensoría Pública con reforma **18/05/2026**,
699 artículos (618 vigentes y 81 derogados según edición), índice
`data/chroma-2026/`. Manifiesto `config/corpus.json`, hash del PDF y metadatos de
publicación, corte normativo, consulta y estado declarado. Diez artículos del
producto contrastados e idénticos al corpus anterior; no cambian las fórmulas.
La fecha de corte no se confunde con una certificación de reformas posteriores.

- `/explicar` recalcula las entradas, recupera los artículos configurados para ese
  cálculo y entrega al modelo un JSON con resultado y fragmentos identificados.
- Se usa `app/prompts/rag_v3.md`; `rag_v1.md` y `rag_v2.md` se conservan como versiones
  RAG y `system_v3.md` se conserva para la comparación
  histórica de semana 2, no es el prompt del nuevo flujo RAG.
- Para décimo tercero se exige Art. 111; para décimo cuarto, Art. 113; para
  vacaciones, Arts. 69 y 71. La lista y top-k están en `config/parametros.yaml`.
- Horas adicionales exige Art. 55. Liquidación recupera Arts. 69, 71, 111, 113
  y 185; añade 188 para despido intempestivo y 55 cuando hay horas pendientes.
  La búsqueda exacta amplía el número de resultados cuando hacen falta más de
  cinco artículos. Se verificó con el índice real para C08, C09 y C10, sin API.
  `rag_v3` añade los nombres y límites de estos cálculos y preserva la corrección
  de nombre de v2. Las pruebas reales anteriores corresponden a sus versiones
  registradas; no se atribuyen a v3.
- El buscador devuelve identificador, documento, artículo, texto, URL y versión.
  La búsqueda exacta mantiene los filtros de vigencia y tema combinados.
- El servidor rechaza citas ajenas a los fragmentos recuperados y montos USD que
  no figuren en los datos del cálculo. Los números de artículos no habilitan dinero.
  Estos controles no demuestran por sí solos que cada frase sea fiel a la fuente.
- Sin todos los artículos necesarios, se abstiene antes de crear el cliente LLM.
  Si el índice no está disponible, devuelve 503 y conserva el cálculo separado.
- El frontend muestra las fuentes citadas, su versión y el texto exacto desplegable.
- Se descargó el PDF de la URL oficial configurada y se reconstruyó el índice:
  692 fragmentos, 610 marcados vigentes según esa edición y 82 derogados.
- La línea base semántica del 30/10 obtuvo 12/13 = 92,3 % (hit@5), con fallo P07.
  La recuperación actual del agente conserva la pregunta original y añade los
  artículos de los temas reconocidos. La comprobación local posterior obtuvo
  13/13 con **todos** los artículos esperados. Para temas reconocidos entrega
  solo los artículos pertinentes; Art. 75 se añade cuando se pregunta por acumular
  vacaciones. No se rellenan los huecos con artículos de materias distintas.
- Pasaron 50 comprobaciones locales de RAG, endpoint con dobles, fragmentación
  y aislamiento de rutas (1,59 s), sin consumo de API.
  Esta comprobación local no midió generación con un proveedor. Posteriormente se
  probaron tres explicaciones reales con v1 y se repitió el décimo tercero con v2;
  resultados y corrección en [la bitácora](10-bitacora-copia.md), grupo C.
  Las corridas generativas posteriores, sus fallos y el cierre están en
  `docs/07-evaluacion.md`; las cifras históricas no se atribuyen a los prompts actuales.

**Límite normativo:** la edición anterior indicaba reforma de 2023 y se conserva
para contraste. La activa indica 18/05/2026. `vigente` detecta derogación según
la edición consultada; no sustituye una certificación jurídica ni prueba que no
existan reformas posteriores al corte. Contraste cerrado en `04-fuentes.md`.

**Archivos locales:** las dependencias nuevas se instalaron en `.deps-rag/` y el
modelo se descargó en `.cache/modelos/`, dentro de la copia. No se modificó `.venv`.
El índice permanece en `data/chroma/`. Las rutas se validan antes de abrir Chroma.

## Consulta normativa del agente

`consultar_normativa` usa `recuperar_normativa`, que combina la pregunta original
con artículos por tema configurados, entrega sus
identificadores al prompt `normativa_v3` y valida `TextoNormativo`. Sin respaldo
o con una cita ajena a los fragmentos, se abstiene. La consulta normativa no
publica dinero ni operaciones aritméticas nuevas: los valores personalizados
se resuelven mediante las herramientas con datos del formulario. Dos comparaciones
sin importe monetario admiten datos declarados inequívocos del texto: años para
días anuales de vacaciones y horas diarias para exceso sobre la jornada general.
Pydantic valida esas entradas y Python hace las operaciones. Los resultados se
entregan al modelo identificados como herramientas, nunca como fuentes normativas.

Hay una comprobación conservadora de cantidades con unidad (días, horas, meses,
años, remuneraciones y porcentajes) contra el texto citado. Reconoce equivalencias
básicas como «quince días» y «15 días». Es un filtro literal, no una prueba
semántica completa de que la norma aplica al caso; puede producir abstenciones
adicionales y debe evaluarse con las preguntas de referencia.

El agente usa actualmente `agente_v4` para decidir herramientas y `rag_v3` para explicar
cálculos. Sus pruebas iniciales usan dobles de modelo y buscador. Una prueba real
posterior completó la explicación del décimo tercero con `calculo-0`, 600,00 USD
y cita `art-111` del índice real. La bitácora F5 registra versiones y consumo.
Las mediciones de recuperación y llamadas reales conservan su alcance y versión;
una consulta aprobada no acredita automáticamente las métricas del agente.

La consulta real citada corresponde a `agente_v2`. `agente_v3` conserva el
protocolo corregido y añade la solicitud de vista previa PDF; esta extensión
se comprobó con un doble, sin consumo adicional de API. La preparación consulta
las fuentes del índice local y congela sus referencias junto al cálculo; el PDF
no incorpora texto libre del modelo ni reproduce los artículos completos.

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

`eval/run_eval.py` mide la **recuperación correcta (hit@5)** con las 20 preguntas de `eval/preguntas.csv` y guarda el detalle en `eval/resultados_recuperacion.json`. Objetivo de la guía: ≥ 85 %. Esta cifra mide solo la recuperación: todavía no mide si la respuesta final es correcta, si cita bien ni si resiste una inyección; esas métricas van en `docs/07-evaluacion.md`. También registra la distancia del mejor resultado en las preguntas que deben abstenerse, para fijar el umbral de silencio.

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

**Mejoras propuestas el jueves 29, todavía no aplicadas:** 1) quitar del texto que se convierte en vector las anotaciones de reforma («(Sustituido por el Art. 21 de la Ley s/n…)») y anteponer el capítulo; 2) filtrar por el alcance del producto (jornada, vacaciones, remuneración, décimos, despido) antes del top-k. El nuevo explicador de cálculos usa artículos exactos configurados; la recuperación semántica general conserva esta línea base y su fallo P07.

## Cómo reconstruir

```powershell
pip install -r requirements.txt
py scripts/ingest.py
py eval/run_eval.py
```

La primera vez se descarga el modelo de embeddings (unos 470 MB). Hay que volver a correr `ingest.py` si cambia el PDF o el modelo.

Los dos scripts leen `EMBEDDING_MODEL` y `CHROMA_PATH` del `.env` (`retriever.cargar_entorno()`), igual que el servidor. Así se indexa y se busca con el mismo modelo y en la misma carpeta. Una variable definida en la terminal tiene prioridad sobre el `.env`.
