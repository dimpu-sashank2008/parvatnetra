# ==============================================================================
# PARVAT NETRA -- Multi-Stage Production Container Specification (Phase 5)
# Smart India Hackathon (SIH) | Problem Statement ID: 26001
# Ministry of Development of North Eastern Region (MDoNER)
# ==============================================================================

# ------------------------------------------------------------------------------
# STAGE 1: Builder (Compile wheels & spatial C-extension dependencies)
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install compilation toolchains and GIS/Spatial header development packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libgeos-dev \
    libproj-dev \
    libgdal-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python wheels into local prefix
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ------------------------------------------------------------------------------
# STAGE 2: Production Runner (Lean runtime with spatial shared libraries)
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PATH=/root/.local/bin:$PATH

WORKDIR /app

# Install runtime spatial libraries (GEOS, Proj, GDAL, PostgreSQL client) & curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgeos-c1v5 \
    libproj25 \
    gdal-bin \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application codebase
COPY . /app

# Ensure field evidence upload storage is pre-created
RUN mkdir -p /app/static/uploads/field_reports

# Expose national sentinel gateway port
EXPOSE 8080

# Production Health Check querying the /api/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Launch with production multi-threaded Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
