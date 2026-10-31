## Plan de calidad y evaluación

*Grupo 7 · Beneficios y liquidaciones laborales · taller de la Clase 4, 29 de octubre de 2026*

> **Ejercicio del taller.** Las metas son las planteadas en clase. Lo que se aplica hoy en el repositorio está en la sección «Estado en el repositorio» al final. Las mediciones reales de la aplicación están en `docs/07-evaluacion.md`.

### 1. Evaluación básica del RAG
| Métrica | Cómo se mide | Meta |
|---|---|---|
| Acierto de recuperación | La fuente correcta aparece en los primeros 5 resultados, sobre 20 preguntas del conjunto del lunes | 90 % |
| Respuestas con cita | Respuestas que citan su fuente | 80 % |
| Silencio correcto | 3 preguntas cuya respuesta no está en los documentos: el sistema debe decir que no sabe | 100 % |

### 2. Evaluación básica del agente
- Escenarios: A · Camino feliz; B · Fuera de alcance; C · El tope; D · Inyección en un documento.
- Meta de tareas cumplidas: 79 %. Rechazos correctos en fuera de alcance e inyección: 100 %.

### 3. Evaluación del flujo automatizado
- Conjunto dorado: 20 casos en `eval/casos_flujo.jsonl`, con el resultado esperado escrito antes de correr.
- Errores silenciosos: **0**. Máximo a revisión humana: 30 %. Umbral actual: 0.85.

### 4. Calidad del software
| Práctica | Se aplica |
|---|---|
| Pruebas unitarias con pytest (cada función de cálculo y cada herramienta) | Sí |
| Medición de cobertura (pytest-cov) | Sí |
| Linter y formato (ruff, eslint o similar) | No |
| Integración continua (GitHub Actions) que corre todo en cada push | Sí |
| La evaluación del RAG, el agente y el flujo también corre en CI | No |

- Meta de cobertura: 80 %.
- Quién y cuándo: GitHub Actions corre pytest y la cobertura en cada push y pull request; QA revisa los resultados antes de cada entrega. La evaluación no corre en CI (ver abajo).

### Evidencia para la Revisión 3 y la Entrega 3
- Salida de `python eval/evaluar.py` y de `pytest` en `docs/evidencias/semana-3/`.

### Estado en el repositorio (30 de octubre de 2026)

- **CI** (`.github/workflows/ci.yml`): ejecuta `pytest` con cobertura mínima de 80 % en cada push y pull request. Las pruebas usan dobles del modelo: no llaman a Groq ni a Gemini.
- **Sin evaluación generativa en CI:** las 20 preguntas del RAG y del agente requieren el proveedor y se ejecutan manualmente con los scripts de `eval/`. Sus resultados están en `docs/07-evaluacion.md`.
- **Flujo automatizado:** no implementado. `casos_flujo.jsonl` conserva plantillas con `TODO` y el «0 errores silenciosos» es del simulador del taller, no una medición.
- **Linter:** no se aplica.
