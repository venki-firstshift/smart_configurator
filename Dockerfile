# Stage 1: Build the UI application
#FROM node:22.9.0-alpine AS build
#WORKDIR /ui
#COPY ui/package*.json /ui/
#RUN npm ci --prefer-offline --no-audit --progress=false
#COPY ui/ /ui
#RUN npm run build
#COPY --from=build /ui/dist/sakai-ng /app/ui

# Stage 2: Setup the Python environment
#FROM python:3.12.3-slim-bullseye
FROM tiangolo/uwsgi-nginx:python3.12
ENV LISTEN_PORT 18080
EXPOSE 18080
# Replace ngnix conf completely
COPY nginx.conf /app
COPY index.html /app/www/index.html
# Replace supervisord conf file
COPY supervisord.conf /etc/supervisor/conf.d

# Install dependencies in one layer and clean up in the same layer
RUN apt-get update && apt-get install -y \
    net-tools \
    telnet \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY src/ /app
COPY requirements.txt ./
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
COPY start_server.sh ./

CMD ["/app/start_server.sh"]