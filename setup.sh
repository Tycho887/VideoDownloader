#!/bin/bash

set -e

echo "🔧 Setting up environment for video downloader on Raspberry Pi 5..."

# Update and install base packages
echo "📦 Installing base system packages..."
sudo apt update
sudo apt install -y \
  python3 python3-pip python3-venv \
  ffmpeg \
  build-essential yasm pkg-config \
  libx264-dev libfdk-aac-dev libmp3lame-dev libopus-dev \
  libdav1d-dev git curl

# Check FFmpeg AV1 support
echo "🔍 Verifying FFmpeg AV1 support..."
if ffmpeg -codecs | grep -qE 'D.*AV1'; then
    echo "✅ AV1 codec support found in system FFmpeg."
else
    echo "⚠️ AV1 codec NOT found. Building FFmpeg from source with libdav1d..."

    mkdir -p ~/ffmpeg_build && cd ~/ffmpeg_build

    # Clone FFmpeg source
    git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg && cd ffmpeg

    ./configure \
        --prefix=/usr/local \
        --enable-gpl \
        --enable-libx264 \
        --enable-libmp3lame \
        --enable-libfdk-aac \
        --enable-libopus \
        --enable-libdav1d \
        --enable-nonfree

    make -j$(nproc)
    sudo make install
    hash -r

    echo "✅ FFmpeg rebuilt with AV1 support."
fi

# Return to project root
cd "$(dirname "$0")"

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python packages..."
pip install --upgrade pip
pip install yt-dlp

# Install from requirements.txt if it exists
if [ -f requirements.txt ]; then
    echo "📄 Installing from requirements.txt..."
    pip install -r requirements.txt
fi

echo "✅ Setup complete!"
echo "👉 Run: source venv/bin/activate"
