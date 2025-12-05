# Architecture Migration Plan: Modular Microservices

## Goal
Transition from a monolithic single-folder setup to a clean, modular architecture where "Infrastructure" (Proxy, DNS) is separated from "Applications" (Keto Monitor, Landing Page).

## 1. Target Architecture
We will organize the project into three sibling directories on the Raspberry Pi:

```text
~/projects/
├── infrastructure/       # Service: Nginx Proxy Manager & Cloudflare DDNS
│   └── docker-compose.yml
├── keto_monitor3.0/      # Service: Keto Monitor App
│   └── docker-compose.yml
└── landing_page/         # Service: Main Landing Page
    ├── docker-compose.yml
    ├── Dockerfile
    └── index.html
```

**Key Concept: The Shared Network**
All containers will communicate via a dedicated Docker network named `web-public`. This allows the Proxy in `infrastructure` to talk to the Apps in other folders.

---

## 2. Migration Steps

### Phase 1: Preparation (The Network)
We need to create the bridge network manually once.
*   **Command:** `docker network create web-public`

### Phase 2: Infrastructure Layer
We will extract the "admin" parts out of the current Keto project.
1.  Create folder `~/projects/infrastructure`.
2.  Create a `docker-compose.yml` containing **only**:
    *   `npm` (Nginx Proxy Manager)
    *   `ddns` (Cloudflare Updater)
3.  **Network Config:** Attach both to `web-public`.
4.  **Volumes:** Ensure we point to the *existing* `npm` data folder so we don't lose your login/certs!

### Phase 3: Keto Monitor Layer (Cleanup)
We strip down the existing `keto_monitor3.0/docker-compose.yml`.
1.  Remove `npm` and `ddns` services.
2.  Keep only `web` (Flask App).
3.  **Network Config:** Attach `web` to `web-public`.
4.  **Ports:** We can remove port mapping `5000:5000` (optional, for security) since Nginx talks internally, but keeping it for local debug is fine.

### Phase 4: Landing Page Layer (New)
We create the new project `~/projects/landing_page`.
1.  **Files:** `index.html` (Content), `Dockerfile` (Nginx static).
2.  **Docker Compose:** Define service `landing`.
3.  **Network Config:** Attach to `web-public`.

### Phase 5: Execution & Switchover
1.  **Stop everything:** `docker compose down` in the old folder.
2.  **Start Infrastructure:** `docker compose up -d` in `infrastructure/`.
3.  **Start Keto:** `docker compose up -d` in `keto_monitor3.0/`.
4.  **Start Landing:** `docker compose up -d` in `landing_page/`.
5.  **Reconfigure Nginx:**
    *   Update Host `thy-projects.com` -> Forward to Hostname `landing` (Port 80).
    *   Update Host `keto.thy-projects.com` -> Forward to Hostname `web` (Port 5000).

---

## 3. Detailed Configuration Previews

### A. Infrastructure `docker-compose.yml`
```yaml
services:
  npm:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '443:443'
      - '81:81'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
    networks:
      - web-public

  ddns:
    image: oznu/cloudflare-ddns:latest
    restart: always
    environment:
      - API_KEY=${CLOUDFLARE_API_TOKEN}
      - ZONE=thy-projects.com
      - PROXIED=true
    networks:
      - web-public

networks:
  web-public:
    external: true
```

### B. Keto Monitor `docker-compose.yml` (Updated)
```yaml
services:
  web:
    build: .
    restart: unless-stopped
    volumes:
      - ./keto.db:/app/keto.db
      - ./config:/app/config
    env_file:
      - .env
    networks:
      - web-public

networks:
  web-public:
    external: true
```

### C. Landing Page `docker-compose.yml`
```yaml
services:
  landing:
    build: .
    restart: unless-stopped
    networks:
      - web-public

networks:
  web-public:
    external: true
```
