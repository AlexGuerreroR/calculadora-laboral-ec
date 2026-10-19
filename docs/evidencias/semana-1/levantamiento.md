# Levantamiento de información real · Semana 1

**Método:** encuesta abierta por WhatsApp a personas conocidas del grupo que trabajan o han trabajado.
**Fecha:** 18 y 19 de octubre de 2026 · **Responsable:** Bladimir Velasco
**Mensaje enviado:**

> Hola, estamos haciendo un proyecto universitario sobre beneficios laborales. ¿Qué duda tienes o has tenido sobre tu décimo tercero, décimo cuarto, vacaciones, horas extra o liquidación? Escríbeme tu pregunta tal como te la harías. (No necesito tu nombre ni datos personales.)

**Privacidad:** no se registran nombres, teléfonos ni datos que identifiquen a las personas (LOPDP). Las preguntas se copian textualmente, con su ortografía original.
**Respaldo:** las capturas originales las conserva el grupo fuera del repositorio, disponibles para el docente si las solicita. Las versiones anonimizadas (sin nombres, teléfonos ni fotos) se agregarán en `docs/evidencias/semana-1/encuesta/` en un PR posterior.

## Preguntas recibidas (15 preguntas reales)

| ID | Pregunta (textual) | Perfil | Tema | Historia relacionada |
|---|---|---|---|---|
| P01 | Si trabajé 8 meses siendo afiliada cuánto sería mi liquidación? | Trabajadora | Liquidación | HU-01 |
| P02 | Que tal, actualmente llevo 9 meses laborando afiliado, como se que estoy recibiendo mi remuneración económica correctamente? | Trabajador | Verificación de pagos | HU-02 |
| P03 | ¿En qué momento del año puedo pedir mis vacaciones? | Trabajador | Vacaciones (normativa) | HU-06 |
| P05 | Buenas noches, como se cuanto deben pagarme por mis vacaciones? | Trabajador | Vacaciones | HU-06 |
| P06 | trabajé 6 meses en un trabajo, me aseguraron por 3 meses y me despidieron cuanto debo recibir de liquidacion ? | Trabajador | Liquidación + afiliación irregular | HU-01, HU-09 |
| P07 | cuantas vacaciones me toca recibir, llevo 3 años de trabajo ? | Trabajador | Vacaciones | HU-06 |
| P08 | trabaje 3 meses en una empresa, cuanto recibio de liquidacion, yo renuncie. | Trabajador | Liquidación | HU-01 |
| P10 | si renuncio al año , recibo decimos? | Trabajador | Décimos | HU-04, HU-05 |
| P11 | cuanto recibo de decimo. | Trabajador | Décimos | HU-04, HU-05 |
| P12 | trabajo los feriados, como me pagan las horas extra. | Trabajador | Horas extra | HU-07 |
| P13 | hago 3 horas extras en la noche, cuanto me deben pagar? | Trabajador | Horas extra | HU-07 |
| P14 | trabaje 1 año, recibo decimos? | Trabajador | Décimos | HU-04, HU-05 |
| P15 | cuanto recibo de decimos ? | Trabajador | Décimos | HU-04, HU-05 |
| P16 | FALTA: pregunta real adicional | | | |
| P17 | FALTA: pregunta real adicional | | | |

## Comentarios adicionales (no cuentan como preguntas)

Respuestas recibidas que son afirmaciones, no preguntas. Se conservan porque aportan información sobre el alcance.

| ID | Comentario (textual) | Perfil | Aporte |
|---|---|---|---|
| K01 | En mi caso estos parámetros no aplican ya que yo trabajo de forma independiente | Trabajador independiente | Confirma el alcance negativo y el perfil de trabajador informal |
| K02 | yo no estoy asegurado en mi trabajo. | Trabajador | Caso de posible incumplimiento: derivación al Ministerio del Trabajo (HU-09) |

## Resumen por tema

| Tema | Preguntas | N.º |
|---|---|---|
| Décimo tercero y décimo cuarto | P10, P11, P14, P15 | 4 |
| Liquidación | P01, P06, P08 | 3 |
| Vacaciones | P03, P05, P07 | 3 |
| Horas suplementarias y extraordinarias | P12, P13 | 2 |
| Verificación de pagos | P02 | 1 |
| FALTA: clasificar P16 y P17 | P16, P17 | 2 |
| **Total de preguntas** | | **15** |
| Comentarios adicionales | K01, K02 | 2 |

## Hallazgos

1. **Los cinco cálculos se confirman.** 12 de las 13 preguntas clasificadas hasta ahora tratan sobre décimos, liquidación, vacaciones u horas extra.
2. **Casi nadie da todos los datos.** Preguntas como P11 y P15 ("cuanto recibo de decimo") no indican sueldo ni fechas, y P01 no indica el motivo de salida. Esto justifica los **formularios guiados** y que el sistema **pida los datos que faltan** en lugar de suponerlos.
3. **Aparecen casos que no se deben calcular sino derivar.** P06 (afiliado solo una parte del tiempo y despedido) y el comentario K02 (sin afiliación) implican posibles incumplimientos del empleador: el sistema debe orientar y **derivar al Ministerio del Trabajo**, no dictaminar.
4. **Hay usuarios fuera del alcance.** El comentario K01 (trabajador independiente) confirma el alcance negativo y el perfil de trabajador informal como beneficiario indirecto.
5. **Surgen detalles a decidir en el diseño.** P12 (horas en feriados) y P13 (horas en la noche) plantean recargos especiales: jornada nocturna y trabajo en días de descanso. Se debe verificar en el Código del Trabajo si entran al alcance del cálculo de horas.
6. **Hay preguntas normativas, no solo de cálculo.** P03 ("¿en qué momento puedo pedir mis vacaciones?") se responde con el texto del Código mediante RAG; servirá para las 20 preguntas normativas de la Semana 3.
7. **Limitación del levantamiento:** todas las respuestas provienen de trabajadores; ninguna de empleadores. Las historias del perfil empleador se basan en el caso oficial y se recomienda consultar al menos a un pequeño empleador.

## Conclusión

Los temas más consultados fueron los décimos (4), seguidos de liquidación y vacaciones (3 cada uno), lo que confirma los cinco cálculos elegidos. Las preguntas reales llegan con datos incompletos y, en algunos casos, esconden conflictos laborales; por eso el sistema necesita formularios guiados, validación y derivación al Ministerio del Trabajo.
