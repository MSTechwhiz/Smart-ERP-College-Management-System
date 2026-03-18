#!/bin/bash
# MongoDB Backup Script

BACKUP_DIR="/data/backups/$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "$BACKUP_DIR"

echo "Starting MongoDB backup to $BACKUP_DIR..."

if [ -z "$MONGO_URI" ]; then
    echo "Error: MONGO_URI is not set."
    exit 1
fi

mongodump --uri="$MONGO_URI" --out="$BACKUP_DIR" --gzip

if [ $? -eq 0 ]; then
    echo "Backup completed successfully."
    # Optional: Remove backups older than 7 days
    find /data/backups -type d -mtime +7 -exec rm -rf {} +
else
    echo "Backup failed!"
    exit 1
fi
