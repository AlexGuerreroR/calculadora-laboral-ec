# Ficha de RAG · Grupo 7 · Calculadora de beneficios y liquidaciones laborales

Integrantes: Alexander Guerrero, Bladimir Velasco, Dorian Zambrano
Fecha: 2026-10-27
Avance: 100 % (Fuentes, Corte, Etiquetas, Preguntas reales, Regla de silencio)

## Objetivo del RAG
Explicar derechos laborales citando el artículo del Código del Trabajo, calcular décimos, vacaciones y liquidaciones en código, y abstenerse de dictaminar casos litigiosos.

## 1. Fuentes
| Fuente | Dónde | Archivo en data/raw | Fecha/versión | Estado |
|---|---|---|---|---|
| Código del Trabajo | Registro Oficial / trabajo.gob.ec | CODIGO_DEL_TRABAJO.pdf | Codif. 2005-017, reforma RO 309 2023-05-12 | descargada |
| Acuerdo ministerial del salario básico unificado 2026 | Ministerio del Trabajo | acuerdo_sbu_2026_mdt-2025-195.pdf | MDT-2025-195, 2025-12-18 | descargada |
| Guías del Ministerio del Trabajo sobre décimos y liquidaciones | trabajo.gob.ec | — | — | pendiente |

## 2. Estrategia de corte
Por artículo. Cada explicación debe citar el artículo. Y cada cálculo (décimos, vacaciones, indemnización) lo hace una función de Python con pruebas, nunca el modelo.

## 3. Etiquetas (metadatos)
| Campo | Ejemplo del grupo | Para qué |
|---|---|---|
| documento | Código del Trabajo | Cita |
| articulo | 188 | Cita |
| tema | despido | Filtrar por tipo de consulta |
| vigente | true | Excluir texto reformado |

## 4. Preguntas de evaluación (eval/preguntas.json)
| # | Pregunta | Esperado | Tipo |
|---|---|---|---|
| 1 | Me botaron sin visto bueno después de 3 años, ¿qué me toca? | Art. 188 | Tiene respuesta en las fuentes |
| 2 | ¿Hasta cuándo me tienen que pagar el décimo tercero? | Art. 111 | Tiene respuesta en las fuentes |
| 3 | Llevo 7 años en la empresa, ¿cuántos días de vacaciones tengo? | Art. 69 | Tiene respuesta en las fuentes |
| 4 | Me voy de la empresa y no tomé mis vacaciones, ¿me las pagan? | Art. 71 | Tiene respuesta en las fuentes |
| 5 | ¿Cuánto me deben pagar por las horas extra que trabajo el domingo? | Art. 55 | Tiene respuesta en las fuentes |
| 6 | ¿Cuántas horas al día me pueden hacer trabajar? | Art. 47 | Tiene respuesta en las fuentes |
| 7 | ¿Cuánto es el décimo cuarto y quién lo recibe? | Art. 113 | Tiene respuesta en las fuentes |
| 8 | Me dieron el desahucio después de 5 años, ¿me toca alguna bonificación? | Art. 185 | Tiene respuesta en las fuentes |
| 9 | ¿Qué beneficios me da el contrato colectivo de mi empresa? | — | No está en las fuentes (debe abstenerse) |
| 10 | Mi jefe dice que renuncié pero yo no firmé nada, ¿quién tiene razón? | — | Requiere derivar a una persona |

## 5. Regla de silencio
Mensaje de abstención: No encontré ese tema en las normas que tengo cargadas (Código del Trabajo y acuerdos del Ministerio del Trabajo), así que no puedo darle una respuesta con fundamento. Tampoco puedo decidir quién tiene razón en un conflicto laboral. Le recomiendo acudir a la Inspectoría del Ministerio del Trabajo o a un consultorio jurídico gratuito.

## Error que debemos evitar
Dejar que el modelo calcule la liquidación «porque tiene el artículo en el contexto»: cada ejecución da un número distinto.

## Reto para avanzados
Diez cálculos de referencia en pytest con casos límite: 2 años y 11 meses frente a 3 años; más de 25 años de servicio.

## JSON para eval/preguntas.json
```json
[
  {
    "pregunta": "Me botaron sin visto bueno después de 3 años, ¿qué me toca?",
    "esperado": "Art. 188",
    "debe_abstenerse": false,
    "tipo": "con"
  },
  {
    "pregunta": "¿Hasta cuándo me tienen que pagar el décimo tercero?",
    "esperado": "Art. 111",
    "debe_abstenerse": false,
    "tipo": "con"
  },
  {
    "pregunta": "Llevo 7 años en la empresa, ¿cuántos días de vacaciones tengo?",
    "esperado": "Art. 69",
    "debe_abstenerse": false,
    "tipo": "con"
  },
  {
    "pregunta": "Me voy de la empresa y no tomé mis vacaciones, ¿me las pagan?",
    "esperado": "Art. 71",
    "debe_abstenerse": false,
    "tipo": "con"
  },
  {
    "pregunta": "¿Cuánto me deben pagar por las horas extra que trabajo el domingo?",
    "esperado": "Art. 55",
    "debe_abstenerse": false,
    "tipo": "con"
  },
  {
    "pregunta": "¿Cuántas horas al día me pueden hacer trabajar?",
    "esperado": "Art. 47",
    "debe_abstenerse": false,
    "tipo": "con"
  },
  {
    "pregunta": "¿Cuánto es el décimo cuarto y quién lo recibe?",
    "esperado": "Art. 113",
    "debe_abstenerse": false,
    "tipo": "con"
  },
  {
    "pregunta": "Me dieron el desahucio después de 5 años, ¿me toca alguna bonificación?",
    "esperado": "Art. 185",
    "debe_abstenerse": false,
    "tipo": "con"
  },
  {
    "pregunta": "¿Qué beneficios me da el contrato colectivo de mi empresa?",
    "esperado": null,
    "debe_abstenerse": true,
    "tipo": "sin"
  },
  {
    "pregunta": "Mi jefe dice que renuncié pero yo no firmé nada, ¿quién tiene razón?",
    "esperado": null,
    "debe_abstenerse": true,
    "tipo": "deriva"
  }
]
```