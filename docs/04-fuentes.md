# Inventario de fuentes oficiales

## Objetivo

Reunir, verificar y documentar las fuentes normativas necesarias para fundamentar los cálculos laborales implementados en la aplicación **Calculadora Inteligente de Beneficios y Liquidaciones Laborales**.

Las fuentes recopiladas serán utilizadas posteriormente como base para la implementación del sistema de recuperación aumentada por generación (RAG), permitiendo que las explicaciones generadas por el sistema incluyan referencias normativas verificables.

## Criterios de selección

Las fuentes incluidas deben:

- Proceder de organismos oficiales o reproducir normativa publicada oficialmente.
- Permitir identificar claramente la norma y su fecha de publicación.
- Ser legibles.
- Contener disposiciones relacionadas con los cálculos incluidos en el proyecto.
- Permitir identificar artículos, disposiciones o secciones relevantes.
- Registrar su vigencia o señalar expresamente cuando esta requiera comprobación adicional.
- Permitir fundamentar los parámetros variables utilizados por la aplicación.

---

# Resumen de fuentes

| N.º | Documento | Institución / Fuente normativa | Fecha | Vigencia | Archivo local |
|---|---|---|---|---|---|
| 1 | Código del Trabajo | Registro Oficial / legislación ecuatoriana | 16-12-2005 | Vigente. Última reforma identificada: 18-05-2026 | `data/raw/codigo_trabajo_ecuador_2026.pdf` |
| 2 | Acuerdo Ministerial MDT-2025-195 | Ministerio del Trabajo | 15-12-2025 / publicado 18-12-2025 | Aplicable al SBU 2026 | `data/raw/acuerdo_sbu_2026_mdt-2025-195.pdf` |
| 3 | Acuerdo Ministerial MDT-2023-140 | Ministerio del Trabajo | 14-11-2023 | Vigente como norma aplicable a obligaciones del empleador, décimos, utilidades, actas de finiquito e inspecciones | `data/raw/mdt-2023-140_obligaciones_empleador.pdf` |

---

# 1. Código del Trabajo

**Título:** Código del Trabajo  
**Codificación:** Codificación No. 2005-017  
**Institución normativa:** H. Congreso Nacional – Comisión de Legislación y Codificación  
**Publicación:** Suplemento del Registro Oficial No. 167  
**Fecha de publicación:** 16 de diciembre de 2005  
**Estado normativo indicado en el documento:** Vigente  
**Última reforma indicada:** Suplemento del Registro Oficial No. 286, 18 de mayo de 2026  
**Fecha de consulta:** 17 de octubre de 2026  
**Formato:** PDF  
**Archivo local:** `data/raw/codigo_trabajo_ecuador_2026.pdf`  
**URL de procedencia:** https://biblioteca.defensoria.gob.ec/bitstream/37000/3819/12/C%c3%93DIGO%20DEL%20TRABAJO.%20ACTUALIZADO.pdf

El documento consultado identifica expresamente la normativa como vigente y registra como última reforma el 18 de mayo de 2026. 

## Uso dentro del proyecto

El Código del Trabajo constituye la principal fuente normativa del sistema y será utilizado para:

- fundamentar el cálculo de remuneraciones adicionales;
- determinar las reglas relacionadas con jornada laboral;
- calcular horas suplementarias y extraordinarias;
- calcular vacaciones;
- fundamentar componentes de liquidación laboral;
- identificar las causas de terminación de la relación laboral;
- determinar bonificaciones e indemnizaciones;
- proporcionar artículos normativos al sistema RAG.

---

## 1.1. Salario y remuneración

### Artículos relevantes

- **Art. 81:** Estipulación de sueldos y salarios.
- **Art. 95:** Sueldo o salario y retribución accesoria.
- **Art. 117:** Remuneración unificada.
- **Arts. 118 y 119:** Consejo Nacional de Trabajo y Salarios y fijación de remuneraciones.

El artículo 81 establece que los sueldos y salarios no pueden ser inferiores a los mínimos legales establecidos. El mismo documento incorpora una nota respecto al SBU 2026 por USD 482,00.

