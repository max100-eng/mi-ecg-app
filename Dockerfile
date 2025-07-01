# syntax=docker/dockerfile:1

# --- Base image for Node.js (for JS/React app build) ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app
# Only copy the JS file (App.js) and any package.json if present
COPY --link App.js ./
# If you had a package.json, you would run npm install and build here
# For a single JS file, we skip build steps

# --- Base image for Python (for Streamlit/ECG backend) ---
FROM python:3.11-slim AS python-builder
WORKDIR /app
# System dependencies for scientific stack
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*
# Copy all Python files and requirements (if any)
COPY --link *.py ./
COPY --link ecg_analysis.py ./
COPY --link __init__.py ./
# Create virtual environment and install dependencies
RUN python -m venv /app/.venv \
    && . /app/.venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache-dir streamlit neurokit2 matplotlib pandas numpy

# --- Final image ---
FROM python:3.11-slim AS final
WORKDIR /app
# Copy Python app and venv from builder
COPY --from=python-builder /app /app
COPY --from=python-builder /app/.venv /app/.venv
# Copy JS frontend (App.js) from frontend-builder
COPY --from=frontend-builder /app/App.js ./App.js
# Create non-root user
RUN useradd -m ecguser
USER ecguser
ENV PATH="/app/.venv/bin:$PATH"
# Expose Streamlit default port
EXPOSE 8501
# Default command: run Streamlit app (change as needed)
CMD ["streamlit", "run", "ecg_app.py"]
