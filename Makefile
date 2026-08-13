# ─────────────────────────────────────────────────────────────────────────────
#  KePin — Makefile
#
#  MODE:
#    dev   — mode development: frontend vite dev (HMR) di host,
#             backend/db/smtp-sink di docker
#    local — mode local: seluruh stack (frontend+backend+db+smtp-sink) di docker
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
	@echo ""
	@echo "VARIANT per mode:"
	@echo "  make dev | make dev-build | make dev-build-seed"
	@echo "  make local | make local-build | make local-build-seed"
	@echo ""
	@echo "  <mode>            : jalankan stack (tanpa build ulang image)"
	@echo "  <mode>-build      : build ulang image lalu jalankan"
	@echo "  <mode>-build-seed : build ulang + database fresh + seed demo lengkap"
	@echo ""
	@echo "DOMAIN:"
	@echo "  $(APP_URL)              → frontend (port $(FRONTEND_PORT))"
	@echo "  $(API_URL)              → backend  (port $(BACKEND_PORT))"
	@echo "  Override: make dev DOMAIN=localhost API_DOMAIN=localhost"
	@echo ""
	@echo "UTILITAS:"
	@echo "  make seed        : wipe DB + seed demo lengkap (pakai image yang ada)"
	@echo "  make seed-dev    : wipe DB + seed lengkap, hanya backend (untuk mode dev)"
	@echo "  make ps          : status container"
	@echo "  make logs        : tail log semua service"
	@echo "  make down        : stop + hapus container (volume tetap)"
	@echo "  make reset-db    : hapus container + volume DB (fresh total)"
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
