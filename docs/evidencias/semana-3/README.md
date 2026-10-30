# Evidencias de la semana 3

## Talleres (archivos tal como se descargaron al terminar cada taller)

La clase 4 indicó que los archivos de los talleres son evidencia y deben estar en el repositorio.
Son **plantillas generadas por el taller**: su código tiene partes por completar (`TODO`, `...`) e
importa módulos que no existen en nuestro proyecto (`app.config.PARAMETROS`, `app.rag`). No se
ejecutan: `pytest.ini` limita las pruebas a `tests/`.

| Taller | Quién lo hizo | Archivos | Dónde quedó implementado |
| --- | --- | --- | --- |
| Clase 3 · Agentes de alcance controlado (28/10) | Alexander Guerrero | [taller-clase3-agentes/](taller-clase3-agentes/) | ADR-004 en [docs/09-decisiones.md](../../09-decisiones.md); agente en `app/services/agent.py`; décimos en `app/tools/decimos.py` (el caso de 6 meses en la Costa = 241 es C05 en `tests/test_calculos.py`) |
| Clase 4 · Automatización inteligente y calidad (29/10) | Bladimir Velasco | [taller-clase4-automatizacion/](taller-clase4-automatizacion/) | CI en `.github/workflows/ci.yml` (cobertura medida: 92 %, mínimo 80 %); evaluación en `eval/evaluar_agente.py` y [docs/07-evaluacion.md](../../07-evaluacion.md). El flujo automatizado (`flujo.py`, `casos_flujo.jsonl` con los 20 casos) queda para la Entrega 3 |

## Pendiente de completar

- Capturas de la aplicación: entrada sin fuente, fragmento citado, confirmación humana, resumen PDF,
  cambio del salario básico en `config/` e inyección de prompt.
