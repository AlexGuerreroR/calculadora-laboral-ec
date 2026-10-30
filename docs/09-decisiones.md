# Decisiones y registro de asistencia de IA

Proyecto: Calculadora Inteligente de Beneficios y Liquidaciones Laborales. Grupo 7, UNIANDES.

Fecha de preparación de este registro: 19 de octubre de 2026.

## Decisiones técnicas

1. Los cálculos laborales se implementarán mediante funciones deterministas, con parámetros separados del código y del prompt.
2. El modelo de lenguaje se utilizará para explicaciones y recuperación de fundamentos normativos. No será el motor aritmético de la aplicación.
3. Las fuentes y su vigencia se documentan en [04-fuentes.md](04-fuentes.md). Los parámetros se centralizan en [config/parametros.yaml](../config/parametros.yaml).
4. Los diez casos de referencia se conservan con sus datos, fórmulas, desarrollo y resultados en [el archivo Excel](evidencias/semana-1/B4_Resoluci%C3%B3n%20de%20casos.xlsx).
5. Los cambios se presentan mediante pull requests. Las funciones futuras se distinguen del código ya implementado.
6. No se publicarán claves de acceso ni datos personales que permitan identificar a las personas de los casos reales.

## Asistencia de IA durante la preparación

Este registro distingue la asistencia al desarrollo del comportamiento previsto de la aplicación. La utilización de un asistente no convierte una respuesta generada en una fuente normativa ni acredita por sí misma el cumplimiento de la resolución manual requerida.

### Alexander Guerrero

- Asistente utilizado: ChatGPT/Codex de OpenAI, según la conversación de trabajo disponible.
- Usos: orientación sobre Git y GitHub, apoyo en configuración y documentación, preparación de cálculos y fórmulas de los casos de referencia, y elaboración de los documentos de cierre D4.
- Revisión humana informada: Alexander indicó que un contador revisó individualmente los diez casos y confirmó verbalmente los resultados. No se dispone de acta ni de certificación firmada.
- Ajustes documentados: aclaración de periodos de décimos, modalidad acumulada, sueldo del mes de salida ya pagado, vacaciones previamente gozadas y redondeo de cada rubro final a dos decimales. Se incorporaron fuentes y observaciones de aplicación a los parámetros.
- Límite de la evidencia: la revisión verbal de resultados no acredita por sí misma que cada operación haya sido realizada manualmente. El equipo debe poder explicar el desarrollo de cada caso.

### Bladimir Velasco

- **Aportes:** levantamiento de información, propuesta, arquitectura C4, resolución independiente de los diez casos de referencia (A), endpoint `/explicar`, prompts y comparación, evidencias de la semana 2 y revisión de PR.
- **Asistente utilizado:** Claude (Anthropic).
- **Usos:** análisis de la guía, la plantilla y el material de clase; borradores de documentación (propuesta, arquitectura C4, requisitos no funcionales, ADR, evidencias); borradores de los system prompts v1–v3 y de las 10 entradas de comparación; borradores de código del endpoint `/explicar` y de sus pruebas; adaptación del kit de integración al caso 07; revisión de los pull requests del equipo.
- **Verificación y correcciones:** todo el código se ejecutó en mi computadora (`pytest -q`, `uvicorn` y pruebas en `/docs` con el proveedor real). Se corrigieron, entre otros: la cita de la norma pedida al modelo (se quitó tras el aviso del docente del 22/10), los requisitos no funcionales (temperatura reemplazada por razonamiento y tokens ajustados con mediciones reales) y, a partir de la revisión de Alexander en el PR #55, el recálculo del resultado en el servidor y el manejo de la configuración ausente.
- **Límite:** las respuestas del asistente no se usaron como fuente normativa; los valores legales provienen de las fuentes oficiales registradas en `docs/04-fuentes.md` y `config/parametros.yaml`.


### Dorian Zambrano

Se registra su aporte a requisitos, fuentes y revisiones mediante PR. La herramienta de IA utilizada, sus usos específicos y las correcciones efectuadas no han sido confirmados para este registro. Dorian debe aportar su declaración antes de marcar como completo el criterio de declaración individual de D4.

