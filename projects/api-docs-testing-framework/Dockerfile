# API Docs & Testing Framework - Dockerfile
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./

COPY src/ ./src/

RUN pip install --upgrade pip && pip install -e "."

FROM python:3.11-slim as production

WORKDIR /app

COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /app/src ./src
COPY --from=base /app/pyproject.toml ./

EXPOSE 8000

CMD ["uvicorn", "api_testing.main:app", "--host", "0.0.0.0", "--port", "8000"]
