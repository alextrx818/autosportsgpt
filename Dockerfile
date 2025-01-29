FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose the port for the API server
EXPOSE 8080

# Create a startup script
RUN echo '#!/bin/bash\n\
python sports_monitor_bot.py & \n\
uvicorn api_server:app --host 0.0.0.0 --port 8080\n' > /app/start.sh && \
chmod +x /app/start.sh

# Command to run both services
CMD ["/app/start.sh"]
