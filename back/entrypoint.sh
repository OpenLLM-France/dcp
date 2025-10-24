#!/bin/bash

cat <<EOF > /etc/cron.d/update_rating
# Load container environment before each job
DATABASE_URL=${DATABASE_URL}

*/10 * * * * root . /etc/profile; python3 /app/scripts/update_rating.py >> /var/log/cron/task.log 2>&1
EOF

# Start cron in background
cron

# Start main application (keep as PID 1 for proper signal handling)
exec "$@"
