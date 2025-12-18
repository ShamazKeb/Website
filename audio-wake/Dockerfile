FROM python:3.11-slim

# Install system dependencies for audio (PortAudio, ALSA)
# alsa-utils is helpful for debugging (aplay, etc.)
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    alsa-utils \
    gcc \
    linux-libc-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Code
COPY . .

# Run
CMD ["python", "main.py"]
