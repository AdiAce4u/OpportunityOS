FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PORT=8000

WORKDIR /app

# Install system dependencies, curl for healthchecks, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browser and OS dependencies for headless Chromium
RUN playwright install --with-deps chromium

# Create directories for dynamic uploads and screenshots
RUN mkdir -p /app/uploads /app/screenshots

# Copy application source code
COPY app ./app

# Expose default port
EXPOSE 8000

# Container healthcheck supporting dynamic $PORT
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD sh -c "curl -f http://localhost:${PORT:-8000}/docs || exit 1"

# Launch FastAPI with Uvicorn supporting dynamic cloud $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
