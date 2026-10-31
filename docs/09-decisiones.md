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

Se registra su aporte a requisitos, fuentes y revisiones mediante PR. El usuario
confirmó el 30/10/2026 que Dorian utilizó **ChatGPT**. No detalló qué tareas se
apoyaron en ese asistente ni qué correcciones o validaciones realizó Dorian;
esos puntos quedan por precisar por el integrante, sin atribuir automáticamente
a la IA todos sus aportes ni registrar una revisión humana no confirmada.

## Estado de implementación y revisión

Estado histórico al preparar el documento (19/10): el backend contenía `/health`.
Actualización de la copia al 30/10: están implementados motor de cinco cálculos,
interfaz, RAG, agente acotado y PDF con confirmación humana. La validación real
de calidad y la disponibilidad del respaldo se registran en `07-evaluacion.md`;
la existencia de código no se equipara al cumplimiento de las métricas.

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

Decisión histórica del 19/10: Gemini principal y Groq de respaldo. En la copia
del 30/10 se invirtió el orden: **Groq principal y Gemini de respaldo**, mediante
`.env`, por los errores de disponibilidad observados. No se afirma que los
límites históricos de cuota sigan vigentes: dependen de la cuenta y el modelo.
La prueba real de failover distingue fallo simulado del principal y respuesta
real de Gemini; sus resultados y tiempos están en `eval/respaldo_real*.json`.

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
| Remuneraciones y saldos | Sí | Durante el cálculo y, si se pide PDF, en la instantánea pendiente en memoria | Sí, al pedir explicación o adjuntar el cálculo al agente | Calcular, explicar y resumir el beneficio |
| Fechas de ingreso, corte y salida | Sí | En memoria; también en la instantánea pendiente de PDF | Sí, si forman parte del cálculo adjunto | Calcular tiempos y mostrar datos utilizados |
| Región (Costa/Galápagos o Sierra/Amazonía) | Sí | En memoria; también en la instantánea pendiente de PDF | Sí, dentro del cálculo adjunto | Determinar el período del décimo cuarto |
| Consulta de texto libre al agente | Sí | Solo durante la solicitud; no se registra su contenido en logs | Sí | Consultar normativa y coordinar herramientas |
| Nombre, cédula, empresa, teléfono o correo | **No se piden** | No hay campos para ellos; el texto libre no se filtra automáticamente | Podrían enviarse si el usuario los incluye en la consulta; la interfaz pide no hacerlo | Se solicita no introducirlos |
| Cookie aleatoria de sesión del resumen y token de aprobación | Sí | Cookie HttpOnly/SameSite en navegador; hash de sesión y token pendiente en memoria | No | Vincular vista previa y confirmación, impedir reutilización |
| PDF generado | Se produce tras confirmación | Bytes en memoria enviados al navegador; no se guarda en disco del servidor | No | Descarga autorizada por el usuario |
| Registro técnico (`logs/llm.jsonl`) | — | Sí, local y fuera del repositorio | No | Medir proveedor, modelo, intento, tokens y tiempo; nunca guarda el texto del usuario ni los montos |
 
Actualización de la copia, 30/10/2026: el frontend informa del envío al proveedor
al usar IA y de la memoria temporal para la vista previa del PDF. Los pendientes
caducan a los 300 segundos configurados y se eliminan al procesar otra operación;
también desaparecen al reiniciar el proceso. Confirmar o cancelar elimina la
entrada inmediatamente. La preparación está acotada por sesión y por proceso.
El PDF se genera sin API y solo tras la confirmación de un token de un solo uso.
Esto documenta el tratamiento implementado; no certifica cumplimiento jurídico
ni verifica secretos históricos de un repositorio que no se inspeccionó.
 
### Consecuencias
 
**Positivas:** Las claves se leen en el backend y no se incorporan al prompt ni al frontend. Se documentan los datos tratados y el aviso de privacidad de la aplicación. La ausencia de secretos en un historial remoto no se ha verificado en esta revisión de la copia.
 
**Negativas y riesgos:** Cada integrante debe configurar su `.env` para usar IA; los cálculos y el PDF son locales. No hay historial persistente de consultas para auditar su contenido. Los pendientes de PDF viven en un solo proceso y se pierden al reiniciarlo; un despliegue con varios workers requiere otro diseño de almacenamiento. La consulta del agente admite texto libre y podría contener información personal pese al aviso de no introducirla. Si una clave llega a un commit debe revocarse y notificarse; no se ha inspeccionado el historial remoto en esta tarea.
 
---
