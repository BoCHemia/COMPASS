# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11.0
FROM python:${PYTHON_VERSION}-slim as base

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
WORKDIR /app

# Install dependencies as root
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=/requirements.txt \
    python -m pip install -r /requirements.txt

# Copy source and give ownership to appuser
COPY --chown=appuser:appuser . /app

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
