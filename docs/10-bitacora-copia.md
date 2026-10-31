# Bitácora de cambios de la copia

Fecha: 30 de octubre de 2026. Proyecto: Calculadora Laboral EC.

## Alcance y forma de incorporar los cambios

Esta bitácora registra trabajo realizado exclusivamente dentro de
`Proyecto_Titulación_copia/calculadora-laboral-ec`. No se ha inspeccionado ni
modificado el proyecto original y no se han realizado operaciones en GitHub.
La copia recibida no contiene `.git`: los grupos siguientes son una propuesta
para futuros commits, no commits ya creados ni diferencias contra el remoto.

Las rutas son relativas a la raíz de la aplicación. Para incorporar cada grupo
al repositorio local, revisar primero su diferencia con la versión que exista
allí. Si un archivo pertenece a varios grupos, seleccionar los bloques indicados;
copiar el archivo completo incorporaría también cambios de otros grupos.
Verificar cada grupo antes de preparar el siguiente. La publicación remota queda
para una autorización posterior: esta bitácora no autoriza modificar el original
ni realizar commits o push.

## Grupo A: aislamiento de rutas

Propósito: impedir que el índice y los archivos de ingesta/evaluación apunten
fuera de la copia, incluso mediante `..` o enlaces que resuelvan fuera.

| Archivo | Cambios que pertenecen a este grupo |
| --- | --- |
| `app/services/retriever.py` | Añadir `validar_ruta_copia`, usarla en `ruta_indice` y validar antes de abrir el cliente Chroma. |
| `scripts/ingest.py` | Validar índice y ruta del PDF antes de leer, descargar o reconstruir. |
| `eval/run_eval.py` | Validar índice, CSV de entrada y JSON de resultados antes de trabajar; cerrar el CSV con `with`. |
| `tests/test_rutas_copia.py` | Nuevo: rutas internas/externas, raíz, escapes relativos, rutas ambiguas de Windows, enlaces simulados y rechazo antes de efectos. |

Verificación realizada: 14 pruebas de aislamiento aprobadas. No se utilizó el
intérprete del `.venv` copiado. `.venv/pyvenv.cfg` conserva una referencia histórica
al original; no se modificó ni se siguió hacia ese proyecto.

## Grupo B: conectar RAG con la explicación y la interfaz

Propósito: que `/explicar` use artículos recuperados e identificados, verifique
las citas del modelo y muestre sus fuentes. Sin respaldo suficiente, se abstiene.

| Archivo | Cambio |
| --- | --- |
| `app/services/retriever.py` | Devolver ID y metadatos completos; combinar correctamente filtros de tema y vigencia; caché del modelo dentro de la copia; desactivar telemetría anónima de Chroma. Estos bloques son adicionales al grupo A. |
| `app/services/rag.py` | Nuevo: recuperación de artículos del cálculo, construcción de contexto JSON, validación de citas y montos explícitos USD, llamada con prompt configurado. |
| `app/schemas.py` | Añadir `FuenteRAG` y `ExplicacionRAG` con identificadores de citas. |
| `app/routers/explicar.py` | Conectar recuperación y generación después del recálculo; devolver fuentes; abstenerse sin respaldo y dar error comprensible si falla el índice. |
| `app/prompts/rag_v1.md` | Nuevo: primera versión del prompt RAG; se conserva como antecedente de la prueba real. |
| `config/parametros.yaml` | Añadir `rag`, top-k y artículos exigidos para cada cálculo. En este grupo, el prompt inicial es `rag_v1`; el cambio a `rag_v2` pertenece al grupo C. |
| `frontend/index.html` | Añadir sección desplegable de fuentes. |
| `frontend/app.js` | Mostrar documento, artículo, fragmento, versión y enlace HTTPS mediante nodos de texto. |
| `tests/test_rag.py` | Nuevo: citas y montos incorrectos, metadatos y abstención sin llamar al proveedor. |
| `tests/test_explicar.py` | Adaptar el doble a `ExplicacionRAG`, inyectar fuentes y comprobar su retorno. |

Verificación realizada: 50 comprobaciones locales aprobadas en 1,59 segundos
(RAG, endpoint con dobles, fragmentación y aislamiento). Sintaxis de `frontend/app.js`
comprobada con `node --check`. Estas pruebas usaron fuentes/modelo simulados cuando
correspondía; no acreditan las métricas de generación con un proveedor real.

## Grupo C: corrección tras la prueba con proveedor real

Prueba inicial con `rag_v1`: tres solicitudes reales a `/explicar`, usando datos
ficticios y el índice real. Gemini falló por tiempos de espera y un error 503;
Groq respondió como respaldo en las tres solicitudes.

| Caso | Total | Citas | Observación de la revisión |
| --- | --- | --- | --- |
| Décimo tercero, 12 remuneraciones de 600 | 600,00 USD | Art. 111 | El modelo terminó llamándolo «valor de vacaciones». Monto y cita correctos, explicación no aprobada. |
| Décimo cuarto, 6 meses, Costa/Galápagos | 241,00 USD | Art. 113 | Respuesta revisada sin la confusión anterior. |
| Vacaciones, sueldo 600, 01/10/2025 a 01/10/2026 | 300,00 USD | Arts. 69 y 71 | Respuesta revisada sin la confusión anterior. |

Instrucción ambigua identificada: `rag_v1` indicaba de forma general usar «valor de vacaciones».
La corrección limita ese nombre al cálculo de vacaciones y explicita el nombre
que corresponde a cada `resultado.tipo`.

| Archivo | Cambio |
| --- | --- |
| `app/prompts/rag_v2.md` | Nuevo: nombres condicionales según tipo y comprobación final de coherencia; conserva `rag_v1` para trazabilidad. |
| `config/parametros.yaml` | Cambiar solamente `rag.prompt` de `rag_v1` a `rag_v2`. |
| `.env` | Configuración local autorizada: `LLM_PRINCIPAL=groq`, `LLM_RESPALDO=gemini`. Se conservan las claves sin mostrarlas. **No incorporar este archivo a Git.** |
| `README.md` y `docs/06-rag.md` | Actualizar la referencia al prompt activo y enlazar esta bitácora para los resultados con proveedor real. |

Repetición real del décimo tercero con `rag_v2`, realizada el 30/10/2026:

- Endpoint `/explicar`: HTTP 200, estado `ok`.
- Proveedor: Groq, modelo `openai/gpt-oss-120b`, primer intento, 1.224 ms de llamada.
- Entradas ficticias: 12 remuneraciones de 600. Resultado del código: 600,00 USD.
- Respuesta: «décima tercera remuneración», sin confundirla con vacaciones.
  Los pasos conservaron 7.200,00 USD de suma y 600,00 USD de total.
- Cita e identificador devueltos: Art. 111 y `art-111`; fuente real recuperada.
- Consumo registrado: 1.171 tokens de entrada y 195 de salida.
- SHA-256 de `app/prompts/rag_v2.md` utilizado:
  `1cc1673fee614c69b81288c1917710a18f44d83e4c2253d3248145cdc9f4b00c`.
- Resultado de esta repetición: aprobado. No se repitieron décimo cuarto ni
  vacaciones con v2, ni se ejecutó la evaluación generativa completa.

No se ha cambiado el código de cálculo ni añadido nuevas herramientas. El ajuste
del nombre está en el prompt; una repetición correcta no garantiza todas las
respuestas futuras del modelo.

## Grupo D: documentación y resultado de recuperación

| Archivo | Cambio |
| --- | --- |
| `README.md` | Estado parcial de semana 3, preparación del entorno de esta copia, ejecución y límites de la verificación. |
| `docs/06-rag.md` | Flujo conectado, fuentes, abstención, métricas reales y limitación normativa. |
| `eval/resultados_recuperacion.json` | Resultado realmente ejecutado el 30/10: 12/13 = 92,3 % en hit@5. P07 sigue fallando. |
| `docs/10-bitacora-copia.md` | Este registro para incorporar los cambios por grupos y continuar documentando ajustes. |

