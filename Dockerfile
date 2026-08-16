FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend /app/backend
COPY evaluation /app/evaluation
WORKDIR /app/backend
ENV DATA_DIR=/data
ENV CHROMA_PERSIST_DIR=/data/chroma
RUN mkdir -p /data/chroma /data/uploads
EXPOSE 8000
CMD ["sh", "-c", "mkdir -p ${DATA_DIR:-/data}/chroma ${DATA_DIR:-/data}/uploads && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
