FROM python:3.12-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY databank/ databank/
COPY web/ web/

# Install dependencies
RUN uv sync --no-dev --frozen

# Expose the API port
EXPOSE 8000

# Run the API server
CMD ["uv", "run", "uvicorn", "toponymia.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