La recuperación cuenta encontrar al menos un artículo esperado, no todos los de
una pregunta combinada. Las 20 preguntas fueron consultadas al índice; no se ha
ejecutado una evaluación generativa de las 20 con el proveedor.

## Archivos locales que no forman parte de los commits propuestos

- `.env`: contiene secretos locales; no copiar a la documentación ni publicar.
- `.venv/`: entorno recibido; no se modificó.
- `.deps-rag/`: dependencias instaladas localmente. Principales: PyMuPDF 1.28.2,
  ChromaDB 1.5.9 y sentence-transformers 5.7.0, dentro de los rangos declarados.
- `.cache/`: descargas y modelo `intfloat/multilingual-e5-small`.
- `data/chroma/`: índice local generado con 692 fragmentos (610 etiquetados como
  vigentes según esa edición y 82 derogados).
- `data/raw/CODIGO_DEL_TRABAJO.pdf`: fuente descargada de la URL ministerial
  indicada por el proyecto; ya está excluida en `.gitignore`.
- `.tmp-aislamiento-*/`, `.tmp-rag-*/`, `.tmp-calculos-*/`, `.tmp-agente-*/`, `.tmp-resumen-*/` y `logs/`: temporales y registros de ejecución.
- `output/pdf/resumen-c09-demo.pdf`: ejemplo generado y revisado, excluido por la regla `output/` existente.

El `.gitignore` recibido no cubre expresamente `.deps-rag/`, `.cache/` ni los
directorios `.tmp-*`. Antes de preparar futuros commits, excluirlos mediante una
revisión autorizada del `.gitignore`; no usar una inclusión masiva de archivos.

## Grupo E: horas adicionales y estimación de liquidación

Etapa autorizada después de cerrar RAG. Se implementaron cálculos, entradas,
endpoints y formularios. No se inició agente ni generación de PDF y no se
consumió API en esta etapa. El original y GitHub permanecen intactos.

### E1: motor y contratos de cálculo

| Archivo | Cambio |
| --- | --- |
| `app/schemas.py` | Añadir `EntradaHoras` y `EntradaLiquidacion`, ampliar los tipos de `ResultadoCalculo`; importes nuevos con `Decimal`, saldos obligatorios, confirmación, fechas y coherencia de días naturales/comerciales. |
| `app/tools/horas.py` | Nuevo: hora ordinaria sin redondeo intermedio, recargos desde YAML, redondeo por rubro y suma final. |
| `app/tools/liquidacion.py` | Nuevo: antigüedad y fracción, desahucio, indemnización, décimos, saldos de vacaciones, horas, salario pendiente y descuentos; total neto determinista. |
| `app/routers/calculos.py` | Añadir POST `/calculos/horas` y `/calculos/liquidacion`, con esquemas y errores 422. |
| `config/parametros.yaml` | Añadir fuente de saldos y límite de tamaño de explicación para liquidación (6.000 caracteres). Tasas, divisores y topes se leen de configuración. |

La liquidación no deduce que los saldos faltantes son cero: deben informarse
incluso cuando sean cero. La base del décimo tercero es la suma de remuneraciones
cuyo décimo sigue pendiente, no el salario adeudado. El décimo cuarto recibe días
pendientes del período regional. Vacaciones recibe saldos separados de días base
y adicionales; se valoran con remuneración fija. Se rechazan descuentos superiores
al total de rubros calculado.

Los motivos soportados son renuncia con desahucio y despido intempestivo,
seleccionados por el usuario. El sistema no determina su procedencia legal.
Se conserva el criterio de años completos para desahucio del Excel. Para despido,
una fracción posterior a tres años se cuenta como un año adicional, con mínimo
y tope de remuneraciones de configuración. Se contempló el aniversario bisiesto.

### E2: formularios

| Archivo | Cambio |
| --- | --- |
| `frontend/index.html` | Añadir opciones y formularios de horas/liquidación, ayudas, saldos explícitos y confirmación; actualizar alcance. |
| `frontend/app.js` | Construir solicitudes nuevas, rechazar vacíos antes de convertir números, cargar ejemplos C09/C10 y exigir confirmación; invalidar resultado anterior al cambiar tipo o iniciar otro cálculo. |

Ejemplos C09/C10: al pulsar el botón se cargan datos ficticios del Excel con los
supuestos visibles, y la casilla de confirmación queda desmarcada. C10 conserva
saldo cero de vacaciones adicionales: el resultado avisa que debe comprobarse
que fueron gozadas o pagadas, sin negar el derecho por antigüedad.

### E3: integrar los resultados con el explicador RAG

| Archivo | Cambio |
| --- | --- |
| `app/routers/explicar.py` | Recalcular horas y liquidación en el servidor; aplicar límite configurado para la entrada de liquidación. |
| `app/services/rag.py` | Recuperar artículos por tipo y motivo, añadir fuente de horas pendientes y no truncar los artículos exactos necesarios al top-5. |
| `app/prompts/rag_v3.md` | Nuevo: nombres de horas/liquidación y límites del supuesto; conserva la distinción de nombres de v2. |
| `config/parametros.yaml` | Añadir artículos de horas/liquidación y adicionales por motivo; activar `rag_v3`. Este bloque se incorpora después de E1. |

Verificación con el índice real, sin API: C08 recuperó 55; C09 recuperó 69, 71,
111, 113 y 185; C10 recuperó los anteriores más 188. Los resultados serializados
midieron 638, 1.671 y 1.829 caracteres respectivamente. No se probó generación
real con v3; las pruebas reales de los grupos anteriores no se presentan como suyas.

### E4: pruebas y documentación

| Archivo | Cambio |
| --- | --- |
| `tests/test_horas.py` | Nuevo: C08, fracciones de hora, entradas inválidas y cambio de recargo en configuración mediante doble. |
| `tests/test_liquidacion.py` | Nuevo: C01–C10 por HTTP, límites de indemnización, fechas, saldos omitidos, descuentos, febrero comercial, aniversario bisiesto, recálculo y recuperación por motivo. |
| `README.md` | Endpoints, alcance, límites y comando de verificación de esta etapa. |
| `docs/03-arquitectura.md` | Distinguir alcance histórico del MVP y cálculo ya implementado en la copia. |
| `docs/06-rag.md` | Registrar el prompt activo y fuentes de los tipos nuevos. |
| `docs/10-bitacora-copia.md` | Este registro de la etapa y sus grupos para una incorporación parcial posterior. |

Comando ejecutado desde la copia, con intérprete externo, dependencias locales,
plugins automáticos desactivados, modelos en modo offline y temporales locales:

```powershell
python -B -m pytest -q -p no:cacheprovider --basetemp=./.tmp-calculos-20261030-02 tests/test_horas.py tests/test_liquidacion.py tests/test_calculos.py tests/test_endpoints_calculo.py tests/test_explicar.py tests/test_rag.py tests/test_frontend.py
```

Resultado: **115 pruebas aprobadas en 2,03 s**, sin proveedor real. Sintaxis JS
verificada con `node --check`. También se ejecutó en memoria el JS de los
formularios con un DOM simulado: rutas y campos de C08/C09/C10, confirmación
obligatoria y rechazo de un campo vacío. Esto no constituye revisión visual en navegador.

Fuente de los valores esperados: `docs/evidencias/semana-1/B4_Resolución de casos.xlsx`,
hoja `Resultados `, C4:C13, y fórmulas/desarrollo de `Calculos y fuentes`. Se leyó
el archivo sin modificarlo ni recalcularlo. Se trazaron los resultados a los datos
y fórmulas registrados. Los diez resultados por HTTP coinciden dentro de ±0,01 USD:

| Caso | Resultado USD |
| --- | ---: |
| C01 | 600,00 |
| C02 | 250,00 |
| C03 | 737,50 |
| C04 | 482,00 |
| C05 | 241,00 |
| C06 | 300,00 |
| C07 | 510,00 |
| C08 | 76,67 |
| C09 | 1.130,33 |
| C10 | 9.331,84 |

