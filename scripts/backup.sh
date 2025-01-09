#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump apical_shopify > "$BACKUP_DIR/db_$DATE.sql"

# Media files backup
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /path/to/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete 