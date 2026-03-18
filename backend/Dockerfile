# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y cron gnupg wget && \
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update && apt-get install -y mongodb-database-tools && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Setup backup cron
COPY scripts/backup.sh /app/scripts/backup.sh
RUN chmod +x /app/scripts/backup.sh && \
    echo "0 2 * * * /app/scripts/backup.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/mongodb-backup && \
    chmod 0644 /etc/cron.d/mongodb-backup && \
    crontab /etc/cron.d/mongodb-backup

# Expose port
EXPOSE 8000

# Run the application (start cron in background)
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
