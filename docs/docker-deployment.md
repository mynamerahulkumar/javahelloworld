# Docker Deployment Guide

This project now ships separate container images for the FastAPI backend and the Next.js frontend. The instructions below cover local development as well as deploying the images to an AWS EC2 Linux instance.

## 1. Build Images Locally

```bash
# From the repository root
docker build -t trading-backend:latest ./backend
docker build -t trading-frontend:latest ./frontend
```

Every build relies on the `.dockerignore` at the repository root, so unnecessary artefacts (logs, node_modules, etc.) are excluded automatically.

## 2. Run Locally with Docker Compose

```bash
docker compose up --build
```

The compose file starts two services:

- `backend`: exposes port `8501` (FastAPI + Uvicorn). Customise with `BACKEND_PORT`, `BACKEND_WORKERS`, and `UVICORN_LOG_LEVEL` environment variables.
- `frontend`: exposes port `3000` and depends on the backend. Override `NEXT_PUBLIC_API_BASE_URL` if you point the UI at a different backend.

Stop the stack with:

```bash
docker compose down
```

## 3. Deploy to AWS EC2 (Linux)

1. **Install Docker (once per instance)**  
   ```bash
   sudo yum update -y                      # Amazon Linux
   sudo yum install docker -y              # or sudo dnf ... on AL2023 / sudo apt ... on Ubuntu
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo usermod -aG docker ec2-user        # log out/in afterwards
   ```

2. **Copy sources or pull from Git**  
   - Either clone this repository on the instance or synchronise the `backend/` and `frontend/` directories via SCP.

3. **Build images on the instance**  
   ```bash
   docker build -t trading-backend:latest ./backend
   docker build -t trading-frontend:latest ./frontend
   ```
   *Alternative*: Build locally, push to your registry (e.g. ECR), then `docker pull` on EC2.

4. **Run containers**
   ```bash
   docker run -d --name trading-backend \
     -p 8501:8501 \
     -e BACKEND_WORKERS=2 \
     trading-backend:latest

   docker run -d --name trading-frontend \
     --link trading-backend \
     -p 3000:3000 \
     -e NEXT_PUBLIC_API_BASE_URL=http://trading-backend:8501/api/v1 \
     trading-frontend:latest
   ```

   The `--link` flag is convenient for simple setups; for production, consider a user-defined bridge network:

   ```bash
   docker network create trading-net
   docker run -d --name trading-backend --network trading-net -p 8501:8501 trading-backend:latest
   docker run -d --name trading-frontend --network trading-net -p 3000:3000 \
     -e NEXT_PUBLIC_API_BASE_URL=http://trading-backend:8501/api/v1 trading-frontend:latest
   ```

5. **(Optional) Use Docker Compose on EC2**
   ```bash
   docker compose up -d
   ```
   Compose honours the same environment variables, so you can customise ports or API URLs via `.env` files or inline `VAR=value docker compose up`.

## 4. Image Tagging for Registries

If you publish the images to Amazon ECR or another registry:

```bash
AWS_ACCOUNT_ID=123456789012
AWS_REGION=us-east-1
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ECR_URI"

docker tag trading-backend:latest "$ECR_URI/trading-backend:latest"
docker tag trading-frontend:latest "$ECR_URI/trading-frontend:latest"
docker push "$ECR_URI/trading-backend:latest"
docker push "$ECR_URI/trading-frontend:latest"
```

Pull the images on EC2 using `docker pull $ECR_URI/trading-backend:latest` and `docker pull $ECR_URI/trading-frontend:latest`.

## 5. Cleanup Legacy Assets

The older monolithic Docker image (`Dockerfile` at the repository root and `docker/start.sh`) has been removed. Use the new per-service Dockerfiles instead.

