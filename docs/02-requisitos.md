# Requisitos del sistema

## 1. Objetivo

Definir los requisitos funcionales y no funcionales de la aplicación web **Calculadora Inteligente de Beneficios y Liquidaciones Laborales**, a partir de las necesidades identificadas para los perfiles de trabajador y empleador.

Los requisitos descritos en este documento servirán como base para el diseño, implementación, validación y pruebas del sistema.

---

# 2. Alcance

La aplicación permitirá realizar cálculos laborales mediante reglas deterministas y presentar una explicación comprensible de los resultados utilizando normativa laboral aplicable.

El alcance inicial incluye:

- cálculo de décima tercera remuneración;
- cálculo de décima cuarta remuneración;
- cálculo de vacaciones;
- cálculo de horas suplementarias y extraordinarias;
- estimación de liquidaciones laborales;
- validación de datos ingresados;
- explicación normativa de resultados;
- generación de un resumen descargable;
- identificación de consultas fuera del alcance de la aplicación.

El sistema no sustituirá asesoría jurídica profesional ni emitirá criterios definitivos en casos litigiosos o que requieran interpretación legal.

---

# 3. Perfiles de usuario

## 3.1. Trabajador

Persona que mantiene o mantuvo una relación laboral y desea consultar valores aproximados correspondientes a beneficios laborales o liquidaciones.

Principales necesidades:

- conocer cuánto le corresponde recibir;
- entender cómo se obtuvo el resultado;
- identificar la norma que respalda el cálculo;
- conocer qué información debe proporcionar;
- obtener un resumen del cálculo realizado.

---

## 3.2. Empleador

Persona natural o representante de una organización que requiere estimar obligaciones económicas relacionadas con sus trabajadores.

Principales necesidades:

- calcular correctamente beneficios laborales;
- verificar parámetros utilizados;
- reducir errores en cálculos manuales;
- obtener resultados desglosados;
- consultar la base normativa aplicable.

---

# 4. Trazabilidad con el levantamiento real

Las historias de usuario definidas en este documento se relacionan con las necesidades identificadas en el levantamiento de información realizado durante la Semana 1.

Las respuestas originales se encuentran documentadas en:

`docs/evidencias/semana-1/levantamiento.md`

Para mantener la trazabilidad, se utilizan los identificadores P01–P15 definidos en dicho documento.

Las historias HU-08 y HU-09 no provienen directamente de una pregunta de la encuesta:

- **HU-08** se deriva del objetivo del caso oficial, que requiere generar un resumen descargable.
- **HU-09** se deriva de la Fase 1 del caso oficial, que establece que parámetros como el Salario Básico Unificado deben mantenerse configurables.

No se crean nuevos identificadores Pxx dentro de este documento para evitar conflictos con las respuestas reales del levantamiento.

---

# 5. Historias de usuario

## HU-01. Calcular décima tercera remuneración

**Como** trabajador,  
**quiero** ingresar mis remuneraciones correspondientes al período de cálculo,  
**para** conocer el valor estimado de mi décima tercera remuneración.

**Preguntas relacionadas:** P10, P11, P14 y P15.

### Criterios de aceptación

**CA-01.1**  
**Dado** que el trabajador ha ingresado correctamente las remuneraciones correspondientes al período,  
**cuando** solicite el cálculo de décima tercera remuneración,  
**entonces** el sistema deberá presentar el valor calculado y el detalle utilizado para obtenerlo.

**CA-01.2**  
**Dado** que existen meses incompletos dentro del período,  
**cuando** el usuario realice el cálculo,  
**entonces** el sistema deberá considerar únicamente los valores correspondientes al tiempo efectivamente laborado.

**CA-01.3**  
**Dado** que el usuario ingresa una remuneración negativa o un dato obligatorio vacío,  
**cuando** intente realizar el cálculo,  
**entonces** el sistema deberá rechazar la entrada e indicar el dato que debe corregirse.

