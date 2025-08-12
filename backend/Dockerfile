# Use Python 3.10 slim image for efficiency
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies for OpenCV, ML libraries, moviepy, and other packages
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgomp1 \
    libgtk-3-0 \
    curl \
    wget \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data and models directories for volume mounting
RUN mkdir -p /app/data /app/models /app/db

# Download NLTK data during build (optional - will download at runtime if needed)
RUN python -c "import nltk; nltk.download('punkt', quiet=True, download_dir='/app/nltk_data') or True; nltk.download('stopwords', quiet=True, download_dir='/app/nltk_data') or True; nltk.download('vader_lexicon', quiet=True, download_dir='/app/nltk_data') or True" || true

# Expose the port that FastAPI runs on
EXPOSE 8000

# Run the FastAPI application with production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]