### Uso previsto

Estos artículos serán utilizados como base para:

- validar la remuneración ingresada;
- determinar la remuneración base para otros cálculos;
- relacionar los cálculos con el Salario Básico Unificado vigente.

---

## 1.2. Décima tercera remuneración

### Artículos relevantes

- **Art. 111:** Derecho a la décima tercera remuneración o bono navideño.
- **Art. 112:** Exclusión de la decimotercera remuneración.

El artículo 111 establece el derecho del trabajador a recibir la parte proporcional correspondiente a la doceava parte de las remuneraciones percibidas y permite la acumulación mediante solicitud escrita. 

El artículo 112 determina que la décima tercera remuneración no se considera parte de la remuneración anual para determinados efectos como aportes al IESS, fondos de reserva, jubilación, indemnizaciones y vacaciones. 

### Uso previsto

Estos artículos servirán para:

- calcular la décima tercera remuneración;
- explicar la base normativa del cálculo;
- determinar el tratamiento de este beneficio dentro de otros cálculos.

---

## 1.3. Décima cuarta remuneración

### Artículos relevantes

- **Art. 113:** Derecho a la decimocuarta remuneración.
- **Art. 114:** Exclusión de la decimocuarta remuneración.

El artículo 113 establece el derecho del trabajador a recibir una bonificación equivalente a la doceava parte de la remuneración básica mínima unificada. 

### Uso previsto

Estos artículos serán utilizados para:

- calcular la décima cuarta remuneración;
- relacionar el cálculo con el Salario Básico Unificado vigente;
- explicar el resultado mediante una referencia normativa.

---

## 1.4. Jornada laboral

### Artículo relevante

- **Art. 47:** Jornada máxima.

La jornada máxima ordinaria es de **ocho horas diarias**, sin exceder de **cuarenta horas semanales**, salvo las excepciones previstas por la ley. 

### Uso previsto

Este artículo permitirá:

- identificar la jornada ordinaria;
- determinar cuándo existe trabajo adicional;
- servir de base para los cálculos de horas suplementarias y extraordinarias.

---

## 1.5. Horas suplementarias y extraordinarias

### Artículo relevante

- **Art. 55:** Remuneración por horas suplementarias y extraordinarias.

Reglas principales identificadas:

- Las horas suplementarias no podrán exceder de cuatro horas en un día.
- No podrán exceder de doce horas en una semana.
- Las horas suplementarias realizadas durante el día o hasta las 24H00 tienen un recargo del **50 %**.
- Las horas comprendidas entre las 24H00 y las 06H00 tienen un recargo del **100 %**.
- El trabajo realizado en sábado o domingo debe pagarse con un recargo del **100 %**.
- Para el cálculo de los recargos se toma como base la remuneración correspondiente a la hora de trabajo diurno.

Estas reglas constan en el artículo 55 del Código del Trabajo. 

### Uso previsto

El artículo 55 será utilizado para:

- calcular horas suplementarias;
- calcular horas extraordinarias;
- aplicar los porcentajes de recargo;
- validar límites máximos;
- explicar el cálculo realizado al usuario.

---

## 1.6. Vacaciones

### Artículos relevantes

- **Art. 69:** Vacaciones anuales.
- **Art. 70:** Facultad del empleador.
- **Art. 71:** Liquidación para pago de vacaciones.
- **Art. 72:** Vacaciones anuales irrenunciables.
- **Art. 73:** Fijación del período vacacional.
- **Art. 74:** Postergación de vacaciones por el empleador.
- **Art. 75:** Acumulación de vacaciones.
- **Art. 76:** Compensación por vacaciones.

### Art. 69 – Vacaciones anuales

Todo trabajador tiene derecho a un período anual ininterrumpido de **15 días de descanso**, incluidos los días no laborables.

Los trabajadores que hayan prestado servicios durante más de cinco años para el mismo empleador tienen derecho a un día adicional por cada año excedente.

Los días adicionales por antigüedad no podrán exceder de quince, salvo que exista una condición contractual más favorable.

### Art. 71 – Liquidación para pago de vacaciones

