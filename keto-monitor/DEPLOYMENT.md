# Deployment Walkthrough: Keto Monitor on Raspberry Pi

## Overview
Your Keto Monitor application is now successfully deployed on your Raspberry Pi and accessible securely from the internet via **https://thy-projects.com**.

## Architecture
We used a containerized approach for maximum stability and cleanliness:

1.  **Web App (`web`)**: The Flask application running your code.
2.  **Nginx Proxy Manager (`npm`)**: Handles SSL certificates (Let's Encrypt) and routes traffic from the internet to your app.
3.  **Cloudflare DDNS (`ddns`)**: Automatically updates your domain's DNS records whenever your home IP address changes.

## Key Locations
*   **Project Directory:** `~/keto-monitor`
*   **Database:** `~/keto-monitor/keto.db` (Persisted on the Pi)
*   **Config Files:** `~/keto-monitor/config/`
*   **Proxy Data:** `~/keto-monitor/npm/`

## Maintenance Cheat Sheet

### 1. Updating the App
When you make changes to the code on your PC:
1.  **PC:** `git push`
2.  **Pi:**
    ```bash
    cd ~/keto-monitor
    git pull
    docker compose up -d --build
    ```

### 2. Checking Logs
If something isn't working, check the logs:
```bash
# Web App Logs
docker compose logs -f web

# Proxy Logs
docker compose logs -f npm

# DDNS Updater Logs
docker compose logs -f ddns
```

### 3. Accessing the Database
To download the live database from the Pi to your PC for inspection:
```powershell
# Run this on your WINDOWS PC
scp johann@raspi:~/keto-monitor/keto.db C:\path\to\local\folder
```

## Configuration Details
*   **Domain:** `thy-projects.com`
*   **Port Forwarding:** Router ports 80 & 443 -> Raspberry Pi ports 80 & 443.
*   **Nginx Admin Panel:** `http://192.168.178.87:81` (Only accessible from home network)

## Next Steps
*   **Backup:** Consider setting up a cronjob to backup `keto.db` regularly.
*   **Monitoring:** Check the logs occasionally to ensure the daily job runs correctly.
