# Use Python 3.10 for best compatibility
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download Turkish model

COPY backend/download_model.py .
RUN python download_model.py

# Copy application files
COPY . .

# Add network diagnostics
RUN echo "from flask import Flask, request\napp = Flask(__name__)\n\n@app.route('/health')\ndef health():\n    return 'OK'\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000)'" > healthcheck.py

# Expose port
EXPOSE 5000


# Run the application with Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--chdir", "/app", "backend.app:app"]
