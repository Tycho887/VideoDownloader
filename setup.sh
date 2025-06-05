#!/bin/bash

set -e

echo "📁 Checking for .env file..."
if [ ! -f ".env" ]; then
  echo "❌ Error: .env file is missing!"
  exit 1
else
  echo "✅ .env file found."
fi

echo "⬆️ Updating docker-compose..."
pip install --upgrade docker-compose

echo "🧹 Cleaning up old Docker containers and images..."
docker-compose down --volumes --remove-orphans
docker system prune -af -f

echo "🔨 Rebuilding Docker images without cache..."
docker-compose build --no-cache

echo "✅ Done. Run 'docker-compose up' to start the services."
