# Calculadora Inteligente de Beneficios y Liquidaciones Laborales

Proyecto de titulación de la carrera de Software de UNIANDES. Caso del Grupo 7: calculadora laboral para Ecuador.

## Integrantes

Alexander Guerrero, Bladimir y Dorian Zambrano.

## Problema y alcance

El proyecto busca facilitar la comprensión de beneficios y liquidaciones laborales mediante cálculos reproducibles y explicaciones sustentadas en normativa del Ministerio del Trabajo. Está dirigido a trabajadores y empleadores.

El alcance contempla décimo tercero, décimo cuarto, horas suplementarias y extraordinarias, vacaciones y liquidaciones. Los cálculos se implementarán en código determinista; la IA se utilizará para explicar los resultados y recuperar fundamentos normativos.

## Estado de la semana 1

Se dispone de propuesta, requisitos, arquitectura, inventario de fuentes, levantamiento de información, parámetros laborales configurables y diez casos de referencia con desarrollo. El backend implementa un endpoint de salud. La calculadora, la interfaz de usuario y la recuperación de documentos con IA permanecen pendientes de implementación e integración.

Los casos de referencia fueron construidos por el equipo a partir de las situaciones más consultadas en el levantamiento (décimos, vacaciones, horas y liquidación); no corresponden a personas reales. Según lo informado por Alexander, un contador revisó individualmente los cálculos y confirmó verbalmente sus resultados. Esta revisión no constituye una certificación firmada. El uso de asistencia de IA se registra en [decisiones y metodología](docs/09-decisiones.md).

## Documentación

- [Propuesta](docs/01-propuesta.md)
- [Requisitos](docs/02-requisitos.md)
- [Arquitectura](docs/03-arquitectura.md)
- [Fuentes normativas](docs/04-fuentes.md)
- [Parámetros laborales](config/parametros.yaml)
- [Levantamiento de información](docs/evidencias/semana-1/levantamiento.md)
- [Diez casos de referencia](docs/evidencias/semana-1/B4_Resoluci%C3%B3n%20de%20casos.xlsx)
- [Índice de evidencias](docs/evidencias/semana-1/README.md)
- [Decisiones y uso de IA](docs/09-decisiones.md)

## Ejecución local del backend

Se requiere Git y Python. En Windows se utilizó Python 3.14 durante la preparación del servicio.

Desde PowerShell:

```powershell
git clone https://github.com/AlexGuerreroR/calculadora-laboral-ec.git
cd calculadora-laboral-ec
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abrir <http://127.0.0.1:8000/health>. La respuesta esperada es:

```json
{"status":"ok"}
```

La documentación automática de FastAPI se encuentra en <http://127.0.0.1:8000/docs>. Para detener el servicio se utiliza Ctrl+C. Esta comprobación verifica la disponibilidad del backend, no la implementación de los cálculos laborales.

## Variables de entorno

La plantilla [.env.example](.env.example) contempla las siguientes variables para la integración posterior:

| Variable | Propósito |
|---|---|
| LLM_PROVIDER | Proveedor del modelo de lenguaje. |
| LLM_API_KEY | Credencial privada del proveedor. |
| LLM_MODEL | Modelo de lenguaje seleccionado. |
| EMBEDDING_MODEL | Modelo para generar representaciones de documentos. |
| CHROMA_PATH | Directorio de almacenamiento vectorial. |
| ALLOWED_ORIGINS | Orígenes previstos para solicitudes del cliente. |

El endpoint actual `/health` no consume estas variables ni requiere una clave de IA. Para futuras integraciones se podrá copiar la plantilla como `.env` y completar los valores localmente. El archivo `.env` y las credenciales no deben publicarse.

## Organización

`app/` contiene el backend; `config/`, los parámetros; `data/`, las fuentes y datos de trabajo; `docs/`, la documentación y evidencias. Los directorios `frontend/`, `tests/`, `eval/` y `scripts/` están reservados para las siguientes etapas.

## Trabajo del equipo

Los aportes y enlaces a pull requests se encuentran en el [índice de evidencias de semana 1](docs/evidencias/semana-1/README.md). Los cambios se presentan mediante ramas y pull requests para su revisión antes de integrarlos a `main`.