## Estado de implementación y revisión

El backend actual contiene el endpoint `/health`. La integración del motor de cálculo, la interfaz, el modelo de lenguaje y la recuperación documental permanecen pendientes.

Los presentes documentos fueron preparados con asistencia de IA a partir de los archivos del repositorio y de la información aportada por Alexander. Corresponde al responsable Dorian revisar su contenido y a Alexander verificar las instrucciones y enlaces antes de aprobar el PR de D4. Esta verificación final no se registra como realizada anticipadamente.

## ADR-001: Proveedor y modelo generativo

- **Estado:** Aceptado
- **Fecha:** 2026-10-19
- **Responsables:** Propuso: Bladimir Velasco · Revisaron: Alexander Guerrero y Dorian Zambrano

### Contexto

El caso pide un endpoint que explique en lenguaje sencillo un resultado ya calculado. El modelo no conversa ni calcula: recibe un resultado y devuelve una explicación en JSON con esquema. Ningún integrante debe pagar ni registrar tarjeta, y en niveles gratuitos el proveedor puede usar los datos enviados. Límites gratuitos consultados el 19/10/2026: Google AI Studio, Gemini 3.8 Flash: 5 solicitudes por minuto, unos 250 000 tokens de entrada por minuto y 20 solicitudes por día. Groq Console, openai/gpt-oss-120b: 30 solicitudes por minuto, 1 000 por día y 8 000 tokens por minuto. El modelo llama-3.1-8b-instant, previsto al inicio, ya no aparece disponible en Groq.

### Opciones consideradas

1. Gemini 3.8 Flash (Google AI Studio): ventaja: gratuito sin tarjeta, buen español, salida JSON con esquema y embeddings para la semana 3 / desventaja: solo 20 solicitudes por día y 5 por minuto.
2. Groq con openai/gpt-oss-120b: ventaja: gratuito, rápido y con 1 000 solicitudes por día / desventaja: no ofrece los embeddings que usaremos en la semana 3; su calidad en español se comprobará al comparar prompts (miércoles 21).
3. OpenAI: ventaja: alta calidad / desventaja: requiere pago, descartado por la guía.

### Decisión

Usaremos Gemini 3.8 Flash como proveedor principal y Groq (openai/gpt-oss-120b) como respaldo, porque ambos son gratuitos sin tarjeta y el modelo solo redacta una explicación corta, tarea que no exige un modelo grande. El proveedor se cambia con LLM_PROVIDER en el .env, sin tocar el código; durante el desarrollo usaremos Groq para reservar la cuota de Gemini.

### Consecuencias

**Positivas:** Costo cero; si Gemini devuelve 429 o se agota su cuota diaria, Groq responde; el mismo proveedor principal servirá para los embeddings de la semana 3.

**Negativas y riesgos:** Con 20 solicitudes diarias, las pruebas reales y la demo deben planificarse, y cada integrante usa su propia clave; las cuotas y los modelos gratuitos cambian sin aviso (como ocurrió con llama-3.1-8b-instant); los datos viajan a un tercero, por eso solo enviamos montos ya calculados, sin datos personales (ver ADR-003).

### Actualización 2026-10-26: Groq pasa a principal y Gemini 3.6 Flash a respaldo

En la revisión 2 (23/10) el docente observó que Gemini no funcionaba en el proyecto y señaló la versión del modelo. El 26/10 probamos los modelos Flash con la misma clave, primero con una llamada simple y luego con `/explicar` (razonamiento `low` y salida JSON con esquema):

| Modelo | Estado según Google | Resultado medido |
| --- | --- | --- |
| `gemini-3.8-flash` | Estable | 503 en la llamada simple (igual que el 22/10) |
| `gemini-3.6-flash` | Estable | Funciona; buena redacción, pero `/explicar` tardó 14,2 · 2,3 · 15,0 s (dos llamadas a menos de 1 s del límite de 15 s) |
| `gemini-3.5-flash` | Obsoleto (Google lo redirige a 3.6) | Funciona; descartado por obsoleto |
| `gemini-3.5-flash-lite` | Estable | Rápido (1,2 a 2,0 s), pero rompe las tildes («d3cimo», «orientacicn»); descartado |
| Groq `openai/gpt-oss-120b` | — | 0,6 a 1,5 s, buena redacción; ganó la comparación de prompts (`docs/05-prompts.md`) |

