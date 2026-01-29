# Pi 3B+ Deployment Guide

## Quick Start

```bash
# 1. Clone the repository on your Pi
git clone <your-repo-url> ~/Website
cd ~/Website

# 2. Make script executable and run
chmod +x deploy-pi.sh
./deploy-pi.sh
```

## Prerequisites

### Install Docker (if not installed)
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in, then verify:
docker --version
```

### Recommended: 64-bit Raspberry Pi OS
The Pi 3B+ supports 64-bit OS, which provides better Docker image compatibility.

## Services Deployed

| Service | Port | Description |
|---------|------|-------------|
| Nginx Proxy Manager | 81 (admin), 80/443 (proxy) | Reverse proxy with SSL |
| Landing Page | via NPM | Static website |
| Keto Monitor | 5000 | News aggregator |
| Handball Tracker | 8000 | FastAPI application |

## Configuration Files Needed

### `infrastructure/.env`
```env
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
```

### `keto-monitor/.env`
```env
# Add your API keys here (e.g., for news APIs)
```

## Post-Deployment

1. Access NPM at `http://<pi-ip>:81`
2. Default login: `admin@example.com` / `changeme`
3. Configure proxy hosts for your domain

## Useful Commands

```bash
# View all containers
docker ps

# View logs
docker logs -f landing-page
docker logs -f handball-tracker

# Restart a service
cd ~/Website/keto-monitor && docker compose restart

# Stop all
cd ~/Website && docker compose -f infrastructure/docker-compose.yml down
```