Los casos C09/C10 declaran último sueldo y períodos anteriores pagados. Sus saldos
no se generalizan. La coincidencia prueba los ejercicios con esos supuestos;
no certifica una liquidación jurídicamente aplicable a cualquier relación laboral.

## Grupo F: agente de alcance controlado

Etapa autorizada después de los cálculos. El agente decide qué herramienta pedir
en un bucle; Python valida y ejecuta funciones específicas. La consulta del
cliente no puede enviar un historial que suplante mensajes de sistema o herramientas.
La verificación local usa dobles. Las pruebas reales posteriores, con su
autorización y límite de consumo, se registran al final de este grupo.

### F1: contrato y cliente de herramientas

| Archivo | Cambio |
| --- | --- |
| `app/schemas.py` | Añadir contrato de consulta, argumentos de búsqueda/explicación, texto normativo y respuesta estructurada con resultados, fuentes, pasos y estados. |
| `app/services/llm.py` | Añadir `generar_herramientas`; aceptar respuestas sin texto cuando contienen tool calls solicitadas y permitir exigir herramienta en la primera vuelta. Conservar reintentos, respaldo y registro de consumo. |
| `config/parametros.yaml` | Nueva sección `agente`: prompts, topes, tamaño de entrada/contexto, tasa y patrones de alcance. |

### F2: servicio y endpoint

| Archivo | Cambio |
| --- | --- |
| `app/services/agente.py` | Nuevo: siete herramientas permitidas, esquemas Pydantic, comprobación contra entradas confirmadas, bucle con presupuesto, consulta normativa con citas y resultado ensamblado por el servidor. |
| `app/routers/agente.py` | Nuevo: POST `/agente`, validación, recálculo del contexto adjunto, tasa, guardas y errores sin detalles internos. |
| `app/main.py` | Registrar el router antes de montar el frontend estático. |
| `app/prompts/agente_v1.md` | Nuevo: planificación de herramientas, datos sin autoridad para cambiar permisos, sin cálculos libres ni valores supuestos. |
| `app/prompts/agente_v2.md` | Nuevo tras la prueba real: contexto con ID explícito, llamada de explicación con ese ID y solicitud de datos mediante herramienta. Se conserva v1 como antecedente. |
| `app/prompts/normativa_v1.md` | Nuevo: respuesta normativa con fuentes y abstención, sin montos ni operaciones para un caso particular. |

La lista cerrada contiene `consultar_normativa`, `calcular_decimos`,
`calcular_vacaciones`, `calcular_horas`, `estimar_liquidacion` y
`explicar_resultado` y `solicitar_datos`. No hay eval, exec, SQL libre, comandos, escritura de
registros, envío, pagos, eliminación ni generación de archivos.

Para calcular, los argumentos deben coincidir con el formulario adjunto, cuyo
resultado se recalcula en el servidor. Se rechaza completar o cambiar sueldo,
fechas, cantidades, región o saldos a partir del texto libre. Los resultados se
identifican explícitamente dentro de cada consulta (`calculo_confirmado.id` y
`calculo_confirmado.resultado`), para que explicar_resultado solo acepte
cálculos existentes. La interfaz publica resultados de herramientas y
explicaciones verificadas; no publica el texto final libre del planificador.

Límites actuales: seis vueltas, ocho llamadas lógicas al modelo, cuatro
herramientas por vuelta, límites de argumentos/contexto y cuatro consultas por
minuto por cliente. El presupuesto lógico incluye las solicitudes normativas y
explicaciones internas; cada solicitud conserva los reintentos/corrección JSON
del cliente. No representa un máximo de ocho peticiones HTTP al proveedor.

La consulta normativa verifica IDs y artículos citados, rechaza montos y nuevas
operaciones y compara cantidades con unidad con el texto de la fuente. Esta
comparación es literal con equivalencias básicas de números escritos en palabras;
no prueba fidelidad semántica completa ni elimina la necesidad de evaluación.
Las guardas léxicas de dominio, inyección y disputa son conservadoras y no se
presentan como 100 % de resistencia ante cualquier formulación posible.

### F3: interfaz y confirmación de datos

| Archivo | Cambio |
| --- | --- |
| `frontend/index.html` | Consulta independiente al asistente, adjuntar el último cálculo, resultados y fuentes, pasos observables y revisión de saldos. |
| `frontend/app.js` | Enviar la consulta, mostrar datos por nodos de texto, fuentes verificadas, confirmación/cancelación con la misma instantánea de datos y exclusión de solicitudes simultáneas. |
| `frontend/styles.css` | Estilo de la consulta, textarea, fuentes y revisión de saldos. |

La confirmación de uso de una liquidación es un campo de la solicitud del
usuario; no se toma del texto del modelo. Sin ella, la herramienta no se ejecuta.
Si un lote contiene una herramienta pendiente y otra de lectura, se produce una
respuesta por cada tool_call_id antes de detener el flujo. El usuario revisa el
resumen y puede confirmar o cancelar. Confirmar inicia una consulta nueva con los
mismos datos y autorización explícita, sin historial persistido.

Esta revisión de datos no es una acción con efectos: no registra un acta, no
envía archivos ni paga. El control de confirmación antes del futuro PDF/otras
acciones con efectos se implementará y probará en su propia etapa.

### F4: comprobaciones y documentación

| Archivo | Cambio |
| --- | --- |
| `tests/test_agente.py` | Nuevo: bucle, lista cerrada, esquemas, datos faltantes/alterados, cálculos reales con modelo simulado, citas y cantidades, lote con confirmación pendiente, topes, guardas, endpoint y tool calls sin texto. |
| `README.md` | Estado, endpoint, uso, límites y comando de verificación del agente. |
| `docs/03-arquitectura.md` | Distinguir bucle implementado y acciones futuras. |
| `docs/06-rag.md` | Alcance y límites de la consulta normativa del agente. |
| `docs/10-bitacora-copia.md` | Este registro para incorporar F1–F4 por separado. |

Comando ejecutado desde la copia con dependencias locales, plugins automáticos
desactivados y modelos offline:

```powershell
python -B -m pytest -q -p no:cacheprovider --basetemp=./.tmp-agente-20261030-04 tests/test_agente.py tests/test_llm.py tests/test_rag.py tests/test_explicar.py tests/test_liquidacion.py tests/test_frontend.py
```

Resultado final local: **101 pruebas aprobadas en 2,24 s**, sin proveedor real. Es una
selección distinta de las 115 de la etapa E. Entre las comprobaciones:

- Cálculo y explicación en varias vueltas, con montos reales de Python.
- Datos propuestos por el modelo distintos del formulario: no se calculan.
- Confirmación pendiente en un lote: todas las llamadas quedan respondidas,
  la liquidación no se ejecuta y la lectura sí puede completarse.
- Un texto del modelo que dice que el usuario confirmó no sustituye el campo
  explícito de confirmación de la solicitud.
- Herramientas inexistentes, JSON/argumentos inválidos, topes y datos manipulados.
- Fuera de dominio, inyección y disputa probados: no se crea cliente ni se gasta API.
- Cantidad nueva (17/diecisiete días) ausente en una fuente que dice quince días:
  se rechaza como respuesta normativa; se permite citar la regla literal de 15 días.
- El cliente acepta una llamada de herramienta sin contenido textual asociado.

Se comprobó en memoria el JS real con un DOM y transporte simulados: consulta
independiente, rechazo visible, confirmación tras clic conservando datos y
cancelación sin otra solicitud. No constituye revisión visual en navegador ni
prueba con proveedor real.

### F5: diagnóstico real y ajuste del protocolo

El usuario autorizó una consulta real del agente con Groq y hasta cuatro
solicitudes lógicas. Datos ficticios: décimo tercero de 12 remuneraciones de
600, total calculado por Python de 600,00 USD. No se usó Gemini como respaldo
en estas pruebas y no se modificaron los límites guardados de configuración.

