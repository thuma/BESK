#!/bin/sh
sqlite3 BESK.db ".dump" > "backup-$(date +%Y-%m-%d).sql"
gzip "backup-$(date +%Y-%m-%d).sql"
echo "Nattens backup" | \
mail -aFrom:hej@kodcentrum.se \
-s "BESK Backup" backup@kodcentrum.se \
-A "backup-$(date +%Y-%m-%d).sql.gz"
rm "backup-$(date +%Y-%m-%d).sql.gz"
rm "backup-$(date +%Y-%m-%d).sql"
