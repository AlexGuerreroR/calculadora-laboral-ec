## ADR · Diseño del agente de alcance controlado

*Taller de la Clase 3 · 28 de octubre de 2026 · Grupo 7 · Beneficios y liquidaciones laborales*
*Integrantes: Alexander Guerrero, Bladimir Velasco, Dorian Zambrano*

### Contexto
El producto necesita, además de responder con nuestros documentos (RAG), ejecutar acciones. Un agente da vueltas pidiendo funciones; debemos acotar qué puede pedir, cuántas vueltas puede dar y qué acciones requieren confirmación humana.

### Decisión
- **Meta:** Explicar los resultados de la calculadora laboral con su fundamento normativo, sin realizar cálculos ni emitir dictámenes jurídicos.
- **Se considera terminada cuando:** Cuando el usuario recibe la explicación con su fuente y artículo, o se informa que no hay respaldo suficiente o requiere asesoría especializada.
- **Usuario:** Trabajadores y empleadores en Ecuador que desean comprender sus cálculos laborales.

| Herramienta | Qué hace | Nivel | Por qué |
|---|---|---|---|
| `calcular_decimos` | Calcula décimos mediante codigo en Python. | Libre | El código calcula; el modelo no. |
| `calcular_vacaciones` | Calcula días y valor mediante Python. | Libre | No modifica registros ni envía información. |
| `estimar_liquidacion` | Obtiene rubros y total mediante Python. | Libre | Solo genera una estimación. |
| `explicar_resultado` | Explica el resultado con respaldo normativo. | Libre | No calcula ni modifica valores. |
| `generar_resumen` | Genera el PDF cuando el usuario lo solicita. | Con confirmación | Requiere la solicitud del usuario. |
| `realizar_pago` | Ejecuta pagos de liquidaciones. | Fuera de la lista | No pertenece al alcance del proyecto. |

- **MAX_ITER = 6.** Al llegar al tope el agente responde: «No pude completar la consulta. Presento lo obtenido e indico qué falta para continuar.»
- **Parámetros en config/:** `salario_basico_unificado.valor` (Porque Cambia según el año.)
- **Herramienta especificada en el taller:** `calcular_decimos` (esquema Pydantic, prueba pytest y config generados).

### Pruebas en el simulador del bucle
- ✔ A · Camino feliz (3 vueltas)
- ✔ B · Fuera de alcance (2 vueltas)
- ✔ C · El tope (6 vueltas)
- ✔ D · Inyección en un documento (3 vueltas; control: La confirmación humana permitió rechazar el envío. Además, validaríamos los argumentos y trataríamos el contenido recuperado como datos, no como instrucciones.)

### Seguridad
- Entradas no confiables: Los documentos que indexa su RAG; Lo que escribe el usuario; Lo que devuelve cada herramienta (incluida la búsqueda).
- Ningún texto leído otorga permisos: los permisos son PERMITIDAS, MAX_ITER y REQUIEREN_OK, en el código.
- La confirmación muestra los argumentos reales (qué se hará y a quién).

### Consecuencias
- Las herramientas «fuera de la lista» no se implementan como herramientas del agente.
- Cada herramienta tiene esquema Pydantic, implementación determinista y prueba con pytest.
- Pendiente para la Entrega 3: implementar las funciones, el botón de confirmación en la interfaz y la evidencia de inyección en docs/evidencias/semana-3/.
