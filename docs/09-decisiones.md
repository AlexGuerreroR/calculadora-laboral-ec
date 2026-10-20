# Decisiones y registro de asistencia de IA

Proyecto: Calculadora Inteligente de Beneficios y Liquidaciones Laborales. Grupo 7, UNIANDES.

Fecha de preparación de este registro: 19 de octubre de 2026.

## Decisiones técnicas

1. Los cálculos laborales se implementarán mediante funciones deterministas, con parámetros separados del código y del prompt.
2. El modelo de lenguaje se utilizará para explicaciones y recuperación de fundamentos normativos. No será el motor aritmético de la aplicación.
3. Las fuentes y su vigencia se documentan en [04-fuentes.md](04-fuentes.md). Los parámetros se centralizan en [config/parametros.yaml](../config/parametros.yaml).
4. Los diez casos de referencia se conservan con sus datos, fórmulas, desarrollo y resultados en [el archivo Excel](evidencias/semana-1/B4_Resoluci%C3%B3n%20de%20casos.xlsx).
5. Los cambios se presentan mediante pull requests. Las funciones futuras se distinguen del código ya implementado.
6. No se publicarán claves de acceso ni datos personales que permitan identificar a las personas de los casos reales.

## Asistencia de IA durante la preparación

Este registro distingue la asistencia al desarrollo del comportamiento previsto de la aplicación. La utilización de un asistente no convierte una respuesta generada en una fuente normativa ni acredita por sí misma el cumplimiento de la resolución manual requerida.

### Alexander Guerrero

- Asistente utilizado: ChatGPT/Codex de OpenAI, según la conversación de trabajo disponible.
- Usos: orientación sobre Git y GitHub, apoyo en configuración y documentación, preparación de cálculos y fórmulas de los casos de referencia, y elaboración de los documentos de cierre D4.
- Revisión humana informada: Alexander indicó que un contador revisó individualmente los diez casos y confirmó verbalmente los resultados. No se dispone de acta ni de certificación firmada.
- Ajustes documentados: aclaración de periodos de décimos, modalidad acumulada, sueldo del mes de salida ya pagado, vacaciones previamente gozadas y redondeo de cada rubro final a dos decimales. Se incorporaron fuentes y observaciones de aplicación a los parámetros.
- Límite de la evidencia: la revisión verbal de resultados no acredita por sí misma que cada operación haya sido realizada manualmente. El equipo debe poder explicar el desarrollo de cada caso.

### Bladimir

Se registra su aporte al levantamiento, propuesta, arquitectura y obtención de los casos reales. La herramienta de IA utilizada, sus usos específicos y las correcciones efectuadas no han sido confirmados para este registro. Bladimir debe aportar su declaración antes de marcar como completo el criterio de declaración individual de D4; no se atribuye una herramienta sin su confirmación.

### Dorian Zambrano

Se registra su aporte a requisitos, fuentes y revisiones mediante PR. La herramienta de IA utilizada, sus usos específicos y las correcciones efectuadas no han sido confirmados para este registro. Dorian debe aportar su declaración antes de marcar como completo el criterio de declaración individual de D4.

## Estado de implementación y revisión

El backend actual contiene el endpoint `/health`. La integración del motor de cálculo, la interfaz, el modelo de lenguaje y la recuperación documental permanecen pendientes.

Los presentes documentos fueron preparados con asistencia de IA a partir de los archivos del repositorio y de la información aportada por Alexander. Corresponde al responsable Dorian revisar su contenido y a Alexander verificar las instrucciones y enlaces antes de aprobar el PR de D4. Esta verificación final no se registra como realizada anticipadamente.
