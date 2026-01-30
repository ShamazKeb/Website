#!/bin/sh

# Start Node.js backend in background
cd /app/backend
npm start &

# Start Nginx in foreground
nginx -g "daemon off;"
