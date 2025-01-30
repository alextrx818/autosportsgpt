FROM python:3.11-slim

WORKDIR /app

# Install git and other dependencies FIRST
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip

# THEN copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Copy production environment file
COPY .env.production .env

# Expose the port for the API server
EXPOSE 8000

# Create a startup script with environment variables
RUN echo '#!/bin/bash\n\
export $(cat .env | xargs)\n\
python sports_monitor_bot.py & \n\
uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8000}\n' > /app/start.sh && \
chmod +x /app/start.sh

# Command to run both services
CMD ["/app/start.sh"]
