FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (ffmpeg is critical for your bot)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry:
# virtualenvs.create false: Installs packages globally in the container (simpler for Docker)
RUN poetry config virtualenvs.create false

# Copy pyproject.toml and poetry.lock (if it exists) first to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Create the mount point for the RAM disk
RUN mkdir -p /mnt/ramdisk

# Copy the rest of the application
COPY . /app

# Define the volume (optional documentation, actual mount happens in compose)
VOLUME ["/mnt/ramdisk"]

# Environment variables
ENV DOWNLOAD_FOLDER=/mnt/ramdisk

# Run the bot
CMD ["python", "main.py"]