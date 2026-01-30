# ================================
# Caro Website - Multi-Stage Dockerfile
# ================================

# Stage 1: Build Node.js backend dependencies
FROM node:20-alpine AS backend-builder

WORKDIR /app/backend
COPY backend/package*.json ./
RUN npm ci --only=production

# Stage 2: Production image with nginx + Node.js
FROM node:20-alpine

# Install nginx
RUN apk add --no-cache nginx

# Create app directories
WORKDIR /app

# Copy backend files
COPY --from=backend-builder /app/backend/node_modules ./backend/node_modules
COPY backend/ ./backend/

# Copy frontend files to nginx directory
COPY public/ /var/www/html/

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/http.d/default.conf

# Create data directory for SQLite persistence
RUN mkdir -p /app/backend/data

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3001
ENV DATABASE_PATH=/app/backend/data/database.sqlite

# Expose ports
EXPOSE 80 3001

# Copy and set entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