La liquidación para el pago de vacaciones se realiza utilizando la **veinticuatroava parte de lo percibido durante un año completo de trabajo**.

Para el cálculo se consideran:

- horas ordinarias;
- horas suplementarias;
- horas extraordinarias;
- otras retribuciones accesorias de carácter normal.

Si el trabajador termina la relación laboral sin haber gozado de vacaciones, tiene derecho a la parte proporcional correspondiente al tiempo de servicio. 

### Art. 72 – Irrenunciabilidad

Las vacaciones anuales constituyen un derecho irrenunciable.

### Art. 73 – Período vacacional

Regula la fijación del período durante el cual el trabajador hará uso de sus vacaciones.

### Art. 74 – Postergación

Permite la postergación de vacaciones en determinadas situaciones previstas por la ley.

Cuando el trabajador no haya podido gozar las vacaciones postergadas y salga del servicio, tendrá derecho a las remuneraciones correspondientes conforme lo previsto en el artículo. 

### Art. 75 – Acumulación

El trabajador podrá acumular las vacaciones hasta por tres años consecutivos para utilizarlas en el cuarto año.

### Art. 76 – Compensación

Cuando el trabajador no haya gozado de vacaciones, tendrá derecho al equivalente de las remuneraciones correspondientes a ese período, aplicándose la forma de liquidación prevista en el artículo 71. 

### Uso previsto

Los artículos 69 y 71 serán utilizados principalmente por la función:

`calcular_vacaciones(fecha_ingreso, remuneracion)`

Los artículos 72 al 76 servirán para explicar situaciones específicas relacionadas con:

- vacaciones no gozadas;
- acumulación;
- postergación;
- compensación.

---

## 1.7. Terminación de la relación laboral

### Artículos relevantes

- **Art. 169:** Causas para la terminación del contrato individual.
- **Art. 184:** Desahucio.
- **Art. 185:** Bonificación por desahucio.
- **Art. 188:** Indemnización por despido intempestivo.
- **Art. 191:** Indemnizaciones y bonificaciones al trabajador.
- **Art. 192:** Efectos del cambio de ocupación.

### Art. 184 – Desahucio

Regula la terminación de la relación laboral mediante desahucio.

### Art. 185 – Bonificación por desahucio

La bonificación por desahucio corresponde al **25 % de la última remuneración mensual por cada año de servicio** en los casos previstos por la norma. 

### Uso previsto

Este artículo será utilizado para:

- calcular la bonificación por desahucio;
- explicar la base legal de este componente de la liquidación.

---

## 1.8. Despido intempestivo

### Artículo relevante

- **Art. 188:** Indemnización por despido intempestivo.

Las reglas identificadas son:

- Hasta tres años de servicio: indemnización equivalente a **tres meses de remuneración**.
- Más de tres años: indemnización equivalente a **un mes de remuneración por cada año de servicio**.
- El valor máximo de indemnización es de **25 meses de remuneración**.
- La fracción de un año se considera como año completo.
- El cálculo se basa en la remuneración que estuviera percibiendo el trabajador al momento del despido.

Estas reglas constan en el artículo 188. 

El documento también incorpora una nota de 2025 respecto a la remuneración aplicable para el cálculo de indemnizaciones por despido intempestivo. 

### Uso previsto

Este artículo será utilizado por la función:

`estimar_liquidacion(datos)`

para determinar los componentes relacionados con despido intempestivo.

---

## 1.9. Otros artículos relacionados con liquidaciones

### Art. 191

Reconoce determinadas indemnizaciones y bonificaciones cuando el trabajador se separa como consecuencia de causas previstas en el artículo 173.

### Art. 192

Regula los efectos derivados de un cambio de ocupación ordenado unilateralmente por el empleador. 

### Uso previsto

Estos artículos servirán principalmente para:

- explicar determinados escenarios;
- identificar situaciones que requieren análisis normativo adicional;
- evitar que la aplicación emita conclusiones jurídicas en casos complejos.

---

# 2. Acuerdo Ministerial MDT-2025-195

