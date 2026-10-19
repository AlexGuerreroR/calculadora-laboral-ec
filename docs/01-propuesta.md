# 01 · Propuesta del proyecto

**Caso 07 · Grupo 7** · Calculadora Inteligente de Beneficios y Liquidaciones Laborales
**Tipo de producto:** automatización de proceso con agente
**Integrantes:** Bladimir Velasco · Alexander Guerrero · Dorian Zambrano

## 1. Problema

Muchos trabajadores en relación de dependencia y pequeños empleadores en Ecuador no saben cómo se calculan el décimo tercer y décimo cuarto sueldo, las vacaciones, las horas suplementarias y extraordinarias, ni la liquidación al terminar una relación laboral. El Código del Trabajo y los acuerdos del Ministerio del Trabajo son públicos, pero interpretarlos requiere conocimiento jurídico.

**Qué pasa hoy sin el sistema:** el trabajador acepta el valor que le indican sin poder verificarlo, o busca en blogs y calculadoras sin fuente; el pequeño empleador calcula a mano y se equivoca. Resultado: cálculos incorrectos y conflictos laborales evitables.

**Evidencia del problema:** ver el levantamiento de preguntas reales en `docs/evidencias/semana-1/levantamiento.md`.

## 2. Usuarios

| Usuario | Necesidad |
|---|---|
| Trabajador en relación de dependencia | Saber cuánto le corresponde, entender cómo se calculó y verificar el monto que le indican. |
| Pequeño empleador | Calcular correctamente lo que debe pagar y tener un respaldo del cálculo. |
| Trabajador informal (beneficiario indirecto) | Conocer qué beneficios tendría con un contrato formal, el sistema no calcula su caso, pero le informa sus derechos. |

## 3. Solución propuesta

Aplicación web con formularios guiados que:

1. **Calcula** los beneficios con funciones deterministas probadas, nunca con el modelo.
2. **Explica** cada resultado en lenguaje sencillo con un modelo generativo, **citando el artículo** del Código del Trabajo recuperado mediante RAG.
3. **Genera un resumen descargable** en PDF.
4. **Deriva** al Ministerio del Trabajo los casos que requieren asesoría legal.

**Principio central:** el código calcula; la IA explica. Ningún número sale del texto generado.

## 4. Alcance

### Lo que hace · los cinco cálculos más consultados

| # | Cálculo | Base legal (a verificar en el texto oficial) |
|---|---|---|
| 1 | Décimo tercera remuneración | Código del Trabajo, art. 111 |
| 2 | Décimo cuarta remuneración | Código del Trabajo, art. 113 |
| 3 | Vacaciones | Código del Trabajo, arts. 69 y 71 |
| 4 | Horas suplementarias y extraordinarias | Código del Trabajo, art. 55 |
| 5 | Liquidación por renuncia/desahucio y despido intempestivo | Código del Trabajo, arts. 185 y 188 |

La selección se contrasta con el levantamiento de preguntas reales.

### Lo que nunca hará (alcance negativo)

- **No dictamina casos litigiosos** ni dice si conviene demandar: deriva al Ministerio del Trabajo.
- **No ayuda a incumplir la ley** (por ejemplo, "cómo no pagar el décimo"): se niega y explica la obligación.
- **No calcula montos con el modelo de IA.**
- **No pide ni guarda datos personales** (nombre, cédula, empresa): solo fechas y montos.
- No cubre utilidades, fondos de reserva, jubilación patronal, sector público (LOSEP), visto bueno ni indemnizaciones especiales: se declaran como fuera de alcance.

**Por qué:** son decisiones con consecuencias legales que requieren un profesional; un error del sistema podría perjudicar al trabajador.

## 5. Riesgos identificados

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El modelo inventa montos o artículos (alucinación) | Alto | Cálculos en código; cita obligatoria del artículo recuperado; abstención si no hay fuente. |
| Normativa o salario básico desactualizados | Alto | Parámetros en `config/parametros.yaml` con fuente y fecha; inventario de fuentes con vigencia. |
| Casos de referencia mal resueltos | Alto | Doble resolución independiente con instructivos oficiales. |
| Usuario usa el resultado como asesoría legal | Medio | Aviso de que es orientativo; derivación al Ministerio del Trabajo. |
| Inyección de prompt | Medio | Contexto recuperado delimitado como datos; pruebas de inyección. |
| Clave de API expuesta | Alto | Clave solo en variables de entorno; `.env` en `.gitignore`. |
| Agotar la capa gratuita del modelo | Medio | Pruebas automáticas con doble (mock) del modelo; avisar al docente. |
| Despliegue tardío | Medio | Desplegar entre el 31 de octubre y el 3 de noviembre. |

## 6. Modelo generativo elegido

**Gemini Flash (Google AI Studio, capa gratuita).**

**Justificación:**
- Es el stack base recomendado por la guía del seminario y no requiere tarjeta de crédito.
- La tarea del modelo es acotada (redactar una explicación a partir de un resultado y un artículo), así que un modelo rápido y económico es suficiente.
- El mismo proveedor ofrece embeddings para el RAG.
- **Temperatura:** la salida debe ser fiel a los datos, por lo que se intentará fijar una temperatura baja desde el backend (API). En la prueba en AI Studio, el modelo gemini-3.8-flash no permitió ajustarla; en la Semana 2 se verificará si la API lo acepta y se documentará el valor final. Si no es configurable, se mantiene el valor por defecto y la fidelidad se garantiza por diseño: cálculos en código, explicación limitada al resultado y al artículo recuperado, cita obligatoria y abstención sin fuente.

**Prueba inicial (18-oct-2026):** al preguntarle sin búsqueda web por el salario básico 2026, el modelo respondió que no lo conocía y dio un valor incorrecto para 2025. Esto confirma la decisión de no confiar en su memoria: los valores van en configuración y la normativa se recupera de fuentes oficiales.

## 7. Indicadores de calidad (del caso)

- 100 % de los 10 cálculos de referencia coincide con el cálculo manual (±0,01 USD).
- 100 % de las entradas inválidas se rechaza antes de llegar al modelo.
- Al menos 80 % de las explicaciones cita el artículo correcto del Código del Trabajo.

## 8. Datos y privacidad

Se aplica minimización de datos (Ley Orgánica de Protección de Datos Personales, 2021).

| Aspecto | Decisión |
|---|---|
| **Datos que pide el sistema** | Fechas de ingreso y salida, remuneraciones mensuales, horas suplementarias y extraordinarias, región y motivo de salida. **No** pide nombre, cédula, correo, teléfono ni empresa. |
| **Qué se envía al modelo (Gemini)** | Solo el tipo de cálculo, los montos ya calculados, el número de meses o años considerados y el fragmento del artículo recuperado. **No** se envían fechas exactas ni ningún dato que identifique a la persona. |
| **Qué se registra (logs)** | Por solicitud: tipo de cálculo, tiempo de respuesta, tokens consumidos y código de resultado (correcto, error de validación, derivación). **No** se registran fechas, montos ni texto escrito por el usuario. |
| **Qué se almacena** | Nada. Las entradas y los resultados se procesan en memoria y se descartan al responder; el PDF se genera en memoria y se entrega al usuario sin guardarse en el servidor. |
| **Proveedor externo** | La capa gratuita de Gemini puede usar lo que recibe para mejorar sus productos; por eso solo recibe datos ya minimizados. |
| **Aviso al usuario** | La interfaz indica que interactúa con IA, que el resultado es orientativo y no asesoría legal, y que no se guardan sus datos. |
