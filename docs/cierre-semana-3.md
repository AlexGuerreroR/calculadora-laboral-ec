# Cierre de la revisión del 30 de octubre

Esta lista corresponde a la **semana 3** de la guía UNIANDES, revisión del viernes
30/10/2026. No declara realizado el despliegue, la evaluación comparada de semana
4 ni la sustentación final del 7 de noviembre. Tampoco sustituye la revisión
jurídica de las fuentes. El avance se desarrolló en la copia y luego se trasladó
al repositorio local. Los cambios todavía no se han publicado en GitHub.

| Requisito de la guía | Evidencia local | Estado |
| --- | --- | --- |
| w3a: ingesta reproducible y metadatos | `scripts/ingest.py`, `config/corpus.json`, corpus activo 2026: 699 artículos | Cerrado documentalmente: edición oficial 18/05/2026, fechas, URL, hash y estado según edición; diez artículos contrastados e idénticos. No certifica reformas posteriores. |
| w3b: justificar fragmentación | `docs/06-rag.md`: por artículo, sin solapamiento y límite de tokens | Documentado. |
| w3c: filtros y búsqueda híbrida | `retriever.py`: vigencia/tema; `agente.py`: consulta original y artículos por tema | Implementado; recuperación corregida 13/13, sin medir generación. |
| w3d: cita obligatoria visible | IDs recuperados validados, metadatos y fragmentos en frontend | Cierre publicado: 11/13 correctas con cita, 84,62 %, método declarado en evaluación. |
| w3e: abstención | Documentos empresariales/IESS ausentes, conflictos y falta de respaldo | Cierre: 4/4 abstenciones/derivaciones esperadas. |
| w3f: herramientas reales, esquemas y límites | Registro cerrado de ocho herramientas, funciones Python, Pydantic, límites de vueltas/llamadas | Implementado y probado. |
| w3g: parámetros en configuración | `config/parametros.yaml`: SBU, períodos, recargos, topes, reglas y límites | Implementado. No significa certificación de actualidad jurídica. |
| w3h: confirmación humana | PDF directo autorizado por el clic en «Descargar PDF»; vista previa con confirmar/cancelar si se solicita al agente. Cookie y token de un uso; revisión explícita de liquidación. | Dos recorridos en la interfaz. La descarga directa no pide un segundo clic de aprobación. Evidencia histórica del PDF en el grupo G y cambio de interfaz en el grupo U de la bitácora. |
| w3i: 20 preguntas, 10 casos, script y reporte | `eval/`, `docs/07-evaluacion.md` | Cerrado con revisión y límites: 20 preguntas, 10/10 cálculos; planificación grabada, 13 generaciones nuevas, publicación posterior sin API. |
| w3j: pruebas con un comando | `pytest -q`: 235 aprobadas | El cierre registró una suite anterior al ajuste de presentación. El traslado al local registra otra ejecución de 235 pruebas en 8,12 s; véase `docs/11-traslado-repositorio-local.md`. No se ejecutaron pruebas nuevas durante esta revisión documental. |
| w3k: evidencias semana 3 | `docs/evidencias/semana-3/README.md`, archivos `eval/cierre_*`, métricas y `cierre-fuentes.md` | Recorrido de interfaz observado: cálculo, fuente 2026, cancelación PDF, abstención e inyección. Generación con IA documentada en JSON, sin reenviarla desde navegador. |

## Demostración en vivo de cinco minutos

1. Mostrar el cálculo C01: doce remuneraciones de 600; total 600. Explicar que
   Python calcula y la IA orienta. Abrir su fuente cuando se pida explicación.
2. Preguntar por la jornada máxima y desplegar la cita y el fragmento recuperado.
3. Preguntar por el reglamento interno de la empresa: mostrar abstención por
   documento no cargado, no una respuesta inventada.
4. Revisar el último cálculo y pulsar «Descargar PDF»: la descarga se autoriza
   con ese clic. Para demostrar la confirmación separada, solicitar el resumen
   al agente con el cálculo adjunto; revisar la vista previa y confirmar o
   cancelar. La IA no confirma por el usuario.
5. Probar inyección directa: mostrar rechazo. Mostrar dónde están parámetros,
   resultados de evaluación y límites. Si falla el proveedor, enseñar el mensaje
   controlado y continuar con cálculos y PDF locales; no fingir respuesta de IA.

Antes de la presentación, iniciar el servidor desde el repositorio local con el intérprete
externo y `PYTHONPATH` descrito en README. El `.venv` copiado no se usa como
intérprete. No reconstruir el índice ni instalar dependencias durante la demo.

## Estado del repositorio

El traslado está registrado en `docs/11-traslado-repositorio-local.md`.
La bitácora `docs/10-bitacora-copia.md` conserva el desarrollo por grupos A–I.
Antes de publicar, revisar las diferencias y seleccionar código, documentación
y evidencias. No incluir `.env`, cachés, dependencias locales ni temporales.
El traslado no creó commits ni hizo push.

Los resultados guardados alcanzan las metas medidas de la semana 3 con el método
de evaluación declarado, y el contraste documental de sus fuentes se cerró
contra la edición oficial de mayo de 2026. No es una certificación jurídica ni
afirma que todas las preguntas obtengan respuesta: P06/P07 siguen absteniéndose.
La evaluación reutilizó decisiones de herramientas y no equivale a una nueva
corrida completa del agente. Publicar los cambios y demostrar el flujo final
siguen siendo pasos separados de estas mediciones.

La declaración de uso de IA de Dorian está pendiente de completar con sus tareas
y validaciones en `docs/09-decisiones.md`.
El corpus activo corresponde a la edición con reforma del 18/05/2026 registrada
en `config/corpus.json`. El contraste de diez artículos no certifica ausencia
de reformas posteriores. La revisión oficial debe distinguir el avance local
del código que ya está publicado en GitHub.
