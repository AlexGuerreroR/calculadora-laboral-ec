# Levantamiento de información real · Semana 1

**Método:** encuesta abierta por WhatsApp a personas conocidas del grupo que trabajan o han trabajado.
**Fecha:** 18 y 19 de octubre de 2026 · **Responsable:** Bladimir Velasco
**Ampliación:** 20 de octubre de 2026. Alexander Guerrero incorpora P16 y P17.
**Mensaje enviado:**

> Hola, estamos haciendo un proyecto universitario sobre beneficios laborales. ¿Qué duda tienes o has tenido sobre tu décimo tercero, décimo cuarto, vacaciones, horas extra o liquidación? Escríbeme tu pregunta tal como te la harías. (No necesito tu nombre ni datos personales.)

**Privacidad:** no se registran nombres, teléfonos ni datos que identifiquen a las personas (LOPDP). Las respuestas se copian textualmente, con su ortografía original.
**Respaldo:** ver la sección *Respaldo anonimizado* al final de este documento.

## Respuestas recibidas (17)

La columna *Historia relacionada* usa la numeración de `docs/02-requisitos.md`.

| ID | Pregunta (textual) | Perfil | Tema | Historia relacionada |
|---|---|---|---|---|
| P01 | Si trabajé 8 meses siendo afiliada cuánto sería mi liquidación? | Trabajadora | Liquidación | HU-06 |
| P02 | Que tal, actualmente llevo 9 meses laborando afiliado, como se que estoy recibiendo mi remuneración económica correctamente? | Trabajador | Verificación de pagos | HU-07 |
| P03 | ¿En qué momento del año puedo pedir mis vacaciones? | Trabajador | Vacaciones (normativa) | HU-03, HU-07 |
| P04 | En mi caso estos parámetros no aplican ya que yo trabajo de forma independiente | Trabajador independiente | Fuera de alcance | HU-10 |
| P05 | Buenas noches, como se cuanto deben pagarme por mis vacaciones? | Trabajador | Vacaciones | HU-03 |
| P06 | trabajé 6 meses en un trabajo, me aseguraron por 3 meses y me despidieron cuanto debo recibir de liquidacion ? | Trabajador | Liquidación + afiliación irregular | HU-06, HU-10 |
| P07 | cuantas vacaciones me toca recibir, llevo 3 años de trabajo ? | Trabajador | Vacaciones | HU-03 |
| P08 | trabaje 3 meses en una empresa, cuanto recibio de liquidacion, yo renuncie. | Trabajador | Liquidación | HU-06 |
| P09 | yo no estoy asegurado en mi trabajo. | Trabajador | Afiliación (derivación) | HU-10 |
| P10 | si renuncio al año , recibo decimos? | Trabajador | Décimos | HU-01, HU-02 |
| P11 | cuanto recibo de decimo. | Trabajador | Décimos | HU-01, HU-02 |
| P12 | trabajo los feriados, como me pagan las horas extra. | Trabajador | Horas extra | HU-04, HU-05 |
| P13 | hago 3 horas extras en la noche, cuanto me deben pagar? | Trabajador | Horas extra | HU-04, HU-05 |
| P14 | trabaje 1 año, recibo decimos? | Trabajador | Décimos | HU-01, HU-02 |
| P15 | cuanto recibo de decimos ? | Trabajador | Décimos | HU-01, HU-02 |
| P16 | Necesito saber cuanto es el monto a recibir por mi decimo.? | Persona consultada | Décimos | HU-01, HU-02 |
| P17 | Hala buenas tardes como puedo hacer para ha cumular mis fondos de reserva hal IES y cada tipo retirarlo | Persona consultada | Fondos de reserva / IESS, fuera de alcance | HU-10 |

### Nota metodológica sobre P04 y P09

- Muchas respuestas no usan signos de interrogación (P08, P11, P12), pero contienen una palabra interrogativa ("cuánto", "cómo") y se consideran preguntas.
- **P04 y P09 están redactadas como afirmaciones.** Se incluyen porque son respuestas reales al mensaje enviado y describen situaciones que el sistema debe saber manejar: P04, un usuario fuera del alcance (trabajador independiente), que debe ser informado con cortesía; P09, una posible irregularidad del empleador (falta de afiliación), que debe derivarse al Ministerio del Trabajo.
- Ambas se usarán en el conjunto de evaluación de la Semana 3 como entradas de tipo *fuera de dominio* y *derivación*.
- Consultas formuladas como preguntas: 15 de 17. P04 y P09 se conservan como afirmaciones recibidas.

