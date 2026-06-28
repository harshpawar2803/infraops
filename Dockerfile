FROM python:3.12-slim

WORKDIR /app

# Install required Linux utilities
RUN apt-get update && apt-get install -y \
    procps \
    iproute2 \
    curl \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Application port
EXPOSE 8080

# Start application
CMD ["python", "app.py"]