## ADR · Flujo automatizado con IA

*Taller de la Clase 4 · 29 de octubre de 2026 · Grupo 7 · Beneficios y liquidaciones laborales*
*Integrantes: Bladimir Velasco, Alexander Guerrero, Dorian Zambrano*

### Contexto
En el producto se repite un proceso que hoy hace una persona a mano: Solicitud de liquidación con fecha de ingreso, fecha de salida, sueldo y tipo de terminación (20 por día). Queremos automatizarlo sin que la IA tome decisiones exactas ni riesgosas.

### Decisión
- **Disparador:** Formulario web
- **Acción final:** Registrar la liquidación como pendiente con su base legal y avisar a RR. HH
- **Flujo fijo y no agente porque:** los pasos son siempre los mismos; hay que poder auditar cada decisión; un error tiene consecuencias de dinero o legales. Toda liquidación sigue los mismos pasos (clasificar, extraer, calcular, revisar, registrar) y cada monto debe poder auditarse contra el artículo del Código del Trabajo

| Estación | Qué hace | Decide | Qué sale |
|---|---|---|---|
| Disparador | Llega: solicitud de liquidación con fechas y sueldo (formulario web) | Sistema | Evento en la cola |
| Clasificar | Decidir el tipo (liquidación, consulta u otro) con un número de confianza | IA | JSON {tipo, confianza} |
| Umbral | Si la confianza es baja, desviar a revisión | Código | Sigue o va a revisión |
| Extraer | Sacar los campos: nombre, fecha de ingreso, fecha de salida, sueldo | IA | Datos validados con Pydantic |
| Reglas | Calcular décimos y vacaciones con Decimal y config/ | Código | Resultado exacto con su fuente |
| Revisión | RR. HH. aprueba antes de cualquier pago | Persona | Aprobado o corregido |
| Actuar | Registrar como pendiente (idempotente) y notificar a RR. HH. | Sistema | Registro con auditoría |

- **Umbral de confianza: 0.85** (en `config/parametros.yaml`). Con los 10 casos de práctica: 7 automáticos, 3 a revisión (30 %), 0 errores silenciosos. Motivo: Con 0.80 el caso de los dos temas (0.84) salía automático y mal. Desde 0.85 no hay errores silenciosos y solo 3 de 10 casos (30 %) van a revisión
- **La persona que revisa recibe:** La solicitud ya clasificada, los campos prellenados, el cálculo con su artículo y el motivo por el que fue a revisión

### Seguridad
- Todo lo que entra por el disparador es texto no confiable.
- La IA solo produce campos de un esquema validado; nunca ejecuta acciones.
- Ninguna estación automática mueve dinero ni envía a terceros sin una persona.
- Las acciones que escriben son idempotentes (no se duplican si se reintentan).

### Consecuencias
- El umbral se recalibra con el conjunto dorado (eval/casos_flujo.jsonl) cada vez que cambian el prompt o el modelo.
- Todo documento termina en un estado: procesado, en revisión o rechazado con motivo. Nunca se descarta en silencio.
- Pendiente para la Entrega 3: implementar app/flujo.py, completar los casos reales del conjunto dorado y correr eval/evaluar.py.