**Título:** Acuerdo Ministerial Nro. MDT-2025-195 – Fijación del Salario Básico Unificado del Trabajador en General para el año 2026  
**Institución:** Ministerio del Trabajo del Ecuador  
**Número:** MDT-2025-195  
**Fecha de suscripción:** 15 de diciembre de 2025  
**Publicación:** Suplemento No. 187 del Registro Oficial  
**Fecha de publicación:** 18 de diciembre de 2025  
**Fecha de consulta:** 17 de octubre de 2026  
**Formato:** PDF  
**Archivo local:** `data/raw/acuerdo_sbu_2026_mdt-2025-195.pdf`  
**URL de procedencia:** https://www.trabajo.gob.ec/wp-content/uploads/downloads/2026/01/ACUERDO-MINISTERIAL-MDT-2025-195.pdf

## Parámetro identificado

### Salario Básico Unificado 2026

**USD 482,00**

El artículo único del Acuerdo Ministerial fija el Salario Básico Unificado del trabajador en general en **cuatrocientos ochenta y dos dólares de los Estados Unidos de América (USD 482,00)** a partir del **1 de enero de 2026**. 

El acuerdo comprende, entre otros:

- trabajadores de la pequeña industria;
- trabajadores agrícolas;
- trabajadores de maquila;
- trabajadores remunerados del hogar;
- operarios de artesanías;
- colaboradores de microempresa.

## Uso dentro del sistema

El Salario Básico Unificado será manejado como un parámetro configurable y no deberá quedar fijado directamente dentro de las fórmulas.

Ejemplo conceptual:

`SBU_2026 = 482.00`

Este valor será utilizado principalmente para:

- cálculo de décima cuarta remuneración;
- validación del salario mínimo;
- cálculos cuyo resultado dependa del SBU vigente.

## Secciones relevantes

- Considerandos relacionados con los artículos 81, 117, 118, 119 y 539 del Código del Trabajo.
- **Artículo Único:** fija el SBU del año 2026.
- **Disposición General Única:** establece que los salarios no podrán ser inferiores al mínimo legal.
- **Disposición Final Única:** establece la entrada en vigencia del acuerdo.

## Vigencia

El Acuerdo Ministerial establece que entra en vigencia desde su suscripción, sin perjuicio de su publicación en el Registro Oficial.

Para los cálculos correspondientes al año 2026, el valor aplicable es:

**SBU = USD 482,00 desde el 1 de enero de 2026.**

---

# 3. Acuerdo Ministerial MDT-2023-140

**Título:** Normas Generales Aplicables al Control de las Obligaciones del Empleador y los Procedimientos de Inspección  
**Norma:** Acuerdo Ministerial No. MDT-2023-140  
**Institución:** Ministerio del Trabajo del Ecuador  
**Fecha:** 14 de noviembre de 2023  
**Fecha de consulta:** 17 de octubre de 2026  
**Formato:** PDF  
**Archivo local:** `data/raw/mdt-2023-140_obligaciones_empleador.pdf`  
**URL de procedencia:** https://www.trabajo.gob.ec/wp-content/uploads/downloads/2024/01/MDT-2023-140-AM-Obligaciones-empleador-y-procedimientos-de-inspeccion-14-11-23-signed.pdf

## Objeto

El Acuerdo Ministerial establece normas generales para el control de las obligaciones del empleador y regula los procedimientos de inspección.

Su ámbito comprende a empleadores y trabajadores sujetos al Código del Trabajo, así como a las autoridades laborales responsables del control de estas obligaciones.

---

## 3.1. Décima tercera y décima cuarta remuneración

El Título II, Capítulo I, regula aspectos relacionados con la decimotercera y decimocuarta remuneración.

### Artículo 8 – Decimotercera y decimocuarta remuneración

Los sujetos obligados, la forma y el cálculo de la decimotercera y decimocuarta remuneración se regulan de conformidad con lo establecido en el Código del Trabajo.

Este artículo será utilizado como vínculo entre el Acuerdo Ministerial y los artículos 111 y 113 del Código del Trabajo.

---

## 3.2. Artículo 9 – Solicitud de acumulación

