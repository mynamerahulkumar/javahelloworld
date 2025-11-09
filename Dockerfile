# syntax=docker/dockerfile:1.6

# ============================
# Frontend build stage
# ============================
FROM node:20-bookworm-slim AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --include=dev

COPY frontend/ ./
RUN npm run build && npm prune --omit=dev

# ============================
# Runtime stage
# ============================
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH" \
    NODE_ENV=production

WORKDIR /app

# System dependencies and Node.js
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg build-essential libffi-dev libssl-dev && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python virtual environment
RUN python -m venv /opt/venv

# Install backend dependencies
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --upgrade pip && pip install -r backend/requirements.txt

# Copy backend application
COPY backend/ backend/

# Copy frontend build artifacts
COPY frontend/next.config.* frontend/
COPY frontend/public frontend/public
COPY frontend/package.json frontend/package-lock.json frontend/
COPY --from=frontend-builder /app/frontend/.next frontend/.next
COPY --from=frontend-builder /app/frontend/node_modules frontend/node_modules

# Runtime start script
COPY docker/start.sh docker/start.sh
RUN chmod +x docker/start.sh

EXPOSE 3000 8501

CMD ["docker/start.sh"]