**CA-01.4**  
**Dado** que el cálculo se ha realizado correctamente,  
**cuando** se presente el resultado,  
**entonces** el sistema deberá mostrar la referencia normativa utilizada.

---

## HU-02. Calcular décima cuarta remuneración

**Como** trabajador,  
**quiero** calcular mi décima cuarta remuneración según mi región y período laboral,  
**para** conocer el valor que me corresponde recibir.

**Preguntas relacionadas:** P10, P11, P14 y P15.

### Criterios de aceptación

**CA-02.1**  
**Dado** que el trabajador selecciona Costa o Región Insular,  
**cuando** se realice el cálculo,  
**entonces** el sistema deberá utilizar el período de cálculo correspondiente a esa región.

**CA-02.2**  
**Dado** que el trabajador selecciona Sierra o Amazonía,  
**cuando** se realice el cálculo,  
**entonces** el sistema deberá utilizar el período aplicable a esa región.

**CA-02.3**  
**Dado** que el Salario Básico Unificado se encuentra configurado para el período consultado,  
**cuando** se realice el cálculo,  
**entonces** el sistema deberá utilizar ese valor como parámetro y no un valor fijo dentro de la fórmula.

**CA-02.4**  
**Dado** que falta la región o una fecha necesaria,  
**cuando** el usuario solicite el cálculo,  
**entonces** el sistema deberá impedir la operación e informar los datos faltantes.

---

## HU-03. Calcular vacaciones

**Como** trabajador,  
**quiero** ingresar mi fecha de ingreso y remuneración,  
**para** conocer el valor estimado correspondiente a mis vacaciones.

**Preguntas relacionadas:** P03, P05 y P07.

### Criterios de aceptación

**CA-03.1**  
**Dado** que el trabajador ingresa una fecha de ingreso válida y su remuneración,  
**cuando** solicite el cálculo,  
**entonces** el sistema deberá determinar el valor correspondiente a vacaciones según el tiempo laborado.

**CA-03.2**  
**Dado** que el trabajador no ha completado un período anual,  
**cuando** se calcule el beneficio,  
**entonces** el sistema deberá calcular el valor proporcional correspondiente.

**CA-03.3**  
**Dado** que la fecha de ingreso es posterior a la fecha actual o posterior a una fecha de salida ingresada,  
**cuando** se intente realizar el cálculo,  
**entonces** el sistema deberá rechazar los datos.

**CA-03.4**  
**Dado** que el cálculo se completa correctamente,  
**cuando** el sistema presente el resultado,  
**entonces** deberá indicar los artículos normativos relacionados con vacaciones.

---

## HU-04. Calcular horas suplementarias

**Como** pequeño empleador,  
**quiero** registrar la remuneración y las horas adicionales trabajadas por un trabajador,  
**para** estimar correctamente el valor correspondiente a horas suplementarias.

**Preguntas relacionadas:** P12 y P13.

### Criterios de aceptación

**CA-04.1**  
**Dado** que el empleador ingresa una remuneración válida y una cantidad válida de horas suplementarias,  
**cuando** ejecute el cálculo,  
**entonces** el sistema deberá aplicar el recargo correspondiente.

**CA-04.2**  
**Dado** que las horas fueron realizadas en un horario con diferente porcentaje de recargo,  
**cuando** se ejecute el cálculo,  
**entonces** el sistema deberá aplicar el porcentaje correspondiente según la normativa utilizada.

**CA-04.3**  
**Dado** que la cantidad de horas supera los límites admitidos por la normativa,  
**cuando** el usuario intente realizar el cálculo,  
**entonces** el sistema deberá advertir que los datos exceden el límite previsto.

---

## HU-05. Calcular horas extraordinarias

**Como** trabajador,  
**quiero** registrar las horas extraordinarias que he trabajado,  
**para** conocer el valor adicional que me corresponde recibir.

**Preguntas relacionadas:** P12 y P13.