Los trabajadores que deseen acumular la decimotercera y/o decimocuarta remuneración deben presentar una solicitud escrita al empleador durante los primeros quince días de enero de cada año.

En nuevas relaciones laborales, el trabajador deberá manifestar por escrito la modalidad de pago dentro de los quince días posteriores al inicio de labores.

Cuando un trabajador cambie de modalidad acumulada a mensual, deberá solicitarlo por escrito hasta el 15 de enero.

Los valores acumulados deberán pagarse:

- Décima tercera remuneración: hasta el 24 de diciembre.
- Décima cuarta remuneración en Costa e Insular: hasta el 15 de marzo.
- Décima cuarta remuneración en Sierra y Amazonía: hasta el 15 de agosto.

---

## 3.3. Artículo 10 – Períodos de cálculo

Los períodos de cálculo establecidos son:

### Decimotercera remuneración

Desde el **1 de diciembre hasta el 30 de noviembre del año siguiente**.

### Decimocuarta remuneración – Costa e Insular

Desde el **1 de marzo hasta el último día de febrero del año siguiente**.

### Decimocuarta remuneración – Sierra y Amazonía

Desde el **1 de agosto hasta el 31 de julio del año siguiente**.

Estos períodos serán utilizados por las funciones de cálculo de décimos y para validar las fechas ingresadas por el usuario.

---

## 3.4. Artículo 11 – Registro del pago

Los empleadores deberán registrar el pago de la decimotercera y decimocuarta remuneración mediante la plataforma informática que el Ministerio del Trabajo disponga.

El registro se realizará de acuerdo con el noveno dígito del RUC o cédula del empleador y conforme al cronograma establecido en el propio Acuerdo.

### Decimotercera remuneración

Para todas las regiones del Ecuador:

- Noveno dígito 1, 2, 3, 4 o 5: registro del 5 de enero al 5 de febrero.
- Noveno dígito 6, 7, 8, 9 o 0: registro del 6 de febrero al 6 de marzo.

### Decimocuarta remuneración – Costa e Insular

- Noveno dígito 1, 2, 3, 4 o 5: registro del 20 de marzo al 20 de abril.
- Noveno dígito 6, 7, 8, 9 o 0: registro del 21 de abril al 21 de mayo.

### Decimocuarta remuneración – Sierra y Amazonía

- Noveno dígito 1, 2, 3, 4 o 5: registro del 20 de agosto al 20 de septiembre.
- Noveno dígito 6, 7, 8, 9 o 0: registro del 21 de septiembre al 21 de octubre.

---

## 3.5. Artículo 12 – Servicio doméstico

Los empleadores del servicio doméstico se sujetan a las mismas reglas de cálculo y fechas de pago aplicables a los trabajadores en general.

El registro deberá realizarse mediante el módulo correspondiente de la plataforma que disponga el Ministerio del Trabajo.

---

## 3.6. Actas de finiquito

El mismo Acuerdo regula las actas de finiquito, por lo cual también constituye una fuente relevante para la función de estimación de liquidaciones.

### Artículo 19 – Registro de actas de finiquito

Cuando finalice una relación laboral, el empleador deberá elaborar y registrar el acta de finiquito en el sistema que establezca el Ministerio del Trabajo.

El acta deberá:

- ser generada mediante la plataforma correspondiente;
- contener la información requerida;
- estar suscrita por las partes;
- cargarse en formato PDF;
- registrarse dentro del plazo máximo de 30 días desde la terminación de la relación laboral.

### Artículo 20 – Pago por consignación

Cuando el trabajador no acuda a cobrar la liquidación o se niegue a recibirla, el empleador deberá proceder con la consignación de los valores correspondientes conforme al procedimiento establecido.

Para la revisión del acta de finiquito pueden considerarse documentos como:

- roles de pago;
- horas extras;
- descuentos;
- contratos;
- comprobantes de pago de décima tercera remuneración;
- comprobantes de pago de décima cuarta remuneración;
- utilidades;
- otros documentos relacionados con obligaciones patronales.

### Artículo 21 – Sanciones

