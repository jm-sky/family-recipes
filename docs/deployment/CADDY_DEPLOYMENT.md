# Caddy — konfiguracja Family Recipes

**Ostatnia aktualizacja:** 2026-07-06

Konfiguracja Caddy dla dwóch domen na `dev-made.it`, wzorowana na gear-stack (`../gear-stack/docs/deployment/gear-stack.caddy`).

## Domeny

| Domena | Rola | Backend |
|---|---|---|
| `family-recipes.dev-made.it` | Frontend SPA (statyczne pliki) | `/api/*` → `localhost:8002` |
| `api.family-recipes.dev-made.it` | API bezpośrednio | `localhost:8002` |

Plik konfiguracyjny w repozytorium: [`etc/caddy/sites-available/family-recipes.caddy`](../../etc/caddy/sites-available/family-recipes.caddy)

## Wdrożenie na serwerze

```bash
# 1. Skopiuj konfigurację
sudo cp etc/caddy/sites-available/family-recipes.caddy /etc/caddy/sites-available/family-recipes.caddy
sudo chown caddy:caddy /etc/caddy/sites-available/family-recipes.caddy
sudo chmod 644 /etc/caddy/sites-available/family-recipes.caddy

# 2. Włącz site (symlink)
sudo ln -sf /etc/caddy/sites-available/family-recipes.caddy /etc/caddy/sites-enabled/family-recipes.caddy

# 3. Walidacja i reload
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Główny `Caddyfile` importuje wszystkie pliki z `sites-enabled/*.caddy` — nie trzeba go edytować ręcznie.

## Co zawiera konfiguracja

- **Security headers** — CSP (reCaptcha, Sentry), HSTS, X-Frame-Options, itd.
- **Cache** — długi cache dla hashowanych assetów Vite (`/assets/*`), brak cache dla HTML
- **SPA routing** — `try_files {path} /index.html`
- **Reverse proxy** — `/api/*` na frontendowej domenie + osobna subdomena API
- **TLS** — automatyczny certyfikat Let's Encrypt (`tls jan.madeyski@dev-made.it`)

Nagłówki CSP w backendzie (`backend/app/core/security_headers.py`) są zsynchronizowane z Caddy — `connect-src` obejmuje `https://*.family-recipes.dev-made.it`.

## Kolejne kroki po wdrożeniu Caddy

### 1. Katalog deploy frontendu

```bash
sudo mkdir -p /var/www/family-recipes
sudo chown -R caddy:deploy /var/www/family-recipes
sudo chmod -R 775 /var/www/family-recipes
sudo chmod g+s /var/www/family-recipes
```

Szczegóły uprawnień: [DEPLOYMENT.md](../../DEPLOYMENT.md).

### 2. Build i deploy frontendu

```bash
pnpm build
./scripts/frontend_build_deploy.sh
```

### 3. Zmienne backendu (`.env`)

Po przejściu na domeny produkcyjne ustaw m.in.:

```env
ENVIRONMENT=production

CORS_ORIGINS=["https://family-recipes.dev-made.it"]
ALLOWED_HOSTS=["api.family-recipes.dev-made.it","family-recipes.dev-made.it","localhost","127.0.0.1"]

FRONTEND_URL=https://family-recipes.dev-made.it
WEBAUTHN_ORIGIN=https://family-recipes.dev-made.it
STORAGE_BASE_URL=https://api.family-recipes.dev-made.it
```

Po zmianie `.env` zrestartuj kontener backendu:

```bash
docker compose -f backend/docker-compose.dev.yml restart app
```

### 4. DNS

Rekordy A/AAAA dla obu domen muszą wskazywać na ten serwer. Caddy sam wystawi certyfikaty TLS po pierwszym żądaniu HTTPS.

## Weryfikacja

```bash
# Status Caddy
sudo systemctl status caddy

# API przez Caddy
curl -s https://api.family-recipes.dev-made.it/health
# Oczekiwane: {"status":"healthy"}

# Nagłówki bezpieczeństwa frontendu
curl -I https://family-recipes.dev-made.it | grep -E "(Content-Security-Policy|X-Frame-Options|Strict-Transport-Security)"

# Logi
sudo journalctl -u caddy -f
```

## Uwagi

- Frontend używa `VITE_API_BASE_URL=/api` — requesty API idą przez tę samą domenę (`family-recipes.dev-made.it/api/...`), bez zmian w buildzie.
- Subdomena `api.family-recipes.dev-made.it` służy do bezpośredniego dostępu do API, URL-i storage i narzędzi dev.
- Backend nasłuchuje na `127.0.0.1:8002` (patrz `CLAUDE.md` — porty projektu).
- Frontend serwowany z `/var/www/family-recipes/` (właściciel: `caddy:deploy`).

## Aktualizacja konfiguracji

1. Edytuj `etc/caddy/sites-available/family-recipes.caddy` w repozytorium
2. Skopiuj na serwer (patrz sekcja „Wdrożenie na serwerze”)
3. `sudo caddy validate --config /etc/caddy/Caddyfile`
4. `sudo systemctl reload caddy`
