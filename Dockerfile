# Stage 1: Dependencies (use base builder)
FROM 000373574646.dkr.ecr.ap-southeast-1.amazonaws.com/oxsci/backend-base-builder:latest AS dependencies

WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Ensure poetry creates in-project venv
RUN poetry config virtualenvs.in-project true

# Optional CodeArtifact reconfiguration via Docker secrets
RUN --mount=type=secret,id=codeartifact_repo \
    --mount=type=secret,id=codeartifact_url \
    --mount=type=secret,id=codeartifact_token \
    if [ -f /run/secrets/codeartifact_repo ] && [ -f /run/secrets/codeartifact_url ] && [ -f /run/secrets/codeartifact_token ]; then \
    CODEARTIFACT_REPO=$(cat /run/secrets/codeartifact_repo) && \
    CODEARTIFACT_URL=$(cat /run/secrets/codeartifact_url) && \
    CODEARTIFACT_TOKEN=$(cat /run/secrets/codeartifact_token) && \
    poetry config repositories.$CODEARTIFACT_REPO $CODEARTIFACT_URL && \
    poetry config http-basic.$CODEARTIFACT_REPO aws $CODEARTIFACT_TOKEN && \
    echo "CodeArtifact repository $CODEARTIFACT_REPO reconfigured with fresh token"; \
    fi

RUN poetry install --only=main --no-root

# Stage 2: Runtime (use base runtime)
FROM 000373574646.dkr.ecr.ap-southeast-1.amazonaws.com/oxsci/backend-base:latest

WORKDIR /app

# Copy project metadata for version extraction
COPY pyproject.toml ./

# Copy virtualenv with dependencies
COPY --from=dependencies /app/.venv /app/.venv

# Common runtime environment variables for agent
ENV SERVICE_PORT=8080 \
    ENV=test \
    CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="1"
EXPOSE ${SERVICE_PORT}

# Copy application source
COPY app /app/app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${SERVICE_PORT:-8080}/health || exit 1

# Default command: uvicorn at fixed port 8080
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.core.main:app", "--host", "0.0.0.0", "--port", "8080"]