### Criterios de aceptación

**CA-05.1**  
**Dado** que el trabajador proporciona una remuneración válida y el número de horas extraordinarias,  
**cuando** solicite el cálculo,  
**entonces** el sistema deberá mostrar el valor resultante aplicando el recargo correspondiente.

**CA-05.2**  
**Dado** que el trabajo corresponde a un período sujeto a un recargo del 100 %,  
**cuando** el sistema realice el cálculo,  
**entonces** deberá aplicar dicho porcentaje.

**CA-05.3**  
**Dado** que el número de horas ingresado es negativo, cero cuando se requiere un valor positivo o no es numérico,  
**cuando** se intente realizar el cálculo,  
**entonces** el sistema deberá rechazar la entrada.

---

## HU-06. Estimar liquidación laboral

**Como** trabajador,  
**quiero** ingresar los datos relacionados con la terminación de mi relación laboral,  
**para** obtener una estimación de los valores que podrían formar parte de mi liquidación.

**Preguntas relacionadas:** P01, P06 y P08.

### Criterios de aceptación

**CA-06.1**  
**Dado** que el usuario ingresa fechas, remuneración y forma de terminación válidas,  
**cuando** solicite una estimación,  
**entonces** el sistema deberá presentar los componentes que correspondan al escenario seleccionado.

**CA-06.2**  
**Dado** que exista un componente de vacaciones, décimos o bonificaciones pendientes,  
**cuando** se genere la estimación,  
**entonces** el sistema deberá mostrar cada valor de manera separada.

**CA-06.3**  
**Dado** que la fecha de salida es anterior a la fecha de ingreso,  
**cuando** se intente realizar la estimación,  
**entonces** el sistema deberá rechazar la solicitud.

**CA-06.4**  
**Dado** que el caso requiere determinar responsabilidades, existencia de despido ilegal u otra controversia jurídica,  
**cuando** el usuario solicite una conclusión legal,  
**entonces** el sistema deberá indicar que el caso requiere asesoría especializada.

---

## HU-07. Consultar explicación normativa del resultado

**Como** trabajador o empleador,  
**quiero** conocer cómo se obtuvo el resultado y qué norma lo respalda,  
**para** comprender el cálculo presentado por el sistema.

**Preguntas relacionadas:** P02 y P03.

### Criterios de aceptación

**CA-07.1**  
**Dado** que existe un cálculo realizado correctamente,  
**cuando** el usuario solicite su explicación,  
**entonces** el sistema deberá explicar el procedimiento utilizando lenguaje comprensible.

**CA-07.2**  
**Dado** que existe una disposición normativa aplicable,  
**cuando** se genere la explicación,  
**entonces** deberá mostrarse como mínimo el documento y artículo relacionado.

**CA-07.3**  
**Dado** que no se encuentre una fuente normativa suficiente para respaldar una afirmación,  
**cuando** se genere la respuesta,  
**entonces** el sistema no deberá presentar dicha afirmación como una conclusión jurídica confirmada.

---

## HU-08. Generar resumen descargable

**Como** trabajador o empleador,  
**quiero** descargar un resumen del cálculo realizado,  
**para** conservar la información obtenida y revisarla posteriormente.

**Origen:** Caso oficial del proyecto – generación de resumen descargable.

### Criterios de aceptación

**CA-08.1**  
**Dado** que existe un cálculo válido,  
**cuando** el usuario solicite generar el resumen,  
**entonces** el sistema deberá producir un documento descargable.

**CA-08.2**  
**Dado** que se genere el resumen,  
**cuando** el usuario lo abra,  
**entonces** deberá incluir los datos utilizados, resultados obtenidos y referencias normativas principales.

**CA-08.3**  
**Dado** que no existe un cálculo previo válido,  
**cuando** el usuario solicite el documento,  
**entonces** el sistema deberá impedir su generación e informar que primero debe realizar un cálculo.

---

