#!/bin/bash

# Default values
PORT=8060
USE_TEST_ENV=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --test)
      USE_TEST_ENV=true
      shift
      ;;
    -p)
      PORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--test] [-p PORT]"
      echo "  --test    Use .env.test environment file"
      echo "  -p PORT   Specify port (default: 8000)"
      exit 1
      ;;
  esac
done

# Load test environment if specified
if [ "$USE_TEST_ENV" = true ]; then
  if [ -f ".env.test" ]; then
    echo "Loading test environment from .env.test"
    set -a
    source .env.test
    set +a
  else
    echo "Warning: .env.test file not found"
  fi
fi

# Start the service
echo "Starting service on port $PORT..."
poetry run uvicorn app.core.main:app --port "$PORT" --host 0.0.0.0 --reload
