# STAGE 1: Builder
FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# STAGE 2: Final Runtime
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . .

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

# Expose the port
EXPOSE 8000

# Command to run the application
# We point to audit_ai.main:app because the folder structure was flattened
ENV PYTHONPATH="/app/src:${PYTHONPATH}"
CMD ["uvicorn", "audit_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]