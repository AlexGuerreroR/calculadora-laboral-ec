# Evidencias de la semana 2 · MVP e integración con IA generativa

Proyecto: Calculadora Laboral EC · Caso 07 · Grupo 7 · UNIANDES.
Integrantes: Alexander Guerrero, Bladimir Velasco y Dorian Zambrano.
Revisión 2: viernes 23 de octubre de 2026.

La guía pide en esta carpeta: *«capturas de la aplicación funcionando, comparación de prompts, decisiones tomadas y problemas encontrados»*.

## 1. Capturas de la aplicación funcionando

Las capturas están en `capturas/`. No muestran claves ni datos personales.

| # | Archivo | Qué demuestra | Punto de la guía |
| --- | --- | --- | --- |
| 1 | `01-git-status-sin-env.png` | Existe `.env` en la PC, pero `git status` dice «nothing to commit»: la clave no se sube | Clave desde variables de entorno; `.env` en `.gitignore` |
| 2 | `02-pytest.png` | `main` actualizado y suite completa en verde: 83 pruebas con un doble del modelo, sin gastar cuota | Pruebas automatizadas con un doble (mock) |
| 3 | `03-primera-llamada-groq.png` | Llamada real al respaldo: 95 tokens de entrada y 95 de salida (50 de razonamiento), 0,8 s | Servicio que encapsula al modelo; tokens y tiempo |
| 4 | `04-gemini-503.png` y `04b-gemini-sin-conexion.png` | Gemini respondió 503 y luego no conectó (22/10); el mensaje es claro, sin traza | Problema encontrado: por qué hace falta el respaldo |
| 5 | `05-demo-429.png` | Ronda 1 sin protección: 3 de 8 fallan con 429. Ronda 2 con `ClienteLLM`: 8 de 8; tres esperaron el `retry-after` (10 s) y pasaron en el intento 2, sin usar el respaldo | Manejo del 429 con reintentos y espera |
| 6 | `06-calculo-c03.png` | `POST /calculos/decimos`, caso C03 → 737,50, con desglose y fundamento | Endpoint con entrada validada (sin IA) |
| 7 | `07-explicar-422.png` | `/explicar` con datos incompletos → 422 `application/problem+json` con la lista de campos, sin llamar al modelo | Errores comprensibles; entradas inválidas rechazadas antes del modelo |
| 8 | `08-explicar-200.png` | `/explicar` con el resultado C03 → explicación en lenguaje sencillo; total, fundamento y aviso puestos por el servidor; proveedor `groq` | Endpoint principal con salida JSON con esquema |
| 9 | `09-frontend.png` | Interfaz propia: cálculo, desglose, fundamento y explicación con aviso de IA | Frontend funcional |
| 10 | `10-frontend-error.png` y `10b-frontend-sin-servidor.png` | Quinta explicación en un minuto → mensaje claro de límite (429); servidor apagado → «No se pudo conectar con el servidor» | Frontend: errores comprensibles; límite de solicitudes |
| 11 | `11-comparacion-429-real.png` | Durante la comparación de prompts, Groq devolvió 429 (límite de 8 000 tokens por minuto) en la mayoría de las llamadas; el cliente esperó lo indicado y reintentó: las 30 respondieron, ninguna falló | Manejo del 429 con el proveedor real |

## 2. Comparación de prompts

Tabla completa y conclusión del grupo en [docs/05-prompts.md](../../05-prompts.md), generada con `scripts/comparar_prompts.py` sobre las 10 entradas de `eval/entradas_prompts.csv` (7 normales, 2 no procesables y 1 fuera de dominio) y calificada por los tres integrantes.

- Proveedor usado en la corrida: Groq · `openai/gpt-oss-120b` (Gemini no respondía el 22 y 23/10).
- Versión elegida: system_v3 (0 de 10 respuestas inventan; ver conclusión en `docs/05-prompts.md`).

## 3. Decisiones tomadas en la semana

