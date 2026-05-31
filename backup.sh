#!/bin/bash
# Backs up Capitol Watch data files
# Runs every hour, keeps last 48 backups

BACKUP_DIR="$HOME/Desktop/capitol-watch-backups"
SOURCE_DIR="$HOME/Desktop/capitol-watch"
TIMESTAMP=$(date "+%Y-%m-%d_%H-%M-%S")

# Create backup folder for this hour
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

# Copy the important files
cp "$SOURCE_DIR/votes.json" "$BACKUP_DIR/$TIMESTAMP/votes.json" 2>/dev/null
cp "$SOURCE_DIR/bill-analysis.json" "$BACKUP_DIR/$TIMESTAMP/bill-analysis.json" 2>/dev/null
cp "$SOURCE_DIR/server.js" "$BACKUP_DIR/$TIMESTAMP/server.js" 2>/dev/null

# Keep only the last 48 backups (2 days)
ls -1t "$BACKUP_DIR" | tail -n +49 | xargs -I{} rm -rf "$BACKUP_DIR/{}" 2>/dev/null

echo "Backup complete: $TIMESTAMP"