## HU-09. Configurar parámetros laborales

**Como** administrador del sistema,  
**quiero** mantener configurables los parámetros laborales que cambian con el tiempo,  
**para** actualizar la aplicación sin modificar las fórmulas internas.

**Origen:** Caso oficial del proyecto – Fase 1, parámetros configurables.

### Criterios de aceptación

**CA-09.1**  
**Dado** que existe un nuevo valor oficial del Salario Básico Unificado,  
**cuando** se actualice la configuración,  
**entonces** los cálculos posteriores deberán utilizar el nuevo valor.

**CA-09.2**  
**Dado** que existe un valor configurado para un período determinado,  
**cuando** se realice un cálculo correspondiente a ese período,  
**entonces** el sistema deberá utilizar el parámetro que corresponda.

**CA-09.3**  
**Dado** que un parámetro obligatorio no está configurado,  
**cuando** se intente ejecutar un cálculo que dependa de él,  
**entonces** el sistema deberá impedir la operación y reportar el problema de configuración.

---

## HU-10. Rechazar consultas fuera del alcance

**Como** trabajador en conflicto con su empleador,  
**quiero** recibir una indicación clara cuando mi consulta no pueda ser resuelta por la aplicación,  
**para** saber cuándo debo acudir a una autoridad o asesoría especializada.

**Preguntas relacionadas:** P04, P06 y P09.

### Criterios de aceptación

**CA-10.1**  
**Dado** que el trabajador solicita una interpretación jurídica sobre un conflicto laboral,  
**cuando** el sistema identifique que la consulta supera su alcance,  
**entonces** deberá abstenerse de emitir un dictamen.

**CA-10.2**  
**Dado** que una consulta requiere determinar responsabilidades legales,  
**cuando** sea procesada,  
**entonces** el sistema deberá recomendar acudir al Ministerio del Trabajo o a un profesional competente.

**CA-10.3**  
**Dado** que la consulta sí pertenece al alcance de los cálculos definidos,  
**cuando** el usuario la realice,  
**entonces** el sistema deberá permitir continuar con el flujo correspondiente.

**CA-10.4**  
**Dado** que un empleador solicita instrucciones para evitar el pago de un beneficio u obligación laboral,  
**cuando** envíe la consulta,  
**entonces** el sistema deberá negarse a proporcionar instrucciones para incumplir la normativa y deberá explicar que la obligación debe cumplirse conforme a la legislación aplicable.

---

# 6. Matriz de trazabilidad

| Historia | Perfil | Fuente / preguntas relacionadas | Funcionalidad |
|---|---|---|---|
| HU-01 | Trabajador | P10, P11, P14, P15 | Décima tercera remuneración |
| HU-02 | Trabajador | P10, P11, P14, P15 | Décima cuarta remuneración |
| HU-03 | Trabajador | P03, P05, P07 | Vacaciones |
| HU-04 | Pequeño empleador | P12, P13 | Horas suplementarias |
| HU-05 | Trabajador | P12, P13 | Horas extraordinarias |
| HU-06 | Trabajador | P01, P06, P08 | Liquidación laboral |
| HU-07 | Trabajador / Empleador | P02, P03 | Explicación normativa |
| HU-08 | Trabajador / Empleador | Caso oficial del proyecto | Resumen descargable |
| HU-09 | Administrador | Caso oficial – Fase 1 | Parámetros configurables |
| HU-10 | Trabajador en conflicto | P04, P06, P09 | Control de alcance y derivación |

---

# 7. Casos de uso

## CU-01. Calcular beneficio laboral

**Actor principal:** Trabajador o empleador.

### Precondiciones

- El usuario debe seleccionar un cálculo disponible.
- Los parámetros laborales necesarios deben estar configurados.

### Flujo principal

