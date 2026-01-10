FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for opencv and rembg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the rembg model to avoid download at runtime
RUN python -c "from rembg import new_session; new_session('isnet-general-use')"

# Copy the processing script
COPY process_photo.py .

# Set entrypoint
ENTRYPOINT ["python", "process_photo.py"]