| Decisión | Dónde se registra |
| --- | --- |
| Gemini 3.8 Flash como principal y Groq `openai/gpt-oss-120b` como respaldo | ADR-001 |
| Workflow «cálculo en código + IA que explica», sin agente en la semana 2 | ADR-002 |
| Claves solo en `.env` o en el panel del proveedor de despliegue; inventario de datos personales | ADR-003 |
| El modelo no devuelve la norma: el fundamento lo agrega el código (aviso del docente del 22/10) | `docs/03-arquitectura.md`; prompts v2 y v3 |
| `/explicar` recalcula en el servidor el resultado recibido; si no coincide, 422 | PR #55 |
| Razonamiento `low` en lugar de temperatura; 2048 tokens; 15 s por intento y 2 intentos | `docs/03-arquitectura.md` (requisitos no funcionales) |
| Alcance del MVP: décimos y vacaciones; horas y liquidación en la semana 3 | `docs/03-arquitectura.md` (alcance del MVP) |
| Frontend HTML + JavaScript servido por FastAPI; despliegue previsto en Render | `docs/03-arquitectura.md` |

## 4. Problemas encontrados y cómo se resolvieron

| Problema | Causa | Solución |
| --- | --- | --- |
| El kit del martes no arrancaba con algunos `.env` | El kit y la plantilla usaban nombres de variables distintos; una línea vacía rompía el arranque | Se adoptó el kit corregido del 22/10 (acepta ambos nombres) |
| `llama-3.1-8b-instant` ya no estaba disponible en Groq | Cambio del catálogo del proveedor | Respaldo con `openai/gpt-oss-120b`, verificado en la consola de Groq (ADR-001) |
| Riesgo de fuentes inventadas | Pedirle la norma al modelo invita a que la invente (aviso del docente) | Se quitó `fundamento_citado` del esquema; la norma la pone el código |
| El esquema aceptaba `NaN` como sueldo | Validación incompleta de números | `allow_inf_nan=False` y prueba automatizada |
| Conflicto en `requirements.txt` | Un cambio se subió directo a `main` mientras otra rama editaba el mismo archivo | Se resolvió conservando la lista del kit; desde entonces todo va por PR |
| Gemini respondió 503 y luego no conectó (22/10) | Falla del proveedor, no del código | Las pruebas reales se hicieron con Groq; el respaldo cubre este caso |
| El cliente podía enviar a `/explicar` un total o una norma falsos | El backend confiaba en el resultado del navegador | `/explicar` recalcula en el servidor y usa solo sus propios datos |
| Una configuración ausente producía un error 500 | El cliente del modelo se creaba antes de validar | El cliente se crea al final; sin configuración responde 503 claro |
| Groq devolvió 429 durante la comparación de prompts | 30 llamadas seguidas superan su límite de 8 000 tokens por minuto | `llm.py` respetó el `retry-after` y reintentó; ninguna llamada falló (captura 11) |

## 5. Trabajo del equipo (pull requests de la semana)

| PR | Autor | Contenido |
| --- | --- | --- |
| #44 | Bladimir | Arquitectura C4 niveles 1 y 2 |
| #45 | Dorian | ADR-001 y ADR-002 |
| #46 | Alexander | `.env.example` y `.gitignore` de la semana 2 |
| #48 | Bladimir | System prompts v1–v3 y 10 entradas de comparación |
| #49 | Dorian | Esquemas, cálculos de décimos y vacaciones, pruebas |
| #50 | Alexander | Servicio de IA (`llm.py`) con respaldo, reintentos y pruebas |
| #51 | Bladimir | Requisitos no funcionales medidos y alcance del MVP |
| #52 | Bladimir | Entradas de comparación desde los cálculos reales |
| #53 | Dorian | ADR-003 de claves y datos personales |
| #54 | Dorian | Endpoints de cálculo |
| #55 | Bladimir | Endpoint `/explicar` |
| #56 | Alexander | Frontend y README |