1. Primera solicitud: Groq respondió con texto sin herramientas. El servidor no
   publicó ese texto: devolvió `pedir_datos`. No se considera consulta aprobada.
2. Segunda solicitud: se exigió herramienta en la primera vuelta. Groq devolvió
   HTTP 400, `tool_use_failed`; el endpoint respondió 503 genérico.
3. Tercera solicitud, diagnóstico limitado a una llamada lógica: el proveedor
   indicó que el modelo pedía un identificador en vez de llamar una función.
   El ID solo estaba descrito en el prompt; faltaba en el JSON del contexto.

Corrección posterior: incluir `calculo_confirmado.id` explícito, activar
`agente_v2`, exigir herramienta en la primera vuelta y añadir `solicitar_datos`
para que una falta real de datos tenga una salida estructurada compatible con
esa exigencia. Las 101 pruebas locales anteriores corresponden a esta corrección.

Tras las tres solicitudes de diagnóstico, el usuario aprobó ampliar el presupuesto
de cuatro a seis solicitudes lógicas totales. Se repitió la misma consulta con
la versión corregida y un máximo de tres solicitudes adicionales, sin cambiar
los límites guardados ni permitir respaldo con Gemini en esta prueba.

**Resultado real de la versión corregida: aprobado para este caso.**

- Proveedor: Groq, modelo `openai/gpt-oss-120b`.
- Endpoint `/agente`: HTTP 200, estado `completado`.
- Primera vuelta: el modelo solicitó `explicar_resultado` con `calculo_id=calculo-0`.
- La herramienta recuperó el Art. 111 del índice real y generó la explicación
  usando `rag_v3`; las citas y valores pasaron los controles del servidor.
- Segunda vuelta: el modelo terminó; el servidor devolvió el cálculo y su
  explicación verificada, sin publicar el texto final libre del planificador.
- Resultado conservado de Python: 600,00 USD; suma previa: 7.200,00 USD.
- Beneficio correctamente llamado décimo tercero, fuente `art-111`, sin faltantes.
- Dos vueltas y tres solicitudes lógicas: elección de herramienta, generación
  RAG dentro de la herramienta y cierre. Las tres respondieron al primer intento.
- Latencias de proveedor: 793, 1.030 y 1.100 ms. No representan el tiempo total
  de la consulta, que incluye la carga local del modelo de embeddings.
- Tokens por solicitud (entrada/salida): 1.794/53, 1.244/209 y 2.236/253.
  Total de esta repetición: 5.274 de entrada y 515 de salida.
- SHA-256 de `agente_v2.md` utilizado:
  `d0467181743947555c2f95f850f80ff0c0bded98f43c72f0971b9668c4417952`.
- SHA-256 de `rag_v3.md` utilizado:
  `9e217ec13b5f187853a17e85428a9cfbc615a524b10903fe965351115e1ef5ff`.

Consumo lógico acumulado de diagnóstico y repetición: **6 de 6 autorizadas**.
No se realizaron solicitudes adicionales. Esta prueba no cubre con proveedor
real todas las herramientas, confirmación ni las 20 preguntas de evaluación.

## Grupo G: resumen PDF con confirmación humana

Etapa autorizada después del agente. Se instaló ReportLab 4.5.1 y Pillow 13.0.0
en `.deps-rag/` de la copia, con caché y temporales de instalación dentro de ella.
No se modificó `.venv`, no se utilizó el original y no se consumió API generativa.
El presupuesto de seis solicitudes del grupo F no se amplió ni se reutilizó aquí.

### G1: contratos, dependencias y preparación de datos

| Archivo | Cambio |
| --- | --- |
| `requirements.txt` | Declarar `reportlab>=4.4,<5` y tzdata para Windows, para la fecha local del PDF. |
| `config/parametros.yaml` | Nueva sección `resumen`: caducidad, límites de pendientes, tamaño, tasa y zona horaria. Activar `agente_v3`. |
| `app/schemas.py` | Solicitud de vista previa, token, confirmación estricta y vista previa tipada. El puente interno del agente al preparador se excluye de la respuesta JSON. |
| `app/services/resumen.py` | Nuevo: instantáneas en memoria, copia profunda de datos/fuentes, token aleatorio de un solo uso, propietario, caducidad y consumo atómico con bloqueo. |

La preparación recalcula el resultado en el servidor y conserva exactamente esa
instantánea y las fuentes recuperadas. No genera un PDF. Los datos faltantes del
cliente no se rellenan mediante un modelo, y el total/desglose/fundamento enviados
por el navegador no se usan como autoridad. Si no se recuperan fuentes, la vista
previa lo advierte y distingue el fundamento de configuración.

Límites actuales: 300 segundos de validez, 128 pendientes por proceso, cinco por
sesión y ocho preparaciones por minuto por cliente. Los caducados se purgan al
procesar otra operación. Confirmar/cancelar elimina la entrada inmediatamente;
reiniciar el proceso elimina todas. No hay persistencia ni historial de PDFs.

### G2: confirmación y generación

| Archivo | Cambio |
| --- | --- |
| `app/tools/resumen.py` | Nuevo: PDF con ReportLab, datos, total, desglose, fuentes/versiones y límites; marcado escapado, importación diferida y salida en memoria. También formatea los datos visibles de la vista previa. |
| `app/routers/resumen.py` | Nuevo: POST `/resumen/preparar`, `/resumen/confirmar` y `/resumen/cancelar`; recálculo, sesión, aprobación y descarga. |
| `app/main.py` | Registrar el router del resumen antes del frontend estático. |

Confirmar acepta únicamente token y `confirmar=true` como booleano real. No acepta
otro cálculo, un nuevo total, la palabra «true», un 1 ni una aprobación enviada
por el modelo. El token se asocia a una cookie aleatoria HttpOnly/SameSite Strict
(Secure bajo HTTPS), guardando el hash de sesión en el servidor. Otro navegador,
un token vencido o uno ya consumido no pueden generar el archivo.

El consumo del token es atómico: dos confirmaciones simultáneas no lo consumen
dos veces. Si falla la generación, no se revela el error interno y se necesita
preparar otra vista previa. El documento usa los valores revisados aunque el
archivo de configuración cambie antes de confirmar.

El PDF se devuelve como `application/pdf` adjunto, con `Cache-Control: no-store`.
La aplicación no guarda el archivo en disco ni lo envía a terceros. La descarga
se guarda en el navegador del usuario. No se llama a Gemini ni Groq para generar
el documento. Los artículos completos no se reproducen: se indican referencias,
versión y URL, además del fundamento del cálculo.

### G3: integración con el agente y la interfaz

| Archivo | Cambio |
| --- | --- |
| `app/services/agente.py` | Octava herramienta cerrada `generar_resumen`, con ID de cálculo existente. Solo devuelve una aprobación pendiente y la instantánea interna para preparar la vista previa. |
| `app/routers/agente.py` | Convertir la solicitud de resumen del agente en una vista previa ligada a la sesión; respetar errores HTTP del preparador. |
| `app/prompts/agente_v3.md` | Nuevo: conservar ID explícito y pedir vista previa PDF, sin atribuir confirmación al modelo. Se conserva v2, que fue la versión de la prueba real del grupo F. |
| `frontend/index.html` | Botón directo de PDF y panel de datos, desglose, fuentes, confirmación y cancelación; aviso de memoria temporal. |
| `frontend/app.js` | Preparar vista, exigir clic antes del POST de confirmación, descargar Blob, cancelar y controlar solicitudes simultáneas del resumen. El agente abre la misma vista sin aprobarla. |

El token de aprobación no se entrega al modelo ni aparece en sus mensajes de
herramientas. Si el lote contiene PDF pendiente y otra lectura, ambas llamadas
reciben respuesta antes de detenerse. El booleano `confirmar_liquidacion` de la
revisión de saldos del grupo F no sustituye la confirmación del PDF.

### G4: comprobaciones y ejemplo revisado

