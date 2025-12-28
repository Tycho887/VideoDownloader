#!/bin/bash

set -e

echo "📁 Checking for .env file..."
if [ ! -f ".env" ]; then
  echo "❌ Error: .env file is missing!"
  exit 1
else
  echo "✅ .env file found."
fi

# Detect if we should use 'docker compose' (v2) or 'docker-compose' (v1)
if docker compose version >/dev/null 2>&1; then
    DOCKER_CMD="docker compose"
else
    DOCKER_CMD="docker-compose"
fi

echo "🧹 Cleaning up old Docker containers and images..."
$DOCKER_CMD down --volumes --remove-orphans
docker system prune -af

echo "🔨 Rebuilding Docker images without cache..."
$DOCKER_CMD build --no-cache

echo "✅ Done. Run '$DOCKER_CMD up -d' to start the services."