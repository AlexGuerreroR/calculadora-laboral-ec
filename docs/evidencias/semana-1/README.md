# Evidencias de la semana 1

Proyecto: Calculadora Inteligente de Beneficios y Liquidaciones Laborales, UNIANDES, Grupo 7.

Integrantes: Alexander Guerrero, Bladimir y Dorian Zambrano.

## Documentos y entregables

| Evidencia | Ubicación |
|---|---|
| Propuesta del proyecto | [01-propuesta.md](../../01-propuesta.md) |
| Historias de usuario y requisitos | [02-requisitos.md](../../02-requisitos.md) |
| Componentes y flujo de la solución | [03-arquitectura.md](../../03-arquitectura.md) |
| Inventario de fuentes normativas | [04-fuentes.md](../../04-fuentes.md) |
| Parámetros laborales configurables | [parametros.yaml](../../../config/parametros.yaml) |
| Levantamiento de información | [levantamiento.md](levantamiento.md) |
| Diez casos C01–C10 con desarrollo y resultados | [B4_Resolución de casos.xlsx](B4_Resoluci%C3%B3n%20de%20casos.xlsx) |
| Instrucciones de ejecución | [README principal](../../../README.md) |
| Registro metodológico y uso de IA | [09-decisiones.md](../../09-decisiones.md) |

## Aportes y trazabilidad

| Integrante | Aporte | Pull requests |
|---|---|---|
| Alexander Guerrero | Estructura inicial, configuración de parámetros, endpoint de salud y publicación de los diez casos de referencia. | [#34](https://github.com/AlexGuerreroR/calculadora-laboral-ec/pull/34), [#36](https://github.com/AlexGuerreroR/calculadora-laboral-ec/pull/36), [#39](https://github.com/AlexGuerreroR/calculadora-laboral-ec/pull/39), [#41](https://github.com/AlexGuerreroR/calculadora-laboral-ec/pull/41) |
| Bladimir | Levantamiento de información, propuesta, arquitectura y aportación de los casos reales utilizados como referencia. | [#37](https://github.com/AlexGuerreroR/calculadora-laboral-ec/pull/37) |
| Dorian Zambrano | Requisitos, inventario de fuentes y revisión de entregables del equipo. La documentación D4 se entrega mediante su propio PR. | [#38](https://github.com/AlexGuerreroR/calculadora-laboral-ec/pull/38), [#40](https://github.com/AlexGuerreroR/calculadora-laboral-ec/pull/40) |

Cada PR contiene una pestaña **Commits** que permite consultar los cambios y su autoría. El historial general está disponible en [commits de main](https://github.com/AlexGuerreroR/calculadora-laboral-ec/commits/main/).

## Casos de referencia

El archivo Excel reúne diez casos sobre décimos, horas adicionales, vacaciones y liquidaciones, con datos, fórmulas, desarrollo, resultados y fuentes. Según lo informado por Alexander, los cálculos fueron revisados individualmente por un contador, quien confirmó verbalmente los resultados. No se adjunta certificación firmada.

## Alcance de la evidencia técnica

El código disponible permite iniciar FastAPI y consultar `/health`, con respuesta esperada `{"status":"ok"}`. Los diez casos son referencias documentales para la implementación posterior; no constituyen resultados de una calculadora ya integrada ni de una suite automatizada de pruebas.

## Cierre de D4

La [tarjeta D4 #35](https://github.com/AlexGuerreroR/calculadora-laboral-ec/issues/35) debe enlazar el PR que incorpore estos documentos. Alexander deberá comprobar las instrucciones de ejecución y los enlaces antes de aprobar el cierre. La revisión final de D4 no se declara completada en este documento.
