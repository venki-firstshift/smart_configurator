#!/bin/bash

echo "Starting Configurator Assistant server"
PYTHONFAULTHANDLER=true
uvicorn copilot:api_server --port 18000




