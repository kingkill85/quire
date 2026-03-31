# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python base with common deps
FROM python:3.12-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/ ./
RUN pip install --no-cache-dir .
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Stage 3: Standard image (with SeleniumBase bypass)
FROM base AS standard

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir ".[bypass]"

ENV QUIRE_CF_BYPASS=internal
ENV DISPLAY=:99

COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8085
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8085/api/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "quire.main:app", "--host", "0.0.0.0", "--port", "8085"]

# Stage 4: Lite image (external bypass only)
FROM base AS lite

ENV QUIRE_CF_BYPASS=external

EXPOSE 8085
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8085/api/health || exit 1

CMD ["uvicorn", "quire.main:app", "--host", "0.0.0.0", "--port", "8085"]
