# Imagen de la Calculadora Laboral EC (despliegue en Railway con Docker).
# El índice del RAG se crea al construir la imagen: viene incluido y la app sigue
# respondiendo con citas después de un reinicio (guía, semana 4).
# Las claves NO van aquí: se configuran como variables en la plataforma.
FROM python:3.13-slim

# Usuario sin privilegios para ejecutar la app.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/user/.cache/huggingface \
    EMBEDDING_MODEL=intfloat/multilingual-e5-small \
    CHROMA_PATH=./data/chroma-2026 \
    PORT=8000
WORKDIR $HOME/app

# Dependencias primero (capa en caché). torch solo para CPU: la versión con CUDA pesa varios GB.
COPY --chown=user requirements.txt .
RUN pip install --user torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu \
 && pip install --user -r requirements.txt

COPY --chown=user . .

# Ingesta: descarga el Código del Trabajo, verifica su SHA-256, crea el índice y
# deja el modelo de embeddings dentro de la imagen.
RUN python scripts/ingest.py

EXPOSE 8000
# La plataforma define PORT. --proxy-headers: detrás de su proxy, la IP real del usuario
# (límite por IP) y el esquema https (cookie segura del resumen PDF).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