**Decisión:** Groq `openai/gpt-oss-120b` pasa a ser el proveedor principal y `gemini-3.6-flash` el respaldo (`LLM_PRINCIPAL=groq`, `LLM_RESPALDO=gemini`, `GEMINI_MODEL=gemini-3.6-flash`). Es la única combinación medida que cumple a la vez la meta de ≤ 8 s y la calidad del texto. El cambio se hizo solo en la configuración, sin tocar el código, como prevé la decisión original.

**Consecuencias:** Gemini sigue funcionando y se puede demostrar con `LLM_PRINCIPAL=gemini`; si Groq falla, la respuesta puede tardar hasta unos 15 s. Groq ofrece 1 000 solicitudes diarias frente a 20 de Gemini, lo que facilita la demo y la evaluación. La clave de Gemini se sigue usando en la semana 3 para los embeddings del RAG, que son otro modelo. Fuente: [modelos de Gemini API](https://ai.google.dev/gemini-api/docs/models), consultada el 26/10/2026.

---

## ADR-002: Workflow o agente

- **Estado:** Aceptado
- **Fecha:** 2026-10-19
- **Responsables:** Propuso: Alexander Guerrero · Revisó: Bladimir Velasco

### Contexto

Los montos de décimos, vacaciones, horas y liquidación tienen efectos legales y económicos para el trabajador. El caso exige que el 100 % de los 10 cálculos de referencia coincida con el cálculo manual (tolerancia ±0,01 USD) y que el 100 % de las entradas inválidas se rechace antes de llegar al modelo. La guía indica que en la semana 2 todavía no hay agente ni base de conocimiento. Además, la cuota gratuita de Gemini es de solo 20 solicitudes por día, por lo que cada llamada al modelo debe justificarse.

### Opciones consideradas

1. Workflow "cálculo en código + IA que explica": ventaja: montos exactos y probados con pytest; el código decide el orden de los pasos (validar, calcular, explicar); los cálculos no gastan cuota y, si la IA falla, igual se muestra el resultado / desventaja: no responde preguntas en lenguaje libre y cada cálculo nuevo exige programar su función.
2. Agente con herramientas desde la semana 2: ventaja: conversación flexible, el modelo elige qué herramienta usar / desventaja: no determinista, consume más tokens y solicitudes por las iteraciones, es más difícil de probar y la guía lo deja para la semana 3.
3. Llamada única donde el modelo calcula y explica: ventaja: implementación simple / desventaja: el modelo puede equivocarse en los montos y no se puede garantizar el ±0,01 USD; inaceptable para un resultado con efectos legales.

### Decisión

Usaremos un workflow determinista con el patrón "cálculo en código + IA que explica" porque los montos tienen efectos legales y deben coincidir al 100 % con el cálculo manual. Pydantic valida la entrada, las funciones de cálculo leen los parámetros de config/parametros.yaml y el modelo solo recibe el resultado ya calculado para explicarlo en lenguaje sencillo. En la semana 3 evaluaremos el agente, que usará estas mismas funciones como herramientas.

### Consecuencias

**Positivas:** Cálculos reproducibles y verificables con pruebas unitarias; el modelo no puede alterar montos; solo el endpoint /explicar consume cuota, los de cálculo no; la demo resiste fallas del proveedor porque el resultado se muestra aunque la explicación no esté disponible.

**Negativas y riesgos:** No hay consulta en lenguaje libre hasta la semana 3; hay más código que mantener y probar; si una situación no está prevista en los formularios (por ejemplo, jornada nocturna o trabajo en feriados, preguntas P12 y P13 del levantamiento), el sistema no la calcula y debe indicarlo.

---
## ADR-003: Manejo de claves y datos personales
 
- **Estado:** Aceptado
- **Fecha:** 2026-10-22
- **Responsables:** Propuso: Bladimir Velasco · Revisó: Dorian Zambrano
 
### Contexto
 
El backend necesita las claves de Gemini y Groq para llamar al modelo, y el repositorio es público. La guía indica que una clave en el repositorio deja en 0 el criterio de integración y obliga a revocarla, porque borrarla en un commit posterior no la saca del historial. Una clave escrita en el system prompt puede filtrarse en una respuesta (OWASP LLM07:2025, System Prompt Leakage). Además, el usuario ingresa datos de su relación laboral (remuneraciones, fechas, región), la LOPDP (2021) exige un inventario de los datos personales que el sistema recibe, almacena o envía al modelo, y en los niveles gratuitos el proveedor puede usar los datos enviados.
 
### Opciones consideradas
 
1. Claves en variables de entorno (`.env` local incluido en `.gitignore`; panel de variables de Render en producción) y minimización de datos: ventaja: la clave nunca entra al repositorio, al prompt ni al navegador, y al proveedor solo sale lo necesario / desventaja: cada integrante debe configurar su propio `.env` y, si alguien sube el `.env` por error, hay que revocar la clave.
2. Clave escrita en el código o en el system prompt: ventaja: configuración inmediata / desventaja: queda en el historial público de Git y puede filtrarse en una respuesta del modelo; criterio de integración en 0.
3. Llamar al modelo desde el frontend (JavaScript) con la clave en el navegador: ventaja: no requiere backend para la IA / desventaja: cualquier usuario puede ver la clave en las herramientas del navegador y gastar la cuota.
 
### Decisión
 
Usaremos variables de entorno porque es la única opción en la que la clave no queda en el repositorio, en el prompt ni en el navegador. Cada integrante guarda sus claves en un `.env` local, ignorado por `.gitignore`; el repositorio solo contiene `.env.example` sin valores, y en Render las claves irán en el panel de variables. Las claves no se comparten por chat ni por WhatsApp. Aplicaremos minimización de datos según este inventario:
 
| Dato | Se recibe | Se almacena | Se envía al modelo | Finalidad |
| --- | --- | --- | --- | --- |
| Remuneraciones mensuales | Sí | No (solo en memoria durante la solicitud) | Sí, como parte del resultado ya calculado, sin datos que identifiquen a la persona | Calcular y explicar el beneficio |
| Fechas de ingreso y de corte | Sí | No | Sí, dentro del resultado | Calcular días, meses y años de servicio |
| Región (Costa/Galápagos o Sierra/Amazonía) | Sí | No | Sí, dentro del resultado | Determinar el período del décimo cuarto |
| Nombre, cédula, empresa, teléfono o correo | **No se piden** | No | No | — |
| Registro técnico (`logs/llm.jsonl`) | — | Sí, local y fuera del repositorio | No | Medir proveedor, modelo, intento, tokens y tiempo; nunca guarda el texto del usuario ni los montos |
 
El frontend mostrará un aviso visible: que la explicación la genera una IA, que es una orientación, que no se guardan sus datos y que ante un conflicto debe acudir al Ministerio del Trabajo.
 
### Consecuencias
 
**Positivas:** La clave nunca aparece en el repositorio ni en el historial; si un prompt se filtra, no expone credenciales; se cumple el inventario y el aviso que exige la guía (LOPDP); si el proveedor usa los datos del nivel gratuito, solo recibe montos sin identificar a nadie.
 
**Negativas y riesgos:** Cada integrante debe configurar su `.env` y la aplicación no funciona sin él; al no guardar nada, no hay historial de consultas para auditar errores; si una clave llega a un commit hay que revocarla de inmediato y avisar al docente; el formulario solo tiene campos con formato validado para que el usuario no escriba datos personales en texto libre.
 
---

## ADR-004: Agente de alcance controlado

- **Estado:** Propuesto (se revisa con el docente en la revisión 3)
- **Fecha:** 2026-10-29
- **Responsables:** Diseño: Alexander Guerrero (taller de la clase 3, 28/10) · Implementación: Bladimir Velasco · Revisa: pendiente

### Contexto

En la revisión 2 el docente pidió que el usuario pueda escribir su caso con sus palabras (por ejemplo, «si me despidieron sin visto bueno y trabajé 3 años, ¿cuánto recibo?»). Un formulario por cálculo no resuelve esa pregunta: el sistema tiene que entender el caso, elegir el cálculo, pedir los datos que faltan y citar la norma. La guía de la semana 3 pide un agente con las herramientas del caso, cada una con esquema Pydantic, implementación determinista y pruebas; límite de iteraciones; rechazo fuera de dominio; parámetros en `config/` y confirmación humana antes de cualquier acción con efectos («registrar, enviar, derivar»). El caso 07 exige que los montos coincidan al 100 % con el cálculo manual (±0,01 USD), que los casos litigiosos se deriven al Ministerio del Trabajo y que se pueda generar un resumen PDF.

Un agente da vueltas pidiendo funciones: cada vuelta es una llamada que se paga, el modelo puede inventar nombres de funciones o argumentos, y todo lo que lee (el texto del usuario, los documentos del RAG y los resultados de las herramientas) es entrada no confiable (OWASP Top 10 for Agentic Applications 2026: ASI01 secuestro del objetivo, ASI02 mal uso de herramientas).

### Opciones consideradas

1. Agente con lista cerrada, tope de vueltas y confirmación humana, que reutiliza las funciones de `app/tools/`: ventaja: el alcance lo fija el código y no el prompt; los montos salen de las mismas funciones probadas del formulario / desventaja: más llamadas al modelo que el flujo fijo (de 2 a 6 por consulta) y más pruebas que mantener.
2. Agente sin límites (cualquier función, sin tope): ventaja: más flexible / desventaja: costo impredecible, puede repetir efectos y un texto malicioso podría pedir acciones prohibidas.
3. Solo el formulario guiado (workflow del ADR-002): ventaja: cero cuota adicional / desventaja: no atiende la observación de la revisión 2 ni responde preguntas combinadas (P07).

### Decisión

Usaremos la opción 1, sin quitar el formulario guiado: los dos conviven y usan las mismas funciones.

- **Meta:** explicar los beneficios y la liquidación con su fundamento en el Código del Trabajo. Los montos los calcula el código; el modelo pide las herramientas y explica. No emite dictámenes jurídicos.
- **Termina cuando:** el usuario recibe la explicación con su artículo, se le pide un dato que falta, se le informa que no hay respaldo suficiente o su caso queda derivado.
- **Usuario:** trabajadores y empleadores en Ecuador que desean comprender sus cálculos laborales.

| Herramienta | Qué hace | Nivel | Por qué |
| --- | --- | --- | --- |
| `consultar_articulo` | Busca en el Código del Trabajo (RAG, ChromaDB) y devuelve los artículos vigentes más cercanos | Libre | Solo lee. Es el «respaldo normativo» que el taller llamó `explicar_resultado`: la explicación la redacta el agente en su respuesta final, sin una herramienta que vuelva a llamar al modelo |
| `calcular_decimo_tercero` | Art. 111 | Libre | Solo calcula; misma función que `/calculos`. El taller la nombró `calcular_decimos`; se separó en dos porque cada décimo pide datos distintos |
| `calcular_decimo_cuarto` | Art. 113 | Libre | Solo calcula |
| `calcular_vacaciones` | Arts. 69 y 71 | Libre | Solo calcula |
| `calcular_horas_extra` | Art. 55 (caso de referencia C08) | Libre | Solo calcula |
| `estimar_liquidacion` | Arts. 71, 111, 113, 185 y 188 (casos C09 y C10) | Libre | Solo genera una estimación |
| `generar_resumen` | Arma el PDF del cálculo con su fundamento y aviso | Con confirmación | Lo pide el caso; se genera solo si el usuario lo aprueba (decisión del taller) |
| `derivar_al_ministerio` | Orienta el caso al Ministerio del Trabajo | Con confirmación | La guía pide confirmación para «derivar»; no envía datos a terceros (ADR-003) |
| `realizar_pago`, `modificar_sueldo`, contactar al empleador, dictaminar si un despido fue legal | — | Fuera de la lista | Mueven dinero, cambian datos o son asesoría legal: los hace una persona |

- **`PERMITIDAS`, `REQUIEREN_OK` y el tope viven en el código** (`app/services/agent.py`) y en `config/parametros.yaml` (`agente.max_iteraciones: 6`), nunca en el prompt.
- **Al llegar al tope (6 vueltas)** el agente responde: «No pude completar la consulta. Presento lo obtenido e indico qué falta para continuar…», y muestra los cálculos ya hechos.
- **Argumentos del modelo:** se validan con el esquema Pydantic de cada herramienta antes de ejecutar; si faltan datos, el error vuelve al modelo y éste los pide al usuario («FALTA:»).
- **Confirmación:** muestra los argumentos reales (qué se hará, con qué datos y a quién). La conversación pausada queda en memoria del servidor; el navegador solo recibe un identificador de un solo uso (15 minutos), nunca el historial.
- **Verificación final en código:** toda respuesta debe citar al menos un artículo; cada artículo citado debe estar entre los recuperados o en el fundamento de un cálculo, y cada monto debe salir de una herramienta. Si no, el sistema se abstiene. La interfaz muestra solo los fragmentos citados.
- **Buscar primero (código, no modelo):** antes de la primera llamada, el servidor recupera los 5 artículos más cercanos a la pregunta y se los entrega al modelo como datos. Lo decidió la evaluación del 29/10: en la línea base el modelo respondía «FALTA:» sin buscar en 9 de sus 10 fallos (ver `docs/07-evaluacion.md`).
- **Fuera de dominio e inyección:** el prompt (`app/prompts/agente_v3.md`) responde «FUERA_DE_DOMINIO» y el sistema muestra un rechazo cortés. La pregunta va en `<pregunta>` y cada fragmento en `<fragmento>`: son datos, nunca instrucciones.
- **Parámetros en `config/parametros.yaml`:** salario básico unificado, divisores, recargos, porcentajes de la liquidación, tope de vueltas, fragmentos por consulta y texto de la derivación.

### Pruebas (simulador del taller y `pytest`)

| Escenario del taller | Resultado en el simulador (28/10) | Prueba automática |
| --- | --- | --- |
| A · Camino feliz | ✔ 3 vueltas | `test_calcula_con_la_herramienta_y_cita_lo_recuperado` |
| B · Fuera de alcance | ✔ 2 vueltas | `test_fuera_de_dominio_tiene_su_propio_mensaje`, `test_herramienta_fuera_de_la_lista_no_se_ejecuta` |
| C · El tope | ✔ 6 vueltas | `test_tope_de_iteraciones` |
| D · Inyección en un documento | ✔ 3 vueltas: la confirmación permitió rechazar | `test_inyeccion_en_un_fragmento_no_da_permisos` |

Las pruebas usan un doble del modelo (`tests/test_agente.py`, `tests/test_consultar.py`): no gastan cuota. La evidencia con el modelo real va en `docs/evidencias/semana-3/`.

### Consecuencias

**Positivas:** atiende la observación de la revisión 2; un texto malicioso no puede crear funciones ni cambiar el tope; el agente y el formulario dan el mismo monto (C08, C09 y C10 coinciden con ±0,01 USD); una cita inventada o un monto calculado por el modelo se detectan y producen abstención; nada con efecto ocurre sin el usuario; el costo por consulta tiene techo (6 llamadas).

**Negativas y riesgos:** cada consulta usa de 2 a 6 llamadas, por lo que la cuota gratuita se agota antes; la verificación es estricta y puede abstenerse ante una respuesta correcta mal escrita (preferimos callar a inventar); el texto libre puede traer datos personales que se envían al proveedor, lo que cambia lo dicho en el ADR-003 sobre «solo campos con formato»: la caja pide no escribirlos y el registro técnico no guarda el texto; las sesiones viven en memoria y se pierden si el servidor se reinicia; la liquidación es una estimación del MVP (sueldo fijo, sin días adicionales de vacaciones ni otros rubros).

---