1. El usuario accede a la calculadora.
2. Selecciona el beneficio laboral que desea calcular.
3. El sistema muestra los campos requeridos.
4. El usuario ingresa la información solicitada.
5. El sistema valida los datos.
6. El sistema ejecuta el cálculo determinista.
7. El sistema presenta el resultado desglosado.
8. El sistema muestra la referencia normativa relacionada.
9. El usuario puede solicitar una explicación o generar un resumen.

### Flujos alternativos

**A1. Datos incompletos**

1. El usuario deja uno o más campos obligatorios vacíos.
2. El sistema identifica los campos faltantes.
3. El cálculo no se ejecuta.
4. El usuario corrige la información.

**A2. Valor inválido**

1. El usuario ingresa una remuneración negativa o dato fuera del rango permitido.
2. El sistema rechaza la entrada.
3. Se informa el motivo de la validación.

**A3. Fecha inválida**

1. El usuario ingresa una fecha futura no permitida o una fecha de salida anterior a la fecha de ingreso.
2. El sistema rechaza la solicitud.
3. Se solicita corregir la información.

---

## CU-02. Estimar liquidación laboral

**Actor principal:** Trabajador o empleador.

### Flujo principal

1. El usuario selecciona la opción de liquidación.
2. Ingresa fecha de ingreso.
3. Ingresa fecha de salida.
4. Ingresa remuneración.
5. Selecciona el motivo o modalidad de terminación disponible.
6. El sistema valida los datos.
7. Se calculan los componentes aplicables.
8. El resultado se presenta de manera desglosada.
9. Se muestran las referencias normativas.
10. El usuario puede generar un resumen.

### Flujo alternativo

Si el usuario describe una controversia jurídica que no puede resolverse mediante datos objetivos, el sistema deberá indicar que el caso está fuera del alcance de la calculadora.

---

## CU-03. Obtener explicación normativa

**Actor principal:** Trabajador o empleador.

### Flujo principal

1. El usuario realiza un cálculo válido.
2. Solicita una explicación.
3. El sistema recupera la información normativa relacionada.
4. Se genera una explicación en lenguaje sencillo.
5. Se muestra el documento y artículo que respaldan la explicación.

### Flujo alternativo

Si no existe suficiente evidencia normativa recuperada, el sistema deberá indicar la limitación y evitar generar una conclusión jurídica no respaldada.

---

## CU-04. Generar resumen

**Actor principal:** Trabajador o empleador.

### Flujo principal

1. El usuario completa un cálculo.
2. Selecciona la opción de generar resumen.
3. El sistema incorpora los datos utilizados.
4. Incluye los resultados calculados.
5. Incorpora las referencias normativas principales.
6. Genera el archivo descargable.

---

# 8. Requisitos funcionales

**RF-01.** El sistema deberá calcular la décima tercera remuneración.

**RF-02.** El sistema deberá calcular la décima cuarta remuneración.

**RF-03.** El sistema deberá calcular vacaciones.

**RF-04.** El sistema deberá calcular horas suplementarias.

**RF-05.** El sistema deberá calcular horas extraordinarias.

**RF-06.** El sistema deberá estimar valores correspondientes a una liquidación laboral dentro del alcance definido.

**RF-07.** El sistema deberá validar todas las entradas antes de ejecutar un cálculo.

**RF-08.** El sistema deberá presentar resultados de manera desglosada.

**RF-09.** El sistema deberá relacionar los resultados con las fuentes normativas aplicables.

**RF-10.** El sistema deberá generar explicaciones comprensibles a partir de los resultados deterministas.

**RF-11.** El sistema deberá permitir generar un resumen descargable.

**RF-12.** El sistema deberá permitir modificar parámetros variables como el Salario Básico Unificado sin alterar las fórmulas internas.

**RF-13.** El sistema deberá identificar consultas fuera del alcance definido.

**RF-14.** El sistema deberá recomendar acudir al Ministerio del Trabajo cuando el caso requiera asesoría o interpretación jurídica especializada.

---

# 9. Requisitos no funcionales

## RNF-01. Tiempo de respuesta