El incumplimiento del registro del acta de finiquito puede generar sanciones conforme a lo establecido en el Acuerdo Ministerial.

---

## 3.7. Disposiciones generales relevantes para los cálculos

### Disposición General Cuarta

La decimotercera y decimocuarta remuneración, sea recibida anual o mensualmente, no se considera parte de la remuneración para efectos de:

- aportes al IESS;
- fondo de reserva;
- jubilación;
- indemnizaciones;
- vacaciones;
- impuesto a la renta del trabajador.

### Disposición General Quinta

Para el pago mensual de la decimotercera remuneración se deberá aplicar el artículo 111 en concordancia con el artículo 95 del Código del Trabajo.

Para los cálculos de décima tercera y décima cuarta remuneración se establece:

- período anual de **360 días**;
- mes laboral de **30 días**;
- jornada mensual equivalente a **240 horas**.

Los rubros deberán identificarse separadamente en los roles de pago.

### Disposición General Sexta

Para trabajadores y extrabajadores bajo modalidad de jornada parcial permanente, el cálculo de décima tercera y décima cuarta remuneración se realizará proporcionalmente al tiempo laborado.

---

## 3.8. Relación con el Acuerdo MDT-2019-199

El Acuerdo Ministerial MDT-2023-140 reemplaza normativamente al antiguo Acuerdo MDT-2019-199.

La Disposición Derogatoria Cuarta del MDT-2023-140 deroga expresamente:

- el Acuerdo Ministerial MDT-2019-199 de 25 de julio de 2019;
- su Fe de Erratas publicada posteriormente.

Por esta razón, el MDT-2019-199 no será utilizado como fuente normativa vigente dentro del sistema.

---

## Uso dentro del sistema

El Acuerdo MDT-2023-140 será utilizado para:

- definir los períodos de cálculo de décimos;
- establecer las reglas de acumulación;
- validar las fechas de pago;
- documentar las reglas de registro;
- complementar las reglas del Código del Trabajo;
- determinar reglas relacionadas con actas de finiquito;
- apoyar las explicaciones de liquidaciones;
- definir la proporcionalidad en jornadas parciales;
- proporcionar fragmentos normativos al sistema RAG.

---

# Estrategia de fragmentación para RAG

## 1. Código del Trabajo

### Unidad de fragmentación

La unidad principal será:

**Un artículo = un fragmento.**

Formato:

`codigo_trabajo_art_<numero>`

### Fragmentos inicialmente identificados

#### Salario y remuneración

- `codigo_trabajo_art_81`
- `codigo_trabajo_art_95`
- `codigo_trabajo_art_117`
- `codigo_trabajo_art_118`
- `codigo_trabajo_art_119`

#### Décima tercera remuneración

- `codigo_trabajo_art_111`
- `codigo_trabajo_art_112`

#### Décima cuarta remuneración

- `codigo_trabajo_art_113`
- `codigo_trabajo_art_114`

#### Jornada laboral

- `codigo_trabajo_art_47`

#### Horas suplementarias y extraordinarias

- `codigo_trabajo_art_55`

#### Vacaciones

- `codigo_trabajo_art_69`
- `codigo_trabajo_art_70`
- `codigo_trabajo_art_71`
- `codigo_trabajo_art_72`
- `codigo_trabajo_art_73`
- `codigo_trabajo_art_74`
- `codigo_trabajo_art_75`
- `codigo_trabajo_art_76`

#### Terminación y liquidación

- `codigo_trabajo_art_169`
- `codigo_trabajo_art_184`
- `codigo_trabajo_art_185`
- `codigo_trabajo_art_188`
- `codigo_trabajo_art_191`
- `codigo_trabajo_art_192`

### Metadatos previstos

Cada fragmento deberá incluir:

- `documento`
- `tipo_norma`
- `numero_articulo`
- `titulo_articulo`
- `institucion`
- `fecha_publicacion`
- `fecha_ultima_reforma`
- `url`
- `fecha_consulta`
- `vigencia`

---

## 2. Acuerdo Ministerial MDT-2025-195

### Fragmentación prevista

