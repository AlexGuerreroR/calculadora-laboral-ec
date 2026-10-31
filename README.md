# Calculadora Laboral EC

## Ejecutar el avance incorporado al repositorio local

Desde esta carpeta, en PowerShell de VS Code:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\iniciar-local.ps1
```

Abra http://127.0.0.1:8000 y actualice con Ctrl + F5. Detenga antes con Ctrl + C
el servidor anterior si ocupa ese puerto. El script usa Python 3.14 externo,
las dependencias locales y los modelos descargados, sin instalar ni consumir IA.
Para otro puerto agregue `-Port 8001` al comando.

El avance incluye cinco calculos, RAG con indice `data/chroma-2026`, asistente
con fuentes y PDF de descarga directa. Las respuestas anteriores se limpian
al descargar o cambiar de calculo. Las secciones historicas siguientes pueden
describir la antigua vista previa del PDF o modelos anteriores; la configuracion
de ejecucion actual usa Groq como principal y Gemini 3.6 Flash como respaldo.
El informe de traslado y el respaldo se indican en `docs/11-traslado-repositorio-local.md`.

**Caso 07 · Calculadora Inteligente de Beneficios y Liquidaciones Laborales** · Grupo 7 · Seminario de Ingeniería de Software con IA Generativa, UNIANDES.

**Integrantes:** Alexander Guerrero, Bladimir Velasco y Dorian Zambrano.

## Problema que resuelve

Los trabajadores consultados (12 de 15 en nuestro levantamiento) no saben cómo se calculan sus décimos, vacaciones, horas adicionales y liquidación. Hoy aceptan el monto que les indican sin poder verificarlo o usan calculadoras sin fuente. El sistema calcula cada valor con código verificado y explica el resultado en lenguaje sencillo, para trabajadores y pequeños empleadores.

## Estado: MVP con RAG conectado (semana 3 parcial)

- **Calcula** (código determinista, sin IA): décimo tercero, décimo cuarto, vacaciones y horas suplementarias/extraordinarias. Estima liquidaciones por renuncia con desahucio o despido intempestivo con saldos informados explícitamente.
- **Explica con RAG** el resultado ya calculado (`/explicar`): recupera los artículos necesarios, valida las citas del modelo y muestra los fragmentos y fuentes en la interfaz. Sin respaldo suficiente, se abstiene.
- **Agente:** consulta normativa y utiliza ocho herramientas cerradas, con argumentos validados y límites. `agente_v4` conserva la pregunta original y `normativa_v3` explica las fuentes pertinentes. Los importes requieren formulario; días anuales y exceso de jornada pueden calcularse en Python con datos explícitos declarados. Cada consulta es independiente.
- **Resumen PDF:** el botón «Descargar PDF» prepara y descarga el documento con un solo clic. Si se solicita al agente, se muestra una vista previa con confirmación o cancelación. Ambos caminos usan un token de sesión de un solo uso; el modelo no confirma la descarga.
- **Pendiente:** evaluación generativa completa del agente y validación final del producto.
- **Despliegue previsto:** Render (semana 4).

## Arquitectura

El frontend (HTML + JavaScript) habla solo con el backend FastAPI. El backend valida con Pydantic, calcula con `app/tools/` usando `config/parametros.yaml` y, para la explicación, llama al modelo mediante `app/services/llm.py` (Groq `openai/gpt-oss-120b`; respaldo Gemini 3.8 Flash), con reintentos, tiempo límite y registro de tokens. Diagramas C4 y flujo completo en [docs/03-arquitectura.md](docs/03-arquitectura.md); decisiones en [docs/09-decisiones.md](docs/09-decisiones.md) (ADR-001 a ADR-003).

| Endpoint | Qué hace | ¿Usa IA? |
| --- | --- | --- |
| `GET /` | Interfaz web del producto | No |
| `POST /calculos/decimos` | Décimo tercero o cuarto (campo `tipo`) | No |
| `POST /calculos/vacaciones` | Días y valor de vacaciones | No |
| `POST /calculos/horas` | Horas suplementarias y extraordinarias | No |
| `POST /calculos/liquidacion` | Rubros y total neto estimado de saldos confirmados | No |
| `POST /explicar` | Explica un resultado; el servidor lo recalcula antes | Sí |
| `POST /agente` | Consulta normativa y herramientas con datos confirmados | Sí |
| `POST /resumen/preparar` | Prepara datos y fuentes para revisión, sin crear PDF | No |
| `POST /resumen/confirmar` | Genera y descarga la instantánea aprobada una sola vez | No |
| `POST /resumen/cancelar` | Invalida la solicitud pendiente | No |
| `GET /health` | Estado del servicio | No |

## Instalación local (Windows, PowerShell)

Requisitos: Git y Python 3.11 o superior (probado con 3.14).

```powershell
git clone https://github.com/AlexGuerreroR/calculadora-laboral-ec.git
cd calculadora-laboral-ec
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
```

En `.env`, pegue **su** clave de Gemini (<https://aistudio.google.com/apikey>) y de Groq (<https://console.groq.com/keys>), sin comillas ni espacios. Compruebe que la clave no se subirá: `git status` no debe mostrar `.env`.

Si PowerShell bloquea `activate`, ejecute una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Ejecución

```powershell
uvicorn app.main:app --reload
```

- Aplicación: <http://127.0.0.1:8000/>
- Documentación de la API: <http://127.0.0.1:8000/docs>

## Variables de entorno

Plantilla: [.env.example](.env.example). Nunca se sube el `.env` con valores.

| Variable | Propósito |
| --- | --- |
| `LLM_PRINCIPAL` / `LLM_RESPALDO` | Proveedor principal y de respaldo (`gemini`, `groq` o `simulado`) |
| `GEMINI_API_KEY` / `GROQ_API_KEY` | Claves privadas de cada proveedor (solo en `.env`) |
| `GEMINI_MODEL` / `GROQ_MODEL` | Modelo de cada proveedor |
| `LLM_TIMEOUT_S` | Tiempo límite por intento del principal; respaldo con 45 s configurados en `Config.timeout_respaldo_s` |
| `LLM_REINTENTOS` | Intentos por proveedor |
| `LLM_MAX_TOKENS` | Tokens máximos de salida |
| `LLM_RAZONAMIENTO` | Nivel de razonamiento (`low`, `medium`, `high`); se usa en lugar de la temperatura |
| `MAX_INPUT_CHARS` | Tamaño máximo de la entrada de `/explicar` |
| `RATE_LIMIT_POR_MINUTO` | Solicitudes por minuto por usuario en `/explicar` |
| `ALLOWED_ORIGINS` | Orígenes permitidos (CORS) |
| `EMBEDDING_MODEL` / `CHROMA_PATH` | Modelo de embeddings e índice local usado por el RAG; el índice debe permanecer dentro de la aplicación |

## Pruebas y evaluación

### Entorno de esta copia (30/10/2026)

Se conservó el entorno `.venv` recibido. Las dependencias RAG nuevas están en
`.deps-rag/`; modelo e índice están dentro de la copia. Desde la raíz de esta
aplicación, usando Python 3.14 instalado en Windows:

```powershell
$env:PYTHONPATH = "$PWD\.deps-rag;$PWD\.venv\Lib\site-packages"
$env:PYTHONIOENCODING = "utf-8"
$env:HF_HOME = "$PWD\.cache\huggingface"
py -3.14 -B -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Para verificar sin gastar API, en vez del servidor:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
py -3.14 -B -m pytest -q -p no:cacheprovider tests/test_rag.py tests/test_explicar.py tests/test_normativa.py tests/test_rutas_copia.py
```

Comprobación realizada: 50 comprobaciones locales aprobadas y recuperación real
12/13 (92,3 %). Esa comprobación local no llamó al proveedor generativo.
Las pruebas reales posteriores y el ajuste a `rag_v2` están registrados en
[la bitácora de la copia](docs/10-bitacora-copia.md), grupo C. Se configuró Groq
como principal y Gemini como respaldo. Las claves permanecen únicamente en el
`.env` local y nunca deben publicarse.
La comprobación anterior utilizó un corpus con reformas hasta 2023. El corpus
activo se actualizó después a la edición con reforma del 18/05/2026, registrada
en `config/corpus.json`. Los diez artículos usados en la evaluación se
contrastaron y son idénticos entre ambas ediciones. No se repitió la evaluación
generativa completa con el nuevo índice.
Detalles, alcance de las métricas y limitaciones en `docs/06-rag.md`.

Comprobación local de cierre posterior: **235 pruebas aprobadas en 5,11 s**, con
`py -3.14 -B -m pytest -q -p no:cacheprovider tests`. No se suman a las selecciones
históricas. Recuperación actual del agente: 13/13 con todos los artículos esperados.
El respaldo `gemini-3.6-flash` respondió un JSON válido en 2,162 s después de un
fallo simulado de Groq; quedó configurado en la copia. Evidencia:
`eval/gemini_modelos_probados_20261030.json`. No se provocó una caída real de Groq.
Lista de requisitos y demostración: [cierre de semana 3](docs/cierre-semana-3.md).

```powershell
pytest -q                          # pruebas con un doble del modelo: no gastan cuota
python scripts/demo_429.py         # demostración del manejo del error 429 (proveedor simulado)
python scripts/comparar_prompts.py # compara system_v1, v2 y v3 → docs/05-prompts.md
```

- Comparación de prompts: [docs/05-prompts.md](docs/05-prompts.md).
- Evidencias de la semana: [docs/evidencias/semana-2/](docs/evidencias/semana-2/).

## Base de conocimiento

Fuentes oficiales, vigencia y estrategia de fragmentación en [docs/04-fuentes.md](docs/04-fuentes.md). Los parámetros variables (salario básico 2026, divisores, días) viven en [config/parametros.yaml](config/parametros.yaml) con su fuente.

## Limitaciones conocidas

- Liquidación: solo los dos motivos indicados. El usuario informa salario pendiente, base del décimo tercero, días pendientes de décimo cuarto y vacaciones, horas pendientes y descuentos. Los campos faltantes se rechazan; no se sustituyen por cero.
- Desahucio por años completos: criterio conservado del ejercicio, pendiente de contraste actualizado. El motivo de salida no es determinado por la IA ni por la calculadora.
- C10 conserva el saldo cero de vacaciones adicionales informado en el Excel; no se generaliza a otros trabajadores. La interfaz y el resultado muestran esta salvedad.
- Horas adicionales: sueldo mensual y jornada completa, con cantidades agregadas informadas; no clasifica horarios ni comprueba límites diarios/semanales.
- Vacaciones con remuneración fija por mes; sin fracciones de mes.
- La explicación depende de la disponibilidad del proveedor de IA; si no responde, el cálculo sigue disponible.

### Verificar la etapa de cálculos

Con el entorno de la copia configurado como se indicó arriba:

```powershell
py -3.14 -B -m pytest -q -p no:cacheprovider tests/test_horas.py tests/test_liquidacion.py tests/test_calculos.py tests/test_endpoints_calculo.py tests/test_explicar.py tests/test_rag.py tests/test_frontend.py
```

Resultado ejecutado: 115 pruebas aprobadas, sin API; incluye C01–C10 del Excel
con tolerancia ±0,01 USD. Nuevos resultados: C08 = 76,67; C09 = 1.130,33;
C10 = 9.331,84 USD, sujetos a los supuestos del ejercicio. El formulario de
liquidación exige revisar y confirmar los saldos propios. C09/C10 permanecen
solo en la documentación y los datos de validación; no son controles de la app.
El prompt activo es `rag_v3`; esta etapa comprobó su integración y las fuentes
locales, sin volver a consumir API. La bitácora detalla el alcance exacto.

### Consultar al agente

En la interfaz, escriba una consulta laboral. Para usar un cálculo, complete el
formulario y marque «Usar los datos de mi último cálculo». El agente no transforma
números del texto libre en sueldos, fechas ni saldos: si faltan datos confirmados,
pide usar el formulario. La liquidación permite revisar y confirmar sus saldos
antes de que la herramienta del agente los utilice. Esta revisión no registra un
finiquito ni realiza una acción externa.

Herramientas: `consultar_normativa`, `calcular_decimos`, `calcular_vacaciones`,
`calcular_horas`, `estimar_liquidacion`, `explicar_resultado`, `solicitar_datos` y
`generar_resumen`. Esta última solo solicita la vista previa; la generación ocurre
en un endpoint separado después del clic humano. No hay herramientas para
ejecutar comandos, enviar, registrar, pagar o borrar.

Los límites viven en `config/parametros.yaml`, sección `agente`: seis vueltas,
ocho solicitudes lógicas al modelo y cuatro herramientas por vuelta. Las
solicitudes lógicas conservan los reintentos/corrección JSON del cliente, por lo
que el número de peticiones HTTP al proveedor puede ser mayor. Se muestran solo
resultados de herramientas y respuestas verificadas, no el texto final libre del
modelo. La primera vuelta exige una herramienta; el contexto incluye explícitamente
el ID del cálculo. El prompt activo del agente es `agente_v3`. Las guardas no
sustituyen la evaluación de fidelidad y cobertura.

Verificación local del agente y componentes afectados:

```powershell
py -3.14 -B -m pytest -q -p no:cacheprovider tests/test_agente.py tests/test_llm.py tests/test_rag.py tests/test_explicar.py tests/test_liquidacion.py tests/test_frontend.py
```

Resultado de esta selección: 101 pruebas aprobadas sin API. No es la misma
selección de 115 pruebas de la etapa de cálculos, ni una evaluación real de las
20 preguntas. Detalles de versiones y resultados en la bitácora, grupo F.

Prueba real posterior con Groq: `agente_v2` eligió `explicar_resultado` para
`calculo-0`; `rag_v3` explicó el décimo tercero conservando 600,00 USD y citando
el Art. 111 recuperado. HTTP 200, estado completado, dos vueltas y tres
solicitudes lógicas. Es una comprobación puntual de ese flujo, no una evaluación
de todas las herramientas ni de las métricas de abstención/rechazo.

## Consideraciones éticas y de datos personales

La aplicación orienta, no asesora: no dictamina conflictos laborales y deriva al Ministerio del Trabajo. No pide nombre, cédula ni datos de contacto. Al usar IA, la consulta, el cálculo adjunto y los fragmentos necesarios se envían al proveedor; no incluya datos personales en el texto libre. Las vistas previas del PDF se conservan temporalmente en memoria con caducidad; el PDF se devuelve al navegador sin guardarse en disco del servidor. Inventario actualizado en [docs/09-decisiones.md](docs/09-decisiones.md).

### Generar un resumen PDF

Hay dos formas de obtener el documento:

- **Desde el cálculo:** revise el resultado y pulse «Descargar PDF». Ese clic
  solicita la preparación y confirma la descarga, sin abrir otra tarjeta de revisión.
- **Desde el agente:** solicite el resumen con el cálculo adjunto. Se muestra
  una vista previa con datos, total, desglose y fuentes. «Confirmar y descargar
  PDF» genera el documento; «Cancelar resumen» invalida la solicitud sin generarlo.

En ambos casos, el navegador llama primero a `/resumen/preparar` y después a
`/resumen/confirmar` con el token y la aprobación. El servidor genera el PDF
con los datos preparados, sin aceptar nuevos montos en la confirmación y sin
llamar a IA para crear el archivo.

Cada solicitud vence según `resumen.vigencia_segundos` (300 s actualmente),
pertenece a una sesión de navegador y solo puede usarse una vez. Los pendientes
caducados se eliminan al procesar otra operación; reiniciar el proceso elimina
todos. Para el MVP se requiere un proceso/worker: el almacén pendiente es local
a ese proceso y no está compartido entre servidores. No hay historial de PDFs.
Los límites de pendientes y solicitudes están en `config/parametros.yaml`.

ReportLab está declarado en `requirements.txt` e instalado en `.deps-rag/` de
esta copia (4.5.1). Comprobación de esta etapa:

```powershell
py -3.14 -B -m pytest -q -p no:cacheprovider tests/test_resumen.py tests/test_agente.py tests/test_rag.py tests/test_explicar.py tests/test_liquidacion.py tests/test_frontend.py
```

Resultado: 109 pruebas aprobadas sin API generativa. Incluye PDF reales C01,
C09 y C10, token de un solo uso, caducidad, otra sesión, cancelación, datos
manipulados y lote de herramientas con PDF pendiente. Se generó además
`output/pdf/resumen-c09-demo.pdf` con el índice real y se revisaron visualmente
sus dos páginas. Es un archivo de demostración local, no un archivo para Git.

## Evaluación real de la copia, 30/10/2026

**Cierre vigente:** 11/13 respuestas correctas con cita (84,62 %), abstención
4/4, recuperación completa 13/13 y cálculos 10/10. El método reutiliza decisiones
de herramienta, genera trece respuestas nuevas y aplica condiciones literales
de las fuentes al publicar; no se presenta como otra planificación nueva.
Consumo conservador total: 75 solicitudes. Gemini 3.6 Flash quedó comprobado de
respaldo. Se actualizó el corpus a la edición oficial con reforma 18/05/2026,
699 fragmentos y metadatos temporales; los diez artículos utilizados son idénticos
a los evaluados. Se observó la interfaz con cálculo, fuente 2026, PDF confirmado
y descargado, cancelación, abstención e inyección, sin más IA. El avance ya se
trasladó al repositorio local; todavía no está publicado en GitHub. El traslado
y sus comprobaciones constan en `docs/11-traslado-repositorio-local.md`. Véanse
[evaluación](docs/07-evaluacion.md) y [lista de cierre](docs/cierre-semana-3.md).

### Línea base histórica

Los diez cálculos de referencia coinciden dentro de USD 0,01. La corrida real
de veinte preguntas con Groq obtuvo 0/13 respuestas correctas con cita: el
agente requiere corrección. Recuperar los artículos con la pregunta original
(12/13) no acredita recuperarlos tras reformular dentro del agente. El
diagnóstico P04 confirma pérdida de evidencia al reformular. La evaluación y
ese diagnóstico consumieron 26/60 solicitudes autorizadas, sin Gemini; la
configuración habitual conserva Groq principal y Gemini de respaldo.

Resultados, criterios y orden de corrección en
[docs/07-evaluacion.md](docs/07-evaluacion.md). Cambios de esta etapa en
[docs/10-bitacora-copia.md](docs/10-bitacora-copia.md), grupo H. No se afirma
que el agente cumpla las metas ni que Gemini se haya probado en esta corrida.

## Uso de IA en el desarrollo y aporte de cada integrante

La declaración de uso de IA y los aportes de cada integrante se registran en [docs/09-decisiones.md](docs/09-decisiones.md) y en los pull requests del repositorio.
