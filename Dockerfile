# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12.0
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-privileged user with a real home
ARG UID=10001
RUN useradd \
    --create-home \
    --home-dir /home/appuser \
    --shell /bin/bash \
    --uid "${UID}" \
    appuser

ENV HOME=/home/appuser
ENV XDG_CACHE_HOME=/home/appuser/.cache
ENV STREAMLIT_CONFIG_DIR=/home/appuser/.streamlit

WORKDIR /app

# Install system dependencies as root (no special mounts needed here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    libxrender1 \
    libxext6 \
    libsm6 \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (with pip cache + requirements bind-mount)
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=/requirements.txt \
    python -m pip install -r /requirements.txt

# Copy source and give ownership to appuser
COPY --chown=appuser:appuser . /app

# Ensure uploads folder exists and is writable
RUN mkdir -p /app/output && chown -R appuser:appuser /app/output

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]