| Archivo | Cambio |
| --- | --- |
| `tests/test_resumen.py` | Nuevo: preparación, aprobación estricta, cancelación, caducidad, sesión, reutilización, consumo concurrente, instantánea estable, fallo de generación, PDFs reales e integración del agente con un doble. |
| `tests/test_agente.py` | Ampliar la lista cerrada esperada con `generar_resumen`. |
| `README.md` | Flujo de PDF, endpoints, dependencia, memoria temporal y comando de pruebas. |
| `docs/03-arquitectura.md` | Separar preparación por agente y generación tras aprobación humana. |
| `docs/06-rag.md` | Diferenciar la prueba real v2 y la extensión PDF v3 probada localmente. |
| `docs/09-decisiones.md` | Actualizar inventario: consulta libre, instantánea en memoria, cookie/token y PDF descargado; corregir afirmación de que no se conserva ningún dato. |
| `docs/10-bitacora-copia.md` | Este registro para incorporar G1–G4 por separado. |

Comando ejecutado con dependencias locales, plugins automáticos desactivados y
modelo de embeddings offline:

```powershell
python -B -m pytest -q -p no:cacheprovider --basetemp=./.tmp-resumen-20261030-01 tests/test_resumen.py tests/test_agente.py tests/test_rag.py tests/test_explicar.py tests/test_liquidacion.py tests/test_frontend.py
```

Resultado: **109 pruebas aprobadas en 2,77 s**, sin API generativa. Esta selección
es distinta de las selecciones de los grupos E/F. Se verificaron PDFs reales de
C01, C09 y C10 con extracción de texto, totales, referencias y límites. Preparar,
cancelar, confirmar con datos inválidos y usar otro navegador no generaron PDF.
La confirmación doble, el token vencido y el cambio de configuración también
se comprobaron. La integración del agente usó un doble y un lote de dos llamadas;
el PDF solo se produjo después del POST de confirmación.

Se comprobó el JS real en memoria con DOM y transporte simulados: preparar no
descarga, el clic de confirmación envía solo token y booleano, cancelar no produce
otra descarga y la respuesta del agente no aprueba automáticamente. Sintaxis
verificada con `node --check`; esto no es una revisión visual del navegador.

Se generó `output/pdf/resumen-c09-demo.pdf` mediante los endpoints reales,
confirmación de prueba e índice local real: total 1.130,33 USD, artículos 69, 71,
111, 113 y 185. Archivo de 5.325 bytes y dos páginas. Se renderizaron e inspeccionaron
visualmente ambas páginas en memoria: sin recortes, solapamientos ni bloques fuera
de página. El archivo está excluido por la regla `output/` del `.gitignore` recibido.
El ejemplo contiene datos ficticios y no debe incorporarse como código.

Limitación de despliegue: el almacén de confirmaciones es de un solo proceso.
El MVP debe usar un worker; varios workers o servidores requieren un almacén
compartido o un diseño equivalente. No se presenta esta solución como persistente.
La prueba real del agente v2 no se atribuye a v3: no se consumió API en esta etapa.

## Grupo H: evaluación reproducible de preguntas y cálculos

Autorización: corrida de las 20 preguntas con hasta 60 solicitudes lógicas a
Groq, con sus reintentos configurados y sin Gemini en esta corrida. La
configuración habitual de la aplicación conserva Groq principal y Gemini de
respaldo: se verificaron ambos nombres y modelos sin imprimir credenciales.
La exclusión del respaldo solo existe en la configuración temporal del evaluador.

| Archivo | Cambio y propósito |
| --- | --- |
| `eval/run_agente_real.py` | Nuevo: ejecutar las 20 preguntas originales con el servicio real, presupuesto global de 60, separación entre solicitudes, evidencia incremental, huellas de código/configuración/prompts y bloqueo de sobrescritura accidental. |
| `eval/resultados_agente_real_20261030.json` | Evidencia real de la corrida; contiene preguntas ficticias del conjunto, respuestas, fuentes y trazas. No contiene claves ni mensajes internos de excepciones. |
| `eval/casos_calculo.csv` | Congelar los diez casos de referencia existentes, con entradas y valores esperados del ejercicio Excel. |
| `eval/run_calculos.py` | Nuevo: reproducir el CSV por HTTP local con TestClient, sin API generativa. |
| `eval/resultados_calculos_20261030.json` | Evidencia de los diez endpoints: 10/10 dentro de USD 0,01. |
| `eval/revision_agente_20261030.json` | Revisión asistida de las veinte respuestas frente a su referencia, con motivos por fila. |
| `eval/resumir_evaluacion.py` y `eval/metricas_agente_20261030.json` | Reproducir indicadores desde evidencia y revisión separadas; no equiparar citas con corrección. |
| `eval/diagnosticar_agente.py` y `eval/diagnostico_P04_20261030.json` | Diagnóstico puntual posterior, máximo tres llamadas adicionales dentro del mismo límite global; no sobrescribe resultados de la corrida. |
| `docs/07-evaluacion.md` | Método, denominadores, limitaciones y resultados de la evaluación. |
| `docs/evidencias/semana-3/README.md` y `README.md` | Ubicar las evidencias y advertir los resultados pendientes de corrección. |

No se alteraron las preguntas, las respuestas esperadas, los prompts ni el motor
para facilitar esta corrida. Las preguntas se enviaron sin adjuntar formularios
inventados. El evaluador del agente invoca el servicio directamente: no acredita
el limitador HTTP ni la interfaz. La revisión semántica se distingue de la mera
presencia de citas y de la recuperación histórica hit@5.

Comandos de esta etapa, desde la copia y con el intérprete externo/dependencias
locales descritos en `docs/07-evaluacion.md`:

```powershell
py -3.14 -B eval/run_calculos.py
py -3.14 -B eval/run_agente_real.py
```

Resultado real: 20/20 preguntas procesadas, 24 solicitudes lógicas. Recuperación
con la pregunta original: 12/13 (92,31 %), tanto alguno como todos los artículos
esperados; esta cifra no mide la búsqueda interna reformulada. Respuesta correcta
con cita: 0/13. Abstención/derivación: 3/4. Fuera de dominio: 2/2. Inyección:
no obedece 2/2 órdenes, pero solo cumple 1/2 comportamientos de referencia porque
rechaza toda P20. El agente no alcanza la meta generativa de la guía.

Diagnóstico P04 posterior: 2 solicitudes adicionales, total **26/60**, sin
Gemini. La pregunta original recupera Art. 47, pero la reformulación del agente
recuperó 152, 1, dos innumerados tras 156 y 20. El modelo devolvió
`no_disponible` ante esos fragmentos. Se documentó como primera corrección
propuesta conservar la consulta original; no se alteró todavía el agente.
Las otras causas no se dan por demostradas sin sus trazas. No se ejecutó otra
batería de pruebas ni se consumieron las 34 solicitudes restantes.

## Grupo I: corregir los fallos reales y cerrar la semana 3

Se conservó la evidencia H sin mejorar sus cifras retrospectivamente. El usuario
pidió completar el proyecto conforme a la guía y autorizó hasta 32 solicitudes
Groq y 2 Gemini adicionales, manteniendo 60 totales. Después autorizó una tercera
prueba Gemini: techo global 61. La consulta de la lista de modelos fue una
operación de metadatos, sin generación ni solicitud lógica al modelo.

| Subgrupo y archivos | Cambio concreto |
| --- | --- |
| I1: `app/services/agente.py`, `config/parametros.yaml`, `app/prompts/agente_v4.md`, `app/prompts/normativa_v2.md` | Conservar pregunta original, recuperar artículos de todos los temas reconocidos, separar orientación normativa de importe personalizado, terminar sin llamada adicional cuando ya existe orientación validada. Se conservan v3/v1. |
| I2: `app/schemas.py`, `app/tools/vacaciones.py`, `app/services/agente.py` | Calcular días anuales con años de servicio explícitos mediante entrada Pydantic y Python. No inventar sueldo ni fechas, no confundir años con edad ni declarar vacaciones acumuladas. La respuesta normativa incluye el resultado estructurado `calculo_dias`. |
| I3: `app/services/agente.py`, `config/parametros.yaml` | Apartar órdenes hostiles entre comillas y validar la pregunta exterior; seguir rechazando órdenes directas. Abstenerse por documentos privados no cargados o reglas de aportes al IESS ausentes, en vez de clasificar todo como fuera de dominio. |
| I4: `app/services/agente.py`, `tests/test_agente_correcciones.py` | Completar la cita visible con metadatos de IDs válidos cuando el texto omite el artículo; rechazar artículos o IDs ajenos. Admitir días base/adicionales/totales realmente calculados por Python. Normalizar «ciento por ciento». |
| I5: `app/config.py`, `app/services/llm.py`, `.env.example`, `.env` solo local | Timeout del respaldo 45 s y principal sin cambio de timeout. Se ensayó Gemini 2.5 Flash (404) y se restableció Gemini 3.8 Flash en `.env`; principal Groq sin cambios. La plantilla explicita 3.8. No copiar `.env` al repositorio ni imprimir credenciales. |
| I6: `tests/test_agente.py`, `tests/test_agente_correcciones.py` | Regresiones del diagnóstico real y adaptación del caso de bucle para que siga verificando el límite en el flujo con cálculo adjunto. El rechazo de días no calculados se mantiene con 18 para una antigüedad cuyo resultado Python es 17. |
| I7: `eval/run_recuperacion_corregida.py`, `eval/recuperacion_corregida_20261030.json` | Recuperación del agente corregido con índice real y sin API: todos los artículos esperados en 13/13 preguntas con fuente. Esto aún no acredita calidad de respuestas. |
| I8: `eval/run_agente_corregido.py`, `eval/resultados_agente_corregido_20261030.json`, `eval/resultados_agente_final_20261030.json` | Conservar corrida parcial interrumpida y ejecutar nueva corrida con trazas internas, presupuesto restante y huellas de aplicación/configuración/prompts. |
| I9: `eval/comprobar_respaldo.py`, `eval/respaldo_real*_20261030.json`, `eval/modelos_respaldo_20261030.json` | Falla simulada del principal sin consumir Groq para comprobar Gemini real. Primera prueba: timeout; segunda: 404; tercera autorizada: 503. La lista de modelos se consultó sin generación. No se acredita disponibilidad del respaldo. |
| I10: `.gitignore` | Excluir dependencias locales, cachés y temporales de pruebas antes de una futura incorporación al repositorio. No se ejecutó Git. |

La primera corrida corregida se detuvo al detectar dos falsos rechazos del
validador. Se guardaron dos filas completas; se consumieron o iniciaron seis
solicitudes Groq. La número 32 se interrumpió en curso y se cuenta como consumida
conservadoramente aunque no quedó respuesta. No se elimina ni se califica esa
corrida parcial como una corrida de veinte preguntas.

Presupuesto al iniciar la corrida final: 26 históricas + 6 Groq de la corrida
parcial + 1 primera Gemini = 33. La final reserva máximo 26 Groq (hasta 59 en ese
contador), más las otras dos pruebas Gemini = máximo 61 reales/conservadoras.
Los reintentos HTTP mantienen su límite configurado; no se ocultan como nuevas
autorizaciones lógicas. No se amplió ningún límite sin autorización.

Verificación local final antes de la corrida: **145 pruebas aprobadas en 2,73 s**,
sin API. Selección: correcciones/agente/resumen/liquidación/frontend/RAG/explicar/
cliente LLM/configuración. Antes de esta última corrección hubo selecciones de
127 y 129: no se suman entre sí. Resultado generativo final pendiente al cierre
de esta anotación; se completará con las respuestas reales, no con los dobles.

### I11: segunda corrección y cierre de calidad

- `config/parametros.yaml` y `app/services/agente.py`: entregar solo artículos de
  los temas reconocidos; incorporar Art. 75 únicamente al preguntar por acumular
  vacaciones. Evita que trámites o condiciones de artículos periféricos desvíen
  una respuesta sobre el derecho consultado. Sin tema reconocido se conserva
  la búsqueda semántica original.
- `app/prompts/normativa_v3.md`: foco en lo preguntado, sin ampliar a trámites,
  sin deducir pérdida de derechos, sin citar resultados internos como normas.
- `app/tools/jornada.py`, `app/schemas.py`, `app/services/agente.py`: comparación
  tipada de horas diarias declaradas contra la referencia general configurada.
  Python calcula el exceso; no fija el importe ni determina si aplica un régimen
  excepcional. El resultado se publica como `calculo_jornada`.
- El servidor separa los nombres conocidos de resultados internos de las citas
  documentales, manteniendo la exigencia de una fuente real y rechazando otros
  IDs ajenos. No se convierten herramientas en leyes ni se autorizan citas inventadas.
- `app/config.py` y `.env.example`: modelo Gemini por defecto **3.6 Flash**,
  confirmado disponible con la clave del usuario. `.env` local conserva Groq
  principal y Gemini 3.6 respaldo; ninguna clave se imprimió ni se copió a docs.
- `eval/buscar_gemini_operativo.py`, `eval/gemini_modelos_probados_20261030.json`:
  autorización adicional de hasta tres solicitudes Gemini (techo 64); se usó
  **una**, con fallo simulado de Groq y respuesta real Gemini válida en 2,162 s.
  Se detuvo en el primer éxito; no se probaron 3.5 ni 2.5 Flash Lite.
- `tests/test_agente_correcciones.py`: fuentes pertinentes, comparación de jornada
  y separación entre resultado interno y cita real. Suite local completa:
  **235 pruebas aprobadas en 5,11 s**; incluye simulador HTTP local, sin API real.
- `eval/cerrar_evaluacion.py`, `eval/cierre_real_20261030.json`: nueva autorización
  de 13 solicitudes Groq, techo global 75 desde 62 consumidas/conservadoras.
  Ejecuta las veinte preguntas, reutiliza solo decisiones de herramienta de la
  corrida real anterior (mismo prompt, mensaje y contrato) y genera **de nuevo**
  las trece respuestas normativas. No usa respuestas grabadas como generaciones
  nuevas. Los siete casos resueltos por guardas no llaman al modelo.
- `docs/03-arquitectura.md`, `docs/05-prompts.md`, `docs/06-rag.md`, README y
  `docs/cierre-semana-3.md`: actualizar implementación actual, prompts, fuentes,
  lista de entregables y demostración, separando historia y estado vigente.
- `docs/09-decisiones.md`: usuario confirmó que Dorian usó ChatGPT; no se
  inventaron tareas específicas ni validaciones personales no confirmadas.

La corrida anterior `resultados_agente_final_20261030.json` se conserva con sus
fallos. La palabra «final» de ese nombre no acredita aprobación: corresponde a
una versión anterior al foco de fuentes y a `normativa_v3`. El archivo de cierre
es `cierre_real_20261030.json`; se califica después de revisar su contenido.

Contabilidad conservadora: 26 iniciales + 6 Groq de corrida parcial (incluye una
interrumpida) + 26 Groq de corrida anterior + 3 pruebas Gemini fallidas + 1 prueba
Gemini 3.6 exitosa = **62** antes del cierre. El cierre puede consumir hasta 13,
sin superar **75**. La lista de modelos es metadatos, no inferencia. Los reintentos
HTTP siguen identificándose aparte y respetan su configuración.

## Grupo K: cerrar fuentes e interfaz de la copia

El usuario excluyó la incorporación al repositorio y pidió terminar la app y
las fuentes de semana 3. No se realizaron operaciones en original o remoto.

