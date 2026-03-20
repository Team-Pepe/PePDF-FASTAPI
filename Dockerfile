FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install uv in the builder stage.
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/

# Copy dependency descriptors first to maximize Docker layer cache.
COPY pyproject.toml uv.lock ./

# Create the virtual environment with locked production dependencies.
RUN uv sync --frozen --no-dev --no-install-project

# Copy only the application source code.
COPY app ./app

# Install the local project into the same environment.
RUN uv sync --frozen --no-dev


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy the prepared environment and source code from builder.
COPY --from=builder /app /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]