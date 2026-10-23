# Calculadora Laboral EC

**Caso 07 · Calculadora Inteligente de Beneficios y Liquidaciones Laborales** · Grupo 7 · Seminario de Ingeniería de Software con IA Generativa, UNIANDES.

**Integrantes:** Alexander Guerrero, Bladimir Velasco y Dorian Zambrano.

## Problema que resuelve

Los trabajadores consultados (12 de 15 en nuestro levantamiento) no saben cómo se calculan sus décimos, vacaciones, horas adicionales y liquidación. Hoy aceptan el monto que les indican sin poder verificarlo o usan calculadoras sin fuente. El sistema calcula cada valor con código verificado y explica el resultado en lenguaje sencillo, para trabajadores y pequeños empleadores.

## Estado: semana 2 (MVP)

- **Calcula** (código determinista, sin IA): décimo tercero, décimo cuarto y vacaciones (anuales y proporcionales).
- **Explica** con IA el resultado ya calculado (`/explicar`); la norma la agrega el código, no el modelo.
- **Todavía no calcula** horas extra ni liquidación completa: llegan en la semana 3 como herramientas del agente. Ver «Alcance del MVP» en [docs/03-arquitectura.md](docs/03-arquitectura.md).
- **Despliegue previsto:** Render (semana 4).

## Arquitectura

El frontend (HTML + JavaScript) habla solo con el backend FastAPI. El backend valida con Pydantic, calcula con `app/tools/` usando `config/parametros.yaml` y, para la explicación, llama al modelo mediante `app/services/llm.py` (Gemini 3.8 Flash; respaldo Groq), con reintentos, tiempo límite y registro de tokens. Diagramas C4 y flujo completo en [docs/03-arquitectura.md](docs/03-arquitectura.md); decisiones en [docs/09-decisiones.md](docs/09-decisiones.md) (ADR-001 a ADR-003).

| Endpoint | Qué hace | ¿Usa IA? |
| --- | --- | --- |
| `GET /` | Interfaz web del producto | No |
| `POST /calculos/decimos` | Décimo tercero o cuarto (campo `tipo`) | No |
| `POST /calculos/vacaciones` | Días y valor de vacaciones | No |
| `POST /explicar` | Explica un resultado; el servidor lo recalcula antes | Sí |
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
| `LLM_TIMEOUT_S` | Tiempo límite por intento (s) |
| `LLM_REINTENTOS` | Intentos por proveedor |
| `LLM_MAX_TOKENS` | Tokens máximos de salida |
| `LLM_RAZONAMIENTO` | Nivel de razonamiento (`low`, `medium`, `high`); reemplaza a la temperatura en Gemini 3.8 Flash |
| `MAX_INPUT_CHARS` | Tamaño máximo de la entrada de `/explicar` |
| `RATE_LIMIT_POR_MINUTO` | Solicitudes por minuto por usuario en `/explicar` |
| `ALLOWED_ORIGINS` | Orígenes permitidos (CORS) |
| `EMBEDDING_MODEL` / `CHROMA_PATH` | Base vectorial de la semana 3 (todavía sin uso) |

## Pruebas y evaluación

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

- Sin horas extra ni liquidación completa (semana 3).
- Vacaciones con remuneración fija por mes; sin fracciones de mes.
- La explicación depende de la disponibilidad del proveedor de IA; si no responde, el cálculo sigue disponible.

## Consideraciones éticas y de datos personales

La aplicación orienta, no asesora: no dictamina conflictos laborales y deriva al Ministerio del Trabajo. No pide nombre, cédula ni datos de contacto, no guarda datos del usuario y solo envía al modelo el resultado ya calculado. Inventario de datos en el ADR-003 de [docs/09-decisiones.md](docs/09-decisiones.md).

## Uso de IA en el desarrollo y aporte de cada integrante

La declaración de uso de IA y los aportes de cada integrante se registran en [docs/09-decisiones.md](docs/09-decisiones.md) y en los pull requests del repositorio.
