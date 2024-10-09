#!/bin/bash

echo "Starting Configurator Assistant server"
PYTHONFAULTHANDLER=true
PYTHONPATH=/app
mkdir /tmp/smart_configurator
cd /app
echo "Working directory is $PWD"
uvicorn copilot.api_server:app --host 0.0.0.0 --port 18000




