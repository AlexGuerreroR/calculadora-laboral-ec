# Observaciones de la sustentación y lo que se hizo

Sustentación ante el docente tutor: sábado 7 de noviembre de 2026. La demo se hizo
sobre la URL pública con la versión de `main` de ese día; el modo básico de
liquidación se mostró en local, como versión en revisión.

| # | Observación | Estado | Qué se hizo | Evidencia |
|---|---|---|---|---|
| 1 | Valoró la base del proyecto y destacó la seguridad (claves como secretos, gitleaks, inyección, abstención) | Se mantiene | Sin cambios en esos controles | `docs/10-riesgos.md`, T15–T18 de `docs/08-pruebas.md` |
| 2 | Integrar los cambios de interfaz presentados al final (modo básico de liquidación) | Corregida | Modo básico y avanzado, interfaz rediseñada, explicación y PDF con total referencial | PR #74 (`893b69a`), desplegada con la imagen `a96c0ce` el 10/11 |
| 3 | Ajustar las respuestas a las preguntas más frecuentes de los trabajadores (décimos, vacaciones, liquidación) | Atendida en parte | Orientación igual para frases coloquiales («me botaron», «me sacaron del trabajo»); «¿cuánto me toca?» lleva al formulario sin inventar montos; plazo y registro del finiquito con su fuente; «demandar», «reclamar» o «no me han pagado… ¿qué hago?» derivan al Ministerio del Trabajo | PR #74 y sus pruebas (`tests/`); T12 y T14 contra la URL |
| 4 | (Revisión del PR #73) T12 debía comprobar la fecha, y los casos dependientes no debían desaparecer del total | Corregida | T12 exige «15 de marzo» con el Art. 113; T10, T11 y T19 se marcan BLOQUEADO si falla el caso previo | PR #76 (`98e77d2`), corrida 21/21 del 10/11 |

## Pendiente de la observación 3

Falta medir con el modelo real un conjunto de preguntas frecuentes redactadas como
las haría un trabajador y repetir la evaluación de 20 preguntas con la versión
`a96c0ce`. La comparación vigente de la evaluación (semana 3 frente a semana 4) está
en `docs/07-evaluacion.md` y corresponde a la versión anterior al PR #74.
