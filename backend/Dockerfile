FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first, so this layer is reused when only the code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY ml ./ml

# Same UID as the server's ubuntu user, so files in the data volume stay editable
RUN useradd --uid 1000 --no-create-home appuser
USER appuser

EXPOSE 8000

# One worker only: the refresh jobs and in-memory caches live in this process
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]