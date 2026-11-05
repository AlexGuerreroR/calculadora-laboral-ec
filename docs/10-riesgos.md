# Matriz de riesgos y protección de credenciales

Grupo 7 · Calculadora Inteligente de Beneficios y Liquidaciones Laborales.
Elaborada en el taller «Tablero, credenciales y riesgos» (semana 4, clase 1, 4/11/2026).

Referencias: OWASP Top 10 for LLM Applications y OWASP Top 10 for Agentic Applications,
con la numeración usada en el taller (edición 2026). En la edición 2025, «Excessive Agency»
es LLM06 y «Misinformation» es LLM09.

## Matriz

Cada mitigación se puede verificar en el archivo, la prueba o el documento indicado.

| Riesgo | OWASP | Probabilidad | Impacto | Mitigación | Dónde se ve | Responsable |
|---|---|---|---|---|---|---|
| Un texto copiado del empleador ordena ignorar las reglas o revelar las instrucciones | LLM01 · Prompt Injection | Media | Alto | Patrones de inyección, órdenes citadas apartadas y lista cerrada `PERMITIDAS`; el modelo no puede ejecutar acciones | `config/parametros.yaml`, `app/services/agente.py`, preguntas P19 y P20, pruebas T15 y T16 | Alexander Guerrero |
| Respuesta legal incompleta o con operaciones inventadas («4 × 15 = 60 días») | LLM07 · Misinformation | Media | Alto | Cita obligatoria, validación de cantidades y operaciones, condiciones literales del artículo y abstención | `app/services/agente.py` (`consultar_normativa`), `docs/07-evaluacion.md` | Bladimir Velasco |
| El usuario escribe nombre, cédula o sueldo en la consulta libre y se envía al proveedor | LLM02 · Sensitive Information Disclosure | Media | Medio | Aviso en la interfaz de no ingresar datos personales, registros sin el texto del usuario, sesiones solo en memoria | `frontend/index.html`, `app/services/llm.py`, ADR-003 en `docs/09-decisiones.md` | Dorian Zambrano |
| Muchas consultas agotan la cuota gratuita de Groq | LLM06 · Unbounded Consumption | Media | Medio | Límite de 4 consultas por minuto por IP (429), tope de 8 llamadas y 6 vueltas, máximo de tokens, tiempo límite y respaldo Gemini | `config/parametros.yaml`, `app/routers/agente.py`, prueba T21 | Bladimir Velasco |
| El agente estima la liquidación o genera el PDF sin que el usuario confirme | LLM03 · Excessive Agency | Baja | Alto | 8 herramientas que solo calculan o leen, confirmación humana en `estimar_liquidacion` y `generar_resumen`, tope de 6 vueltas | `app/services/agente.py`, ADR-004, prueba T19 | Alexander Guerrero |

Las pruebas T15–T21 están en [08-pruebas.md](08-pruebas.md); las preguntas P19 y P20, en
`eval/preguntas.csv`.

## Protección de credenciales

| Control | Resultado | Evidencia |
|---|---|---|
| Búsqueda de secretos en todo el historial | `gitleaks git -v --log-opts="--all"`: 105 commits de todas las ramas, **no leaks found** (4/11/2026) | Taller, misión 2 |
| Plantilla sin valores | `.env.example` con 15 variables y ninguna sensible con valor | `.env.example` |
| `.env` fuera del repositorio | `.gitignore` ignora `.env` y `.env.*`, y conserva `!.env.example` | `.gitignore` |
| Prevención automática | gitleaks en cada push y pull request | `.github/workflows/secretos.yml` |
| Claves en producción | Solo como variables o secretos de la plataforma; nunca en el código ni en el Dockerfile | ADR-005 en `docs/09-decisiones.md` |

Como no hubo claves expuestas, no fue necesario rotar ni reescribir el historial. Si alguna vez
se expone una clave, el orden es: **rotarla** en el panel del proveedor, **limpiar** el historial
(`git filter-repo`) y **prevenir** con gitleaks.
