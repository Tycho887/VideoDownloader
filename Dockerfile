# Use a lightweight ARM-compatible image
FROM python:3.10.12-slim-bullseye

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
       ffmpeg \
       libsm6 \
       libxext6 \
       libgl1 \
       && apt-get clean \
       && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a tmpfs directory for downloads
RUN mkdir -p /mnt/ramdisk

# Set up a tmpfs mount point for /mnt/ramdisk
VOLUME ["/mnt/ramdisk"]

# Default environment variables
ENV DOWNLOAD_FOLDER=/mnt/ramdisk
ENV BOT_ENV_FILE=/app/.env

# Set the command to run the bot
CMD ["python", "main.py"]