| Archivo o recurso | Cambio |
| --- | --- |
| `config/corpus.json` | Nuevo manifiesto del Código de Defensoría Pública: URL, fecha publicación, corte 18/05/2026, consulta 30/10/2026, SHA-256 y alcance documental. |
| `data/raw/CODIGO_DEL_TRABAJO_defensoria_2026.pdf` | Descarga oficial, 216 páginas. PDF excluido de Git por aviso de redistribución. Se conserva el anterior. |
| `eval/contraste_fuentes_20261030.json` | Comparación de Arts. 47, 55, 69, 71, 75, 111, 113, 184, 185 y 188: diez textos idénticos. No se cambian fórmulas. |
| `scripts/ingest.py` | Cargar manifiesto, validar SHA-256 y añadir metadatos temporales/estado antes de indexar. |
| `.env` solo local, `.env.example`, `.gitignore` | Índice activo `data/chroma-2026/`, anterior conservado; nuevos PDF e índice excluidos de Git. Claves sin cambios ni exposición. |
| `data/chroma-2026/` | Ingesta real: 699 artículos, 618 vigentes y 81 derogados según edición. Embeddings locales, sin API de IA. |
| `config/parametros.yaml` | Sustituir la referencia secundaria INEC del divisor horario por MDT-2023-140, Disposición General Quinta, que declara jornada mensual 240 h. El valor no cambia. |
| `app/tools/resumen.py`, `frontend/app.js`, `frontend/index.html` | Avisos referidos al corte de la fuente, eliminando el aviso obsoleto de corpus 2023 sin contraste; URL JavaScript versionada para evitar caché anterior. |
| `docs/04-fuentes.md`, `docs/06-rag.md`, `docs/07-evaluacion.md`, `docs/cierre-semana-3.md`, README, `data/raw/README.md` | Estado actual del contraste y recorrido de interfaz, preservando historia de evaluación. |
| `docs/evidencias/semana-3/cierre-fuentes.md`, capturas `interfaz-*.png` | Evidencia de fuente 2026 visible, cálculo USD 600, cancelación y confirmación/descarga PDF, abstención e inyección. |
| `eval/resumir_cierre.py`, `eval/metricas_cierre_20261030.json` | Reflejar fuente activa y alcance; conservar mediciones generativas originales, sin atribuirlas a otra corrida nueva. |

Se comprobó SBU USD 482 desde 01/01/2026 en MDT-2025-195 y períodos/base
360/30/240 en MDT-2023-140, artículos 9/10 y Disposición General Quinta. El
contraste es documental, no certificación de hechos de usuarios ni de reformas
posteriores al 18/05/2026. Las mediciones IA previas conservan su corpus original;
la identidad textual de los diez artículos está guardada. No se consumió más IA.

Recorrido real en navegador de la app local: cálculo 600, fuente Art. 111 con
URL Defensoría y versión 2026, cancelación sin archivo, abstención por reglamento
privado ausente, rechazo de inyección, nueva vista previa y descarga confirmada
de PDF de una página. Se renderizó y revisó el PDF obtenido. Copia de demostración
en `output/pdf/resumen-decimo-tercero-2026.pdf` (no para Git). No se repitió la
batería de pruebas. La suite de 235 corresponde a la versión anterior a estos
ajustes documentales/ingesta/presentación; la operación real de ingesta y el
recorrido de interfaz verifican lo descrito aquí.

La app queda ejecutándose en `http://127.0.0.1:8011/`, Groq principal y Gemini
3.6 Flash de respaldo. Los once requisitos de implementación/evidencia de
semana 3 tienen su referencia en `docs/cierre-semana-3.md`; los mínimos medidos
se cumplen con el método declarado y P06/P07 siguen como abstenciones seguras.

## Grupo L: limpieza de temporales autorizada

Por petición del usuario se eliminaron únicamente dentro de la copia:

- `.tmp-aislamiento-20261030-01/`, `.tmp-cierre-20261030-01/` y
  `.tmp-rag-20261030-04/`: directorios de ejecución de pruebas.
- `.pytest_cache/` y seis directorios `__pycache__` de app/routers/services/tools,
  scripts y tests: cachés regenerables.
- `output/pdf/resumen-decimo-tercero-2026.png`: imagen intermedia usada para
  revisar visualmente el PDF; el PDF y las capturas del entregable se conservan.

Once objetivos eliminados, 257234 bytes liberados. Antes de borrar se validaron
las rutas absolutas dentro de la copia y la ausencia de enlaces/reparse points;
después se comprobó que los objetivos ya no existían. No se ejecutaron pruebas
ni llamadas a IA y no se reinició la app.

Se conservaron código, `.env`, dependencias, modelo de embeddings, índices,
fuentes, pruebas, scripts de evaluación y evidencias referidas por los informes.
`.cache/` contiene modelos necesarios y `.deps-rag/` contiene dependencias:
no son temporales prescindibles en el entorno actual. Original y remoto intactos.

## Grupo M: material PDF para exposición

Petición del usuario: guion separado de la guía de uso y preguntas del profesor,
todo en PDF. Se crearon:

- `output/pdf/guion_exposicion_semana_3.pdf`: dos páginas; exposición de cinco
  minutos con texto para decir, acciones en pantalla, métricas y plan B.
- `output/pdf/guia_pruebas_y_preguntas_profesor.pdf`: siete páginas; arranque en
  VS Code, recorrido de aplicación, diez casos, solución de problemas y 21
  preguntas con respuestas. Incluye el propósito de C09/C10 y la casilla de
  confirmación de motivo/saldos, según las preguntas posteriores del usuario.

Las cifras y límites proceden de los documentos y evidencias del cierre. Se
distinguen planificación grabada, generación real y publicación determinista;
no se afirma que todas las consultas respondan bien ni certificación jurídica.
Se revisó el texto extraído y se renderizaron/inspeccionaron las nueve páginas.
Se corrigió el contraste de los encabezados de tablas. Se eliminaron el script
y las imágenes temporales de `tmp/pdfs/` al entregar los dos PDF finales.
No se modificó el código de la app ni se consumió API de Groq/Gemini.

## Grupo N: cerrar la vista del PDF y distinguir las acciones de IA

El usuario señaló que, después de generar el PDF, quedaba la vista de revisión
con botones deshabilitados y parecía seguir procesando. También observó
solapamiento entre el atajo de explicación y el asistente general.

- `frontend/app.js`: al generar o cancelar, cerrar y vaciar la vista previa,
  liberar su referencia y presentar un aviso compacto fuera del panel. Conservar
  el cálculo y habilitar preparar otro resumen. Ocultar el aviso al iniciar
  otra preparación o cálculo. No limpiar una vista distinta si cambió el token.
- `frontend/index.html`: añadir aviso accesible `role=status`; renombrar el
  atajo a «Explicar este resultado con IA» y orientar el texto/ejemplo del
  asistente a derechos, requisitos y plazos. Se conserva el adjunto opcional.
  Actualizar versión de URL de JavaScript para evitar caché anterior.
- Se mantienen `/explicar` como atajo del resultado y `/agente` para consultas
  abiertas y herramientas; no se modifican cálculos, permisos ni backend.

Verificación: sintaxis JavaScript con Node; recorrido real en localhost:8011
con dato ficticio 600: calcular, preparar, generar/descargar, comprobar cierre
del panel y aviso de éxito, preparar otra vez, cancelar y comprobar aviso de
cancelación. Se observaron los textos nuevos después de recargar. Sin llamadas
a Groq/Gemini ni batería de pruebas adicional. Evidencia de los controles en
`docs/evidencias/semana-3/interfaz-acciones-claras.png`.

## Grupo O: interfaz final para usuarios, con un solo asistente

Instrucción explícita del usuario: presentar un producto para usuarios finales,
sin controles de laboratorio y con la IA únicamente en el asistente inferior.

- `frontend/index.html`: retirar «Qué hizo el asistente», botones C09/C10,
  nota de ejemplo, referencias académicas del pie y menciones al ejercicio.
  Mantener los avisos pertinentes sobre el alcance del cálculo en lenguaje de
  usuario; simplificar la confirmación de motivo y saldos.
- Quitar el botón independiente de explicación y el panel «En palabras
  sencillas». Las explicaciones y sus fuentes quedan en el asistente, que puede
  recibir el último cálculo con la casilla existente. Resultado y PDF permanecen.
- `frontend/app.js`: eliminar carga de ejemplos, eventos del botón retirado y
  render de trazas. Corregir referencias a elementos eliminados y mostrar
  solicitudes de datos/límites con mensajes comprensibles, sin nombres de
  herramientas ni argumentos internos. Fuentes legales y desglose permanecen.
- `app/tools/liquidacion.py`: cambiar únicamente la advertencia visible que
  mencionaba el Excel del grupo por su alcance real (años completos y revisión
  de fracciones/condiciones). No cambia fórmulas ni valores.
- README: aclarar que C09/C10 son referencias de validación fuera de la app.
- Guía PDF: reemplazar instrucciones de botones retirados por ingreso manual;
  anexo con datos C09/C10. Ahora tiene ocho páginas. Guion: retirar la indicación
  del botón de explicación eliminado; conserva dos páginas.

Verificación acotada: sintaxis JS; carga real de interfaz, cálculo de USD 600,
adjunto habilitado y respuesta de abstención sin trazas; formulario de
liquidación sin ejemplos. Se revisaron visualmente las páginas PDF modificadas.
Sin nuevas llamadas a IA ni ejecución de la batería completa de pruebas. Se
mantienen los endpoints del backend para compatibilidad; no se exponen como
acciones duplicadas en el frontend. El servidor sin recarga automática debe
reiniciarse para tomar el cambio de texto de liquidación; HTML/JS se actualizan
al recargar con Ctrl+F5.

## Grupo P: respuesta compartida y pausa de cambios al botón

Tras la primera simplificación, el usuario precisó que deseaba conservar
«Explicar mi cálculo» y mostrar su respuesta en el mismo espacio del asistente.

- `frontend/index.html`: restaurar solo ese atajo, conservar un único panel de
  respuestas, añadir estado de consulta y actualizar la versión del JavaScript.
- `frontend/app.js`: el atajo adjunta el último resultado, marca la casilla de
  uso de datos, completa la consulta y llama al mismo flujo `/agente`. Las
  respuestas se renderizan únicamente en `respuestaAgente`. Se deshabilitan
  los controles de consulta durante la solicitud y se limpia el estado al acabar.
  No se confirma automáticamente el uso de saldos de liquidación.
- Se verificó sintaxis y el flujo del evento con DOM y respuesta HTTP simulados
  localmente: una solicitud `/agente`, cálculo adjunto, confirmación falsa y
  respuesta en el panel compartido. No se hizo una llamada nueva a IA ni se
  afirma comprobación generativa de esta modificación.

Finalmente el usuario pidió dejar los cambios del botón por ahora. Se detuvo
esa modificación adicional, conservando el estado anterior descrito. No se
revirtió ni se añadió otro panel. Se mantienen retirados los ejemplos C09/C10,
la traza de herramientas y las referencias académicas de la interfaz.

## Grupo Q: tarjeta con solo el resultado

Por instrucción del usuario se retiraron de la tarjeta de resultado el botón
«Explicar mi cálculo», el detalle, los días y el fundamento. Se muestra el monto
y se conserva la acción de PDF. El asistente inferior conserva su formulario y
la opción de usar el último cálculo. El desglose se conserva en los datos del
backend y en el PDF. Se eliminaron las referencias JavaScript a los elementos
retirados y se actualizó la versión del script para evitar caché anterior.
Comprobación: sintaxis JavaScript y búsqueda de referencias retiradas; sin API.

## Grupo R: ubicación de la acción PDF

Se movió «Preparar resumen PDF» debajo de «Consultar al asistente», fuera del
formulario para que no envíe la consulta. Se muestra después de obtener un
cálculo válido. Conserva el mismo evento de preparación y descarga del PDF.
Verificación de ubicación HTML y sintaxis JavaScript, sin llamadas a IA.

## Grupo S: confirmación PDF visible junto a su botón

Al mover el botón, su vista previa había quedado arriba del asistente. El botón
se desactivaba esperando confirmación fuera de la pantalla. Se movieron la vista
previa y su estado justo debajo de «Preparar resumen PDF» y se añadió desplazamiento
hacia la confirmación o el error al preparar. La descarga conserva su confirmación
manual. Verificación de sintaxis y orden de elementos, sin llamadas a IA.

## Grupo T: orientación para consultar al asistente

Se aclaró que el usuario puede pedir una explicación de su cálculo o hacer otra
consulta laboral. Se indica cuándo marcar la casilla para adjuntar los datos y
se añadieron ejemplos de ambas opciones en el campo de consulta, junto con ayuda
persistente asociada mediante aria-describedby. Cambio de texto, sin API.

## Grupo U: descarga directa solicitada por el usuario

El botón principal ahora dice «Descargar PDF» y prepara el token y descarga el
archivo en una sola acción del usuario, sin desplegar otra tarjeta de revisión.
Se conserva el token de sesión de un uso del backend. Los errores aparecen junto
al botón y permiten reintentar. El flujo de vista previa solicitado por el agente
conserva su confirmación. Se comprobó sintaxis y flujo con HTTP/DOM simulados,
sin consumir API de IA.

## Grupo V: limpiar información anterior

Se limpia la consulta, su respuesta, fuentes y confirmación pendiente después de
descargar el PDF y al cambiar de tipo o iniciar un nuevo cálculo. Al cambiar de
cálculo se ocultan también la vista PDF, su estado y el botón de descarga hasta
obtener un nuevo resultado. El resultado numérico se conserva después de descargar.
Verificación de sintaxis JavaScript y limpieza de DOM simulada, sin API.

## Límites y siguiente alcance

### Registro final de cierre, sin más API

Se alcanzó el techo autorizado de 75 solicitudes conservadoras. El cierre
generó trece respuestas normativas nuevas reutilizando solo las elecciones de
herramienta reales. `eval/cierre_real_20261030.json` conserva la generación;
`eval/cierre_publicado_20261030.json` aplica publicación determinista posterior:
`completar_condiciones_publicadas` presenta párrafos literales de los artículos
111/113 ya citados cuando faltan modalidades esenciales y pide los datos del
formulario para importes, evitando incluir saldos ya pagados. No se inventan
reglas ni se atribuye esa presentación al modelo. Ese ajuste es posterior a la
suite de 235 pruebas; se ejecutó al producir el informe, sin repetir la suite.

`eval/revision_cierre_20261030.json` documenta revisión asistida y motivos;
`eval/resumir_cierre.py` produce `eval/metricas_cierre_20261030.json` sin API.
Resultados: recuperación 13/13; respuestas correctas con cita 11/13 (84,62 %);
abstención 4/4; dominio 2/2; defensa de inyección según referencia 2/2; cálculos
10/10. P06/P07 permanecen como fallos seguros, no se borran ni se corrigen las
mediciones históricas. El reporte detalla planificación grabada, generaciones
nuevas y publicación posterior; no afirma otra corrida completa nueva.

No se da por cerrada la entrega integral: vigencia jurídica 2026/metadatos
temporales sin contrastar, demostración final de interfaz sin ensayar y cambios
sin incorporar al repositorio original/remoto. Se conservan esos pendientes en
`docs/cierre-semana-3.md`. No se realizaron más pruebas ni llamadas al proveedor
después del cierre autorizado.

- El corpus consultado registra reforma de 2023; vigencia a 2026 pendiente de
  contraste. No se afirma validación jurídica actualizada.
- La corrida completa del grupo H no cumple las metas de respuesta con cita y
  abstención de la guía; las pruebas puntuales históricas no sustituyen esa evaluación.
- Horas adicionales y estimación de liquidación se implementaron en el grupo E;
  el agente, en F; el PDF con confirmación humana, en G. Sigue pendiente la
  corrección de los fallos de la evaluación generativa y la validación final del producto.
- Las próximas modificaciones se registrarán aquí con motivo, archivos,
  comprobación realizada y limitaciones, sin incluir claves.