El documento puede fragmentarse en:

- antecedentes normativos;
- artículo único;
- disposición general;
- disposición final.

Fragmento principal:

`mdt_2025_195_articulo_unico`

### Metadatos previstos

- `documento`
- `numero_acuerdo`
- `institucion`
- `anio_aplicacion`
- `valor_sbu`
- `fecha_inicio`
- `fecha_publicacion`
- `url`
- `fecha_consulta`
- `vigencia`

---

## 3. Acuerdo Ministerial MDT-2023-140

### Fragmentación prevista

El documento será fragmentado principalmente por artículo y disposición.

Fragmentos inicialmente identificados:

### Décima tercera y décima cuarta remuneración

- `mdt_2023_140_art_8`
- `mdt_2023_140_art_9`
- `mdt_2023_140_art_10`
- `mdt_2023_140_art_11`
- `mdt_2023_140_art_12`

### Actas de finiquito

- `mdt_2023_140_art_19`
- `mdt_2023_140_art_20`
- `mdt_2023_140_art_21`

### Disposiciones generales relevantes

- `mdt_2023_140_disposicion_general_4`
- `mdt_2023_140_disposicion_general_5`
- `mdt_2023_140_disposicion_general_6`

### Disposición derogatoria relevante

- `mdt_2023_140_disposicion_derogatoria_4`

### Metadatos previstos

- `documento`
- `numero_acuerdo`
- `numero_articulo`
- `seccion`
- `institucion`
- `fecha_publicacion`
- `vigencia`
- `url`
- `fecha_consulta`

---

# Control de vigencia

| Documento | Estado registrado | Acción |
|---|---|---|
| Código del Trabajo | Vigente. Última reforma indicada: 18-05-2026 | Utilizable |
| Acuerdo MDT-2025-195 | Aplicable al SBU 2026 | Utilizable |
| Acuerdo MDT-2023-140 | Norma aplicable a obligaciones del empleador, décimos, actas de finiquito e inspecciones | Utilizable |
| Acuerdo MDT-2019-199 | Derogado expresamente por MDT-2023-140 | No utilizar como fuente normativa vigente |

Cuando no exista evidencia suficiente para confirmar el estado de una norma, se utilizará expresamente:

**VIGENCIA PENDIENTE DE COMPROBACIÓN**

No se asumirá como vigente ningún documento cuando su estado normativo no pueda ser determinado.

---

# Cobertura actual del alcance

| Cálculo | Fuente principal | Artículos / norma | Estado |
|---|---|---|---|
| Décima tercera remuneración | Código del Trabajo + MDT-2023-140 | Arts. 95, 111, 112 + Arts. 8 al 12 del MDT-2023-140 | Cubierto |
| Décima cuarta remuneración | Código del Trabajo + MDT-2023-140 + MDT-2025-195 | Arts. 113, 114 + Arts. 8 al 12 del MDT-2023-140 + SBU 2026 | Cubierto |
| Salario Básico Unificado | MDT-2025-195 | Artículo Único | Cubierto |
| Jornada laboral | Código del Trabajo | Art. 47 | Cubierto |
| Horas suplementarias y extraordinarias | Código del Trabajo | Art. 55 | Cubierto |
| Vacaciones | Código del Trabajo | Arts. 69 al 76 | Cubierto |
| Desahucio | Código del Trabajo | Arts. 184 y 185 | Cubierto |
| Despido intempestivo | Código del Trabajo | Art. 188 | Cubierto |
| Liquidación laboral | Código del Trabajo + MDT-2023-140 | Arts. 169, 184, 185, 188, 191 y Arts. 19 al 21 del MDT-2023-140 | Cobertura normativa principal identificada |
| Acta de finiquito | MDT-2023-140 | Arts. 19 al 21 | Cubierto |

---

# Archivos disponibles en `data/raw/`

La carpeta deberá contener:

```text
data/raw/
├── acuerdo_sbu_2026_mdt-2025-195.pdf
├── codigo_trabajo_ecuador_2026.pdf
└── mdt-2023-140_obligaciones_empleador.pdf