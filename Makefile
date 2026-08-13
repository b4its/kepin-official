# ─────────────────────────────────────────────────────────────────────────────
#  KePin — Makefile
#
#  MODE:
#    dev   — mode development: frontend vite dev (HMR) di host,
#             backend/db/smtp-sink di docker (akses lewat localhost)
#    local — mode local: seluruh stack (frontend+backend+db+smtp-sink) di docker
#    prod  — mode produksi: seluruh stack di docker + nginx reverse-proxy
#             (make prod-nginx) dengan HTTPS di domain publik
#
#  VARIANT per mode:
#    <mode>            — jalankan stack (tanpa build ulang image)
#    <mode>-build      — build ulang image docker lalu jalankan
#    <mode>-build-seed — build ulang + database fresh + generate seed demo
#                        lengkap (semua tenant/modul) lalu jalankan
#
#  DOMAIN:
#    kepin.oryphem.com      → frontend  (port FRONTEND_PORT, default 3001)
#    api.kepin.oryphem.com  → backend   (port BACKEND_PORT, default 8001)
#
#  DEPLOY PRODUKSI (publish ke domain publik):
#    make prod-build-seed   → build semua image + DB fresh + seed + jalankan
#    make prod-nginx        → pasang reverse-proxy nginx + SSL (certbot)
#
#  Override contoh:
#    make dev DOMAIN=localhost API_DOMAIN=localhost
#    make local-build PUBLIC_API_URL=http://localhost:8001/api/v1
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN        ?= kepin.oryphem.com
API_DOMAIN    ?= api.kepin.oryphem.com
FRONTEND_PORT ?= 3001
BACKEND_PORT  ?= 8001
DB_PORT       ?= 5434

APP_URL       ?= http://$(DOMAIN)
API_URL       ?= http://$(API_DOMAIN)/api/v1

HTTPS_APP_URL ?= https://$(DOMAIN)
HTTPS_API_URL ?= https://$(API_DOMAIN)/api/v1

