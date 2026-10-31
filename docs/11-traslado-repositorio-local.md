# Traslado al repositorio local

Se incorporó el avance desde la copia sin borrar archivos del original.

Respaldo y manifiesto de archivos: `D:\IngenieriaSoftware\UniAndes\Titulación\Proyecto titulación\respaldo-antes-semana3-20261030-192518`.

Se conservaron `.git`, `.venv` y las claves existentes del `.env`; solo se sincronizaron variables públicas. Dependencias, modelos, índice y PDF locales están ignorados por Git. No se hicieron commits ni push.

El manifiesto agrupa código/configuración, documentación/evaluación y datos locales para incorporar cambios por partes. Las comprobaciones posteriores se informan en la conversación.

## Comprobaciones del traslado

- Suite completa ejecutada en este repositorio: **235 pruebas aprobadas en 8,12 s**.
- Índice local abierto: **699 artículos**. Modelo de embeddings cargado sin
  conexión y recuperación del artículo 111 comprobada desde esta carpeta.
- Proveedores leídos sin mostrar claves: Groq `openai/gpt-oss-120b` como principal
  y Gemini `gemini-3.6-flash` como respaldo. No se consumió API.
- `.env`, dependencias, caché, índice y PDFs locales siguen ignorados por Git.
- Se añadió `scripts/iniciar-local.ps1` y se verificó su sintaxis. El comando de
  inicio está al principio del README; usa el Python 3.14 instalado en este equipo.
- La primera ejecución de pruebas se bloqueó dentro del aislamiento y se
  interrumpió; la ejecución completa indicada arriba terminó fuera de él.

Las mediciones generativas anteriores conservan su alcance y fecha; no se
presentan como una nueva evaluación con proveedores. No se modificó `.git`,
no se borraron archivos previos y no se creó ningún commit.
