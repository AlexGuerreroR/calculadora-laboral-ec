# Evidencias de la semana 3

Las evaluaciones se conservan en `eval/`, sin duplicarlas en esta carpeta.
El avance se desarrolló en la copia y después se trasladó al repositorio local.
El traslado se describe en [su registro](../../11-traslado-repositorio-local.md).

## Cierre de la evaluación

| Archivo en `eval/` | Contenido |
| --- | --- |
| `preguntas.csv`, `preguntas.json` | Veinte preguntas de referencia y sus respuestas esperadas. |
| `casos_calculo.csv` | Entradas y resultados esperados de diez casos del ejercicio. |
| `cierre_real_20261030.json` | Trece generaciones normativas nuevas y resultados de las guardas, con decisiones de herramientas reutilizadas. |
| `cierre_publicado_20261030.json` | Publicación de esas mismas generaciones con el ajuste posterior de presentación, sin nuevas llamadas al modelo. |
| `revision_cierre_20261030.json` | Revisión asistida por pregunta y motivo de cada resultado. |
| `metricas_cierre_20261030.json` | Resumen del cierre y sus límites. |
| `recuperacion_corregida_20261030.json` | Recuperación de todos los artículos esperados: 13/13. No mide generación. |
| `resultados_calculos_20261030.json` | Respuestas HTTP locales de diez cálculos: 10/10 dentro de USD 0,01, sin API. |
| `contraste_fuentes_20261030.json` | Comparación de diez artículos entre la edición anterior y la de mayo de 2026. |
| `gemini_modelos_probados_20261030.json` | Comprobación de Gemini 3.6 Flash tras un fallo simulado del proveedor principal. |

El resultado guardado es 11/13 respuestas correctas con cita y 4/4 abstenciones
o derivaciones esperadas. P06 y P07 siguen fallando. El cierre no es una nueva
ejecución completa del planificador y no sustituye una revisión jurídica.
Método y límites: [evaluación](../../07-evaluacion.md).

## Interfaz y fuentes

Se conservan las capturas `interfaz-acciones-claras.png`,
`interfaz-lista-20261030.png`, `interfaz-rechazo-20261030.png` e
`interfaz-vista-final-20261030.png`.
El recorrido y su alcance están descritos en [cierre-fuentes.md](cierre-fuentes.md):
cálculo, fuente con edición 2026, cancelación y descarga de PDF, abstención e
inyección. Las generaciones con IA se respaldan con los JSON; las capturas no
demuestran una evaluación nueva con el proveedor.

Las pruebas y capturas anteriores de vista previa y cancelación documentan ese
recorrido. Actualmente, el botón «Descargar PDF» prepara y confirma en un solo
clic. La vista previa con confirmación separada permanece cuando el resumen se
solicita al agente. El cambio está registrado en el grupo U de la bitácora;
no se presentan las capturas anteriores como una nueva comprobación de ese botón.

El manifiesto del corpus está en `config/corpus.json`. La comparación documental
se limita a los diez artículos registrados y al corte del 18/05/2026.

## Historial de mejoras

| Archivo en `eval/` | Para qué se conserva |
| --- | --- |
| `resultados_agente_real_20261030.json` | Primera corrida real: respuestas, fuentes, herramientas, tiempos y huellas de versiones. |
| `revision_agente_20261030.json`, `metricas_agente_20261030.json` | Revisión y métricas de esa corrida, con los fallos iniciales. |
| `resultados_agente_final_20261030.json` | Corrida anterior cuyas decisiones utiliza `cerrar_evaluacion.py`. |
| `resultados_recuperacion.json` | Recuperación histórica; no es una evaluación de respuestas. |

La evolución del código está registrada en [la bitácora](../../10-bitacora-copia.md).

## Diagnósticos auxiliares

`diagnostico_P04_20261030.json`, `resultados_agente_corregido_20261030.json`,
`modelos_respaldo_20261030.json` y los archivos `respaldo_real*` conservan
diagnósticos e intentos anteriores. No se usan como métricas del cierre.
No deben borrarse sin revisar sus referencias: algunos scripts dependen de ellos.

No publicar `.env`, claves, dependencias, cachés ni registros generales del
proveedor. Los datos de evaluación son los ejemplos del conjunto de referencia.