# ── Tooling: pastikan node & pnpm ditemukan oleh make ────────────────────────
# Make menjalankan recipe dengan /bin/sh. Di server yang memakai nvm, node/pnpm
# hanya aktif di shell interaktif, sehingga perlu dicari manual (fallback nvm).
NODE_BIN := $(shell command -v pnpm 2>/dev/null | xargs -r dirname 2>/dev/null)
ifeq ($(NODE_BIN),)
NODE_BIN := $(shell ls -d $(HOME)/.nvm/versions/node/*/bin 2>/dev/null | tail -n1)
endif
export PATH := $(NODE_BIN):$(PATH)

# Pastikan pnpm benar-benar terpasang. Corepack sudah tidak dibundel sejak
# Node 25, jadi install global via npm bila belum ada (satu kali saja).
ifeq ($(shell command -v pnpm 2>/dev/null),)
$(info ⚠ pnpm belum terpasang — menginstall "npm install -g pnpm" ...)
$(shell npm install -g pnpm >/dev/null 2>&1)
endif

COMPOSE      := docker compose
COMPOSE_FULL := $(COMPOSE) --profile full

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo ""
	@echo "KePin — Makefile"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "MODE:"
	@echo "  dev   : frontend vite dev (HMR) di host + backend/db/smtp di docker"
	@echo "  local : seluruh stack (frontend+backend+db+smtp) di docker"
	@echo "  prod  : seluruh stack di docker + nginx HTTPS (publish ke domain)"
	@echo ""
	@echo "VARIANT per mode:"
	@echo "  make dev | make dev-build | make dev-build-seed"
	@echo "  make local | make local-build | make local-build-seed"
	@echo "  make prod | make prod-build | make prod-build-seed"
	@echo ""
	@echo "  <mode>            : jalankan stack (tanpa build ulang image)"
	@echo "  <mode>-build      : build ulang image lalu jalankan"
	@echo "  <mode>-build-seed : build ulang + database fresh + seed demo lengkap"
	@echo ""
	@echo "DEPLOY PRODUKSI:"
	@echo "  make prod-build-seed : build + DB fresh + seed + jalankan stack produksi"
	@echo "  make prod-nginx      : pasang nginx reverse-proxy + SSL certbot"
	@echo ""
	@echo "DOMAIN:"
	@echo "  $(HTTPS_APP_URL)          → frontend (port $(FRONTEND_PORT))"
	@echo "  $(HTTPS_API_URL)/docs     → backend  (port $(BACKEND_PORT))"
	@echo "  Override: make dev DOMAIN=localhost API_DOMAIN=localhost"
	@echo ""
	@echo "UTILITAS:"
	@echo "  make seed        : wipe DB + seed demo lengkap (pakai image yang ada)"
	@echo "  make seed-dev    : wipe DB + seed lengkap, hanya backend (untuk mode dev)"
	@echo "  make ps          : status container"
	@echo "  make logs        : tail log semua service"
	@echo "  make down        : stop + hapus container (volume tetap)"
	@echo "  make reset-db    : hapus container + volume DB (fresh total)"
	@echo "  make prod-nginx  : pasang nginx reverse-proxy + SSL (deploy produksi)"
	@echo ""

# ─────────────────────────── Mode Development ────────────────────────────────

.PHONY: dev
dev: ## jalankan backend/db docker + frontend vite dev (HMR) — tanpa build
	-$(COMPOSE_FULL) stop frontend
	$(COMPOSE_FULL) up -d backend
	@echo ""
	@echo "→ Frontend dev: http://localhost:$(FRONTEND_PORT)  (API: $(API_URL))"
	@echo "→ Backend:      http://localhost:$(BACKEND_PORT)/docs"
	@cd frontend && PUBLIC_API_URL=$(API_URL) pnpm exec vite dev --host 0.0.0.0 --port $(FRONTEND_PORT)

.PHONY: dev-build
dev-build: ## build ulang image backend + jalankan mode development
	-$(COMPOSE_FULL) stop frontend
	$(COMPOSE_FULL) build backend
	$(COMPOSE_FULL) up -d backend
	@echo ""
	@echo "→ Frontend dev: http://localhost:$(FRONTEND_PORT)  (API: $(API_URL))"
	@echo "→ Backend:      http://localhost:$(BACKEND_PORT)/docs"
	@cd frontend && PUBLIC_API_URL=$(API_URL) pnpm exec vite dev --host 0.0.0.0 --port $(FRONTEND_PORT)

.PHONY: dev-build-seed
dev-build-seed: ## build + database fresh + seed demo lengkap + jalankan mode development
	$(MAKE) reset-db
	$(COMPOSE_FULL) build backend
	$(COMPOSE_FULL) up -d backend
	@echo ""
	@echo "→ Seed demo lengkap sudah digenerate (semua tenant & modul)."
	@echo "→ Frontend dev: http://localhost:$(FRONTEND_PORT)  (API: $(API_URL))"
	@echo "→ Backend:      http://localhost:$(BACKEND_PORT)/docs"
	@cd frontend && PUBLIC_API_URL=$(API_URL) pnpm exec vite dev --host 0.0.0.0 --port $(FRONTEND_PORT)

# ────────────────────────────── Mode Local ───────────────────────────────────

.PHONY: local
local: ## jalankan seluruh stack docker (tanpa build ulang image)
	$(COMPOSE_FULL) up -d
	@echo ""
	@echo "→ Frontend: http://localhost:$(FRONTEND_PORT)"
	@echo "→ Backend:  http://localhost:$(BACKEND_PORT)/docs"
	@echo "→ DB:       localhost:$(DB_PORT) (kepin/kepin/kepin)"

.PHONY: local-build
local-build: ## build ulang seluruh image + jalankan seluruh stack docker
	$(COMPOSE_FULL) build
	$(COMPOSE_FULL) up -d
	@echo ""
	@echo "→ Frontend: http://localhost:$(FRONTEND_PORT)"
	@echo "→ Backend:  http://localhost:$(BACKEND_PORT)/docs"
	@echo "→ DB:       localhost:$(DB_PORT) (kepin/kepin/kepin)"

.PHONY: local-build-seed
local-build-seed: ## build + database fresh + seed demo lengkap + jalankan seluruh stack docker
	$(MAKE) reset-db
	$(COMPOSE_FULL) build
	$(COMPOSE_FULL) up -d
	@echo ""
	@echo "→ Seed demo lengkap sudah digenerate (semua tenant & modul)."
	@echo "→ Frontend: http://localhost:$(FRONTEND_PORT)"
	@echo "→ Backend:  http://localhost:$(BACKEND_PORT)/docs"
	@echo "→ DB:       localhost:$(DB_PORT) (kepin/kepin/kepin)"

# ────────────────────────────── Mode Production ──────────────────────────────

.PHONY: prod
prod: ## jalankan seluruh stack docker produksi (tanpa build ulang)
	PUBLIC_API_URL=$(HTTPS_API_URL) PUBLIC_APP_URL=$(HTTPS_APP_URL) $(COMPOSE_FULL) up -d
	@echo ""
	@echo "→ Frontend: $(HTTPS_APP_URL)"
	@echo "→ Backend:  $(HTTPS_API_URL)/docs"

.PHONY: prod-build
prod-build: ## build ulang image + jalankan seluruh stack produksi
	PUBLIC_API_URL=$(HTTPS_API_URL) PUBLIC_APP_URL=$(HTTPS_APP_URL) $(COMPOSE_FULL) build
	PUBLIC_API_URL=$(HTTPS_API_URL) PUBLIC_APP_URL=$(HTTPS_APP_URL) $(COMPOSE_FULL) up -d
	@echo ""
	@echo "→ Frontend: $(HTTPS_APP_URL)"
	@echo "→ Backend:  $(HTTPS_API_URL)/docs"

.PHONY: prod-build-seed
prod-build-seed: ## build + database fresh + seed demo lengkap + jalankan stack produksi
	$(MAKE) reset-db
	PUBLIC_API_URL=$(HTTPS_API_URL) PUBLIC_APP_URL=$(HTTPS_APP_URL) $(COMPOSE_FULL) build
	PUBLIC_API_URL=$(HTTPS_API_URL) PUBLIC_APP_URL=$(HTTPS_APP_URL) $(COMPOSE_FULL) up -d
	@echo ""
	@echo "→ Seed demo lengkap sudah digenerate (semua tenant & modul)."
	@echo "→ Frontend: $(HTTPS_APP_URL)"
	@echo "→ Backend:  $(HTTPS_API_URL)/docs"

.PHONY: prod-nginx
prod-nginx: ## pasang reverse-proxy nginx + SSL certbot untuk domain produksi
	./scripts/nginx-setup.sh $(DOMAIN) $(API_DOMAIN)

# ─────────────────────────────── Seed ────────────────────────────────────────

.PHONY: seed
seed: ## wipe database + seed demo lengkap (image yang sudah ada)
	$(MAKE) reset-db
	$(COMPOSE_FULL) up -d
	@echo "→ Database fresh & seed demo lengkap selesai."

.PHONY: seed-dev
seed-dev: ## wipe database + seed lengkap (hanya backend, untuk mode dev)
	$(MAKE) reset-db
	$(COMPOSE_FULL) up -d backend
	@echo "→ Database fresh & seed demo lengkap selesai (backend saja)."

# ────────────────────────────── Utilitas ─────────────────────────────────────

.PHONY: ps
ps: ## status container
	$(COMPOSE) ps

.PHONY: logs
logs: ## tail log semua service
	$(COMPOSE_FULL) logs -f --tail=100

.PHONY: down
down: ## stop + hapus container (volume tetap)
	$(COMPOSE_FULL) down

.PHONY: reset-db
reset-db: ## hapus container + volume DB (fresh total, seed ulang saat startup)
	$(COMPOSE_FULL) down -v
