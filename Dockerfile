# Stage 1: Build the UI application
FROM node:22.9.0-alpine AS build
WORKDIR /ui
COPY ui/package*.json /ui/
RUN npm ci --prefer-offline --no-audit --progress=false
COPY ui/ /ui
RUN npm run build

# Stage 2: Setup the Python environment
FROM python:3.12.3-slim-bullseye
# Install dependencies in one layer and clean up in the same layer
RUN apt-get update && apt-get install -y \
    net-tools \
    telnet \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY src/ /app
COPY requirements.txt ./
# Install Python dependencies
RUN pip install --no-cache-dir --no-dependencies -r requirements.txt
COPY start_server.sh ./
COPY --from=build /ui/dist/sakai-ng /app/server/static

CMD ["./start_server.sh"]