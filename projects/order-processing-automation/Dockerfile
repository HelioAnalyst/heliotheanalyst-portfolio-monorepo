# Order Processing Automation - Dockerfile
# Production-ready container for FastAPI API and Celery workers
#
# Build:
#   docker build -t order-processing .
#
# Run API:
#   docker run -p 8001:8000 order-processing
#
# Run Celery Worker:
#   docker run order-processing celery -A order_processing.tasks worker --loglevel=info

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
# Copy application code
COPY src/ ./src/
RUN pip install --upgrade pip && \
    pip install -e "."



# Production stage
FROM python:3.11-slim as production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /app/src ./src
COPY --from=base /app/pyproject.toml ./

EXPOSE 8000

# Default command runs the API
# Override with: docker run <image> celery -A order_processing.tasks worker --loglevel=info
CMD ["uvicorn", "order_processing.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
