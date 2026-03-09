FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install build dependencies for native extensions
RUN apt-get update && apt-get install -y \
    gcc g++ python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (cached layer)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY project5_receptionist.py ./
COPY call_logger.py ./

RUN chown -R appuser:appuser /app
USER appuser

# Pre-download VAD model during build (not at runtime)
RUN python project5_receptionist.py download-files

# Production start command
CMD ["python", "project5_receptionist.py", "start"]