Los cálculos deterministas deberán devolver un resultado en un tiempo máximo de **2 segundos** en condiciones normales de operación.

Las explicaciones que utilicen el modelo generativo deberán responder en un tiempo máximo objetivo de **10 segundos**, dependiendo de la disponibilidad del proveedor utilizado.

---

## RNF-02. Trazabilidad

El **100 % de las explicaciones normativas mostradas al usuario** deberá identificar como mínimo:

- fuente normativa;
- número de artículo o sección utilizada;
- cálculo al que corresponde.

---

## RNF-03. Privacidad

La aplicación no deberá almacenar información personal que no sea necesaria para realizar el cálculo solicitado.

Las credenciales, tokens y claves utilizadas por servicios externos deberán mantenerse exclusivamente en variables de entorno del backend y no deberán almacenarse en el repositorio.

---

## RNF-04. Disponibilidad para revisión

Durante la revisión y demostración del proyecto, el backend desplegado deberá encontrarse accesible mediante la URL documentada.

El endpoint:

`GET /health`

deberá responder con código HTTP 200 y una respuesta válida mientras el servicio se encuentre desplegado para revisión.

La disponibilidad continua fuera del período de evaluación dependerá de las condiciones y limitaciones del proveedor de alojamiento utilizado.

---

## RNF-05. Exactitud

Los cálculos deterministas deberán coincidir con los casos de referencia definidos para el proyecto con una tolerancia máxima de **±0,01 USD**.

---

## RNF-06. Validación

El **100 % de las entradas inválidas definidas en los casos de prueba** deberá ser rechazado antes de ejecutar el cálculo correspondiente.

---

## RNF-07. Seguridad

Las claves de servicios externos no deberán exponerse:

- en el frontend;
- en archivos públicos;
- en commits;
- en mensajes de error;
- en documentos generados.

---

## RNF-08. Mantenibilidad

Los parámetros laborales sujetos a cambios normativos deberán mantenerse separados de las fórmulas principales para permitir su actualización sin modificar la lógica completa del sistema.

---

# 10. Validaciones de entrada

El sistema deberá rechazar o advertir sobre los siguientes datos:

- remuneraciones negativas;
- valores no numéricos en campos numéricos;
- campos obligatorios vacíos;
- fechas futuras cuando no correspondan;
- fecha de salida anterior a fecha de ingreso;
- períodos de cálculo inválidos;
- cantidades negativas de horas;
- horas adicionales superiores a límites permitidos;
- regiones no contempladas;
- parámetros laborales inexistentes;
- datos incompatibles entre sí.

---

# 11. Límites del sistema

La aplicación tendrá los siguientes límites:

- No determinará judicialmente si existió o no despido ilegal.
- No resolverá controversias entre trabajador y empleador.
- No sustituirá asesoría jurídica.
- No emitirá sentencias ni dictámenes jurídicos.
- No garantizará que una estimación de liquidación corresponda exactamente con el valor reconocido posteriormente por una autoridad.
- No utilizará información normativa sin identificar su fuente.
- No permitirá que el modelo generativo modifique los resultados obtenidos por las herramientas deterministas.
- No responderá como conclusión jurídica definitiva cuando la información disponible sea insuficiente.
- No proporcionará instrucciones destinadas a evadir o incumplir obligaciones laborales.

---

# 12. Relación entre requisitos y módulos previstos

| Módulo | Requisitos principales |
|---|---|
| Cálculo de décimos | RF-01, RF-02, RF-07, RF-08 |
| Cálculo de vacaciones | RF-03, RF-07, RF-08 |
| Horas adicionales | RF-04, RF-05, RF-07, RF-08 |
| Liquidaciones | RF-06, RF-07, RF-08 |
| Explicación normativa | RF-09, RF-10, RF-13, RF-14 |
| Generación de resumen | RF-11 |
| Configuración | RF-12 |
| Validaciones | RF-07 |

---