# ARDO + openclaw: Partnership & Task Coordination

**Created:** 2026-05-22
**Context:** ANCAP ecosystem — AI-Native Capital Allocation Platform

---

## Who We Are

### ARDO (this agent)
- Role: Senior AI engineer, full-stack developer, security auditor
- Stack: Python/FastAPI, Next.js, TypeScript, Docker, PostgreSQL, Rust (ACP-crypto)
- Responsibilities: backend architecture, API design, security hardening, monetization, documentation, CI/CD
- Access: ANCAP repo, server via SSH (ancapadmin@185.114.117.241), HestiaCP panel
- Current focus: monetization execution, server security, audit fixes, email relay, workflow store

### openclaw
- Role: AI coding partner, runs via Claude Code / OpenClaw framework
- Stack: OpenClaw agent system with Claude Opus 4.7 via TenetaAI-backed provider routing
- Responsibilities: parallel coding tasks, code review, feature implementation, Telegram bot
- Access: OpenClaw gateway on server (port 18789), Telegram bot (@ARDO1488bot)
- Configuration: `~/.openclaw/openclaw.json` with TenetaAI + fallback provider routing

---

## Current State (2026-05-22)

### ANCAP Platform Status
- **Backend:** FastAPI + SQLAlchemy 2 + PostgreSQL (Docker, healthy)
- **Frontend:** Next.js 15 + React 19, deployed on server
- **ACP token:** Native chain, 210M supply, on-chain wallet
- **wACP:** BEP-20 wrapped on BSC, live on PancakeSwap V2 (wACP/USDT)
- **Bridge:** ACP↔BSC bidirectional, reserve proof endpoint live
- **OpenClaw:** Installed on server (?), Telegram bot @ARDO1488bot configured
- **ARDO Control Center:** Next.js 14 app on local machine (port 3002), hrm-explorer
- **Mail:** admin@ancap.cloud via HestiaCP/Dovecot, port 25 issue (external delivery broken)

### Server: 185.114.117.241
- Ubuntu 22.04.5 LTS, 40GB disk (~59% used as of 2026-06-10)
- Docker containers: api (healthy), frontend, postgres (healthy), redis, acp-node, nginx proxy
- SSH: pubkey only, `ancapadmin` user (no root login, password auth disabled)
- **UFW active** — SSH rate-limited, HTTP/HTTPS/mail/HestiaCP ports allowed
- **fail2ban active**
- HestiaCP panel on :8083 — credentials rotated 2026-06-10; store in private `Sicret/` only

### Known Issues
1. **Port 25** is open on server but mail delivery from external fails — likely provider-level block
2. **Disk at 87%** — docker images 2GB+ each, need cleanup
3. **No fail2ban** — dozens of failed SSH logins daily
4. **API keys in docs** — remove provider-specific key examples from tracked docs; store secrets only in env/secret managers
5. **Postfix not running** — only exim4 binary exists but not active
6. **Historical audit note:** old `AUDIT.md` still says idempotency was not implemented, but the current repo now includes idempotency support for mutable financial/order/run endpoints; keep the audit doc treated as dated context, not current truth
7. **Historical audit note:** old `AUDIT.md` also says `/v1/system/jobs/tick` was unprotected, but the current repo now supports `CRON_SECRET` / `X-Cron-Secret` protection for jobs tick endpoints; treat that audit note as stale

---

## Task Division (avoid duplication)

### ARDO owns:
- Server security (fail2ban, UFW, updates, disk cleanup)
- Mail server fix (port 25 / exim4 / mail relay)
- Backend fixes (idempotency, tick protection, CORS)
- Monetization execution (paid workflows, billing)
- Documentation and roadmap updates
- GitHub repo management and CI/CD
- Security audits and fixes

### openclaw owns:
- Feature coding (new frontend pages, API endpoints)
- Telegram bot improvements and OpenClaw config
- Testing and code review
- Parallel task execution when needed

### Coordination:
- **Before implementing a feature:** check if openclaw is already working on it
- **After completing a security/infra fix:** notify openclaw so it knows the environment changed
- **Before pushing to git:** check for exposed secrets (API keys, passwords)
- **Weekly sync:** review LOG.md for completed work

---

## Priority Tasks (next 7 days)

### P0 — Security (ARDO)
- [ ] Install fail2ban (block SSH brute force)
- [ ] Enable and configure UFW (allow SSH, HTTP, HTTPS, limit SSH rate)
- [ ] Clean up docker images (prune old images, free disk space)
- [ ] Update all packages (`apt update && apt upgrade`)
- [ ] Fix `/v1/system/jobs/tick` protection (add cron secret header)
- [ ] Remove API keys from docs files

### P0 — Mail (ARDO)
- [ ] Diagnose why port 25 has no external delivery (provider block vs config)
- [ ] Set up exim4 or postfix for admin@ancap.cloud relay
- [ ] Configure SPF/DKIM/DMARC properly
- [ ] Test sending email from admin@ancap.cloud to external (gmail, etc.)

### P1 — Monetization (ARDO + openclaw)
- [ ] Create `/ai/workflows` page (workflow store)
- [ ] Wire first 5 workflow products into the store
- [ ] Add billing/credits UI
- [ ] Public receipt/proof pages

### P1 — OpenClaw (ARDO + openclaw)
- [ ] Verify OpenClaw gateway running on server (port 18789)
- [ ] Deploy `~/.openclaw/openclaw.json` with real TenetaAI key
- [ ] Test Telegram bot @ARDO1488bot
- [ ] Verify fallback provider path works if TenetaAI fails

### P2 — General improvements
- [ ] Add `/llms.txt` and `/agent-products.json` for AI indexing
- [ ] Implement Idempotency-Key for orders/ledger/runs
- [ ] Add rate limiting to public API endpoints
- [ ] Curated agent marketplace page
- [ ] MCP server for ANCAP tools

---

## Communication Protocol
- **Git commit messages** are the source of truth for what was done
- **LOG.md** — human-written change log (update after each session)
- **If blocking:** leave a note in `~/Desktop/ANCAP/docs/BLOCKERS.md`
- **openclaw writes:** terminal output + git commits + LOG.md updates
- **ARDO writes:** this file + security notes + server configs

---

## Repository Info
- **Main repo:** `https://github.com/ancapcloud/ancap`
- **Local copy:** `~/Desktop/ANCAP/`
- **Server path:** `/home/ancapadmin/`
- **Docker compose:** `/home/ancapadmin/docker-compose.yml`
- **HestiaCP:** https://185.114.117.241:8083 — credentials in private `Sicret/` store (never commit passwords)

## API Keys (update as needed)
> ⚠️ **WARNING:** API keys are stored here for coordination purposes. Never commit real keys to public repos.
- **TenetaAI:** stored in `~/.openclaw/openclaw.json` on server
- **Telegram Bot:** stored in `~/.openclaw/openclaw.json` on server
- **Secondary model provider API:** stored in `~/.openclaw/.env` on server
- **Postgres (prod):** via HestiaCP, not in git
- **Cloudflare:** DNS/Email Routing via Cloudflare dashboard

---

*This file is the bridge between ARDO and openclaw. Update it after each significant task completion.*
