FROM alpine:latest

# Installing dependencies
WORKDIR /app
COPY . .

RUN    apk add --no-cache python3 nodejs npm \
    && python3 -m venv .venv \
    && source .venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt \
    && python3 -m ensurepip 

RUN    mkdir logs shared_files

WORKDIR /app/static
RUN    npm install \
    && npx webpack

WORKDIR /app
CMD [".venv/bin/python3", "backend/server.py"]
