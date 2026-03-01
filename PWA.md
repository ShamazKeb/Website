# PWA Troubleshooting Notes (50Liter)

This repo includes a PWA for `50Liter/frontend`. The most common issue is the homescreen icon showing a default letter (e.g., "A") on iOS. The root cause is almost always caching or the icon not being served by the public entrypoint.

## Quick Checks (Server / Container)

Verify the icon is actually present in the container webroot:

```bash
cd ~/website/50Liter
docker compose exec frontend ls -l /usr/share/nginx/html
```

Expected files:
- `apple-touch-icon-180.png`
- `icon-192.png`
- `icon-512.png`
- `manifest.json`

Verify the container serves the icon correctly:

```bash
docker compose exec frontend curl -I http://localhost/apple-touch-icon-180.png
```

Expected: `Content-Type: image/png`

If missing, rebuild the frontend image:

```bash
docker compose build --no-cache frontend
docker compose up -d --force-recreate frontend
```

## Public Endpoint Check (Cloudflare / Reverse Proxy)

If the container serves the icon but the public URL still returns HTML, a proxy or CDN is caching an old response.

Run:

```bash
curl -I https://50liter.thy-projects.com/apple-touch-icon-180.png
```

Expected: `Content-Type: image/png`

If it returns `text/html` with `cf-cache-status: HIT`, purge the cache (Cloudflare) for:
- `/apple-touch-icon-180.png`
- `/manifest.json`
- `/index.html`

Then re-check until `cf-cache-status: MISS` and `Content-Type: image/png` appear.

## iOS Client Cache Reset (Required)

After fixing the server:
1. Delete the old homescreen icon.
2. iOS Settings → Safari → Advanced → Website Data → delete `50liter.thy-projects.com`.
3. Close Safari (app switcher, swipe away).
4. Open Safari → load site → Share → "Add to Home Screen".

## Notes

- iOS uses `apple-touch-icon` links, not the manifest icons.
- `manifest.json` is mainly for Android install prompts.
- If icons change, use a cache-busting filename or query string.