## Resumen por tema

| Tema | Respuestas | N.º |
|---|---|---|
| Décimo tercero y décimo cuarto | P10, P11, P14, P15, P16 | 5 |
| Liquidación | P01, P06, P08 | 3 |
| Vacaciones | P03, P05, P07 | 3 |
| Horas suplementarias y extraordinarias | P12, P13 | 2 |
| Verificación de pagos | P02 | 1 |
| Afiliación / fuera de alcance | P04, P09 | 2 |
| Fondos de reserva / IESS | P17 | 1 |
| **Total** | | **17** |

## Hallazgos

1. **Se mantienen los temas de cálculo seleccionados.** 13 de las 17 respuestas tratan sobre décimos, liquidación, vacaciones u horas extra.
2. **Casi nadie da todos los datos.** Preguntas como P11 y P15 ("cuanto recibo de decimo") no indican sueldo ni fechas, y P01 no indica el motivo de salida. Esto justifica los **formularios guiados** y que el sistema **pida los datos que faltan** en lugar de suponerlos.
3. **Aparecen casos que no se deben calcular sino derivar.** P06 (afiliado solo una parte del tiempo y despedido) y P09 (sin afiliación) implican posibles incumplimientos del empleador: el sistema debe orientar y **derivar al Ministerio del Trabajo**, no dictaminar.
4. **Hay usuarios fuera del alcance.** P04 (trabajador independiente) confirma el alcance negativo y el perfil de trabajador informal como beneficiario indirecto.
5. **Surgen detalles a decidir en el diseño.** P12 (horas en feriados) y P13 (horas en la noche) plantean recargos especiales: jornada nocturna y trabajo en días de descanso. Se debe verificar en el Código del Trabajo si entran al alcance del cálculo de horas.
6. **Hay preguntas normativas, no solo de cálculo.** P03 ("¿en qué momento puedo pedir mis vacaciones?") se responde con el texto del Código mediante RAG; servirá para las 20 preguntas normativas de la Semana 3.
7. **Limitación del levantamiento:** todas las respuestas provienen de trabajadores; ninguna de empleadores. Las historias del perfil empleador se basan en el caso oficial y se recomienda consultar al menos a un pequeño empleador.
8. **Consultas con errores ortográficos y fuera del alcance.** P17 pregunta sobre fondos de reserva e IESS. El sistema debe comprender variaciones de escritura, solicitar aclaraciones cuando sea necesario y orientar hacia la institución correspondiente.

## Conclusión

Los temas más consultados fueron los décimos (5), seguidos de liquidación y vacaciones (3 cada uno), lo que confirma los cinco cálculos elegidos. Las respuestas reales llegan con datos incompletos y, en algunos casos, esconden conflictos laborales o situaciones fuera del alcance; por eso el sistema necesita formularios guiados, validación y derivación al Ministerio del Trabajo.

## Respaldo anonimizado

**Por qué existe:** documenta el origen de las respuestas mediante capturas anonimizadas de los chats, recopiladas en un documento de evidencias, sin exponer datos personales de quienes participaron.


| Aspecto | Cómo se maneja |
|---|---|
| **Qué se respalda** | Una captura de pantalla de cada respuesta de WhatsApp (17 capturas). |
| **Originales** | Las capturas sin editar las conserva el responsable del levantamiento en su dispositivo, **fuera del repositorio**. Se muestran al docente solo si las solicita y no se comparten con terceros. |
| **Cómo se anonimizan** | Antes de publicarlas se cubren con un rectángulo opaco: nombre o apodo del contacto, número de teléfono, foto de perfil y cualquier dato que identifique a la persona (empresa, ciudad, nombres de terceros). Se conservan el texto de la respuesta y la hora. |
| **Dónde se publican** | En `docs/evidencias/semana-1/encuesta/`, con nombres neutros: `respuesta-01.png` … `respuesta-17.png`, en el mismo orden que P01 … P17. |
| **Verificación** | Antes del commit, otro integrante revisa cada captura para confirmar que no queda ningún dato personal visible. |
| **Consentimiento** | El mensaje enviado aclaraba el propósito académico y que no se requerían datos personales; quien respondió lo hizo de forma voluntaria. |
| **Conservación** | Las capturas originales se eliminan al finalizar el seminario (después de la sustentación); en el repositorio solo permanecen las versiones anonimizadas. |
| **Estado** | Pendiente: las capturas anonimizadas se agregarán en un PR posterior de la Semana 1. |
