# STAGE 1: Builder
# We use a slim python image to keep things small from the start
FROM python:3.10-slim as builder

# Prevent python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building python packages
# (gcc and python3-dev are often needed for libraries like numpy/pandas if wheels aren't found)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment to isolate dependencies
RUN python -m venv /opt/venv
# Enable the venv for the upcoming install commands
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# STAGE 2: Final Runtime
FROM python:3.10-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Enable the venv in this stage too
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . .

# Create a non-root user for security (Best Practice)
RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

# Expose the port
EXPOSE 8000

# Command to run the application
ENV PYTHONPATH="/app/src:${PYTHONPATH}"
CMD ["uvicorn", "audit_ai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]