FROM python:3.13-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies in a cache layer. This speeds up build time
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
COPY . /app

# Sync the project and install it, now that we have access to the source code
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-editable

FROM python:3.13-alpine

# Create a non-root user and group with specific IDs
RUN addgroup -S -g 1000 app && adduser -S -u 1000 -G app app

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Switch to the non-root user
USER app

# Expose the correct port
EXPOSE 22112

# Run the application
CMD ["/app/.venv/bin/study-tracker-api"]
