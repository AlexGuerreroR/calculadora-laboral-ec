# Contraste documental y ejecución local

Fecha de consulta: 30/10/2026, America/Guayaquil.

- Código actualizado: [registro de Defensoría Pública](https://biblioteca.defensoria.gob.ec/handle/37000/3819).
- Portada PDF leída: reforma RO 286-S del 18/05/2026, normativa declarada vigente.
- SHA-256: `6949f4b75620a46115282f414033e8e623a19acf22cd2cebd666913cae67ed5b`.
- 216 páginas, 699 fragmentos; 618 marcados vigentes y 81 derogados según edición.
- Comparación de diez artículos utilizados: todos idénticos a la versión anterior.
- Evidencia detallada: `eval/contraste_fuentes_20261030.json`.
- Manifiesto: `config/corpus.json`; índice activo `data/chroma-2026/`, anterior conservado.

Fuentes complementarias:

- [MDT-2025-195](https://www.trabajo.gob.ec/wp-content/uploads/downloads/2026/01/ACUERDO-MINISTERIAL-MDT-2025-195.pdf): SBU de USD 482 desde 01/01/2026.
- [MDT-2023-140](https://www.trabajo.gob.ec/wp-content/uploads/downloads/2024/01/MDT-2023-140-AM-Obligaciones-empleador-y-procedimientos-de-inspeccion-14-11-23-signed.pdf): artículos 9/10, modalidades y períodos; Disposición General Quinta, base 360/30/240.

No se consumió API de IA para descargar, comparar o indexar. Las mediciones de
generación previas se conservan con su versión original; no se afirman nuevas
generaciones posteriores a la actualización. La igualdad textual de los diez
artículos está documentada. No se certifican reformas posteriores al corte ni
la exactitud de hechos declarados por usuarios.

La app está disponible localmente en `http://127.0.0.1:8011/`. En la interfaz
se observó cálculo de décimo tercero de USD 600, fuente Art. 111 con edición
2026 y URL de Defensoría, cancelación sin PDF, abstención por reglamento privado
ausente y rechazo de inyección directa. Son acciones reales sobre la app local,
sin nuevas llamadas al modelo. La evidencia de generación con cita se conserva
en los JSON del cierre; no se reenvió al proveedor desde el navegador.

También se confirmó y descargó un PDF real desde la interfaz. Copia local:
`output/pdf/resumen-decimo-tercero-2026.pdf`, una página, USD 600 y referencia
2026 visibles; página renderizada y revisada sin desbordes. Captura de la app:
`interfaz-lista-20261030.png` y vista de pantalla `interfaz-vista-final-20261030.png`.
Se versionó la URL del JavaScript para evitar que el navegador conservara el
aviso antiguo sobre el corpus. La app quedó abierta en localhost:8011.
