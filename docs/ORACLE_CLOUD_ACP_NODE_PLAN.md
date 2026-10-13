# Oracle Cloud Free Tier — ACP node plan

**Status:** `[x]` **Independent secondary ACP full node live** on Oracle Always Free (`eu-zurich-1`, 2026-10-02).  
**Goal:** Public-facing Always Free ACP full node beside primary `ancap.cloud`, with documented bootstrap, peer sync, and GitHub transparency.

**Network role:** secondary full node (peer of primary). Not a cutover away from `ancap.cloud`.

This document is the **public plan of action**. It does **not** contain OCI tenancy IDs, SSH keys, RPC tokens, or miner reward secrets.

---

## Live peer (2026-10-03)

| Item | Value |
|------|--------|
| Region | `eu-zurich-1` |
| Shape (current) | `VM.Standard.E2.1.Micro` (x86_64 Always Free) — Ampere A1 preferred when OCI capacity allows |
| Public IP | `152.67.79.206` |
| JSON-RPC | `http://152.67.79.206:8545/rpc` |
| P2P listen | `30333/tcp` |
| Sync peer | `http://185.114.117.241:18545/rpc` (primary HTTP peer; UFW allowlist Oracle IP) |
| Tip check | height **18**, tip hash matches `acp1` / primary (`ab6bdd19…d018`) — verified 2026-10-13 with Oracle + local PC peer |
| Planned hostname | `acp2.ancap.cloud` (TLS + rate-limit) once DNS is pointed |
| Local PC peer | `http://127.0.0.1:8545/rpc` via `scripts/start-acp-node.ps1 -Background` + `ACP_PEER_RPC_URLS=http://185.114.117.241:18545/rpc` (HTTPS peer needs rustls rebuild; stale EXE fails TLS) |

### Sync incident (2026-10-03)

Oracle lagged at height 12 while primary was at 17. Root cause: Oracle `acp-node` binary used `reqwest` **without TLS features**, so `https://acp1.ancap.cloud/rpc` peer sync failed every tick. Host `curl -4` to Cloudflare worked; the node binary could not.

**Mitigation live now:** primary exposes read RPC on host `:18545` via `acp-rpc-peer-expose` (socat → `acp-node:8545`), UFW allows only Oracle `152.67.79.206`. Oracle `ACP_PEER_RPC_URLS` points at that HTTP peer.

**Code fix (repo):** `ACP-crypto/acp-node/Cargo.toml` adds `reqwest` feature `rustls-tls` so future Oracle images can sync over HTTPS again after rebuild/redeploy.

Read methods on the Oracle peer accept unauthenticated `getblockcount` / chain probes. State-changing methods still require the host-local `rpc.token` (never published).

---

## Why Oracle Cloud Free Tier

Oracle Cloud **Always Free** includes:

| Resource | Always Free budget (typical) |
|----------|------------------------------|
| Compute | Ampere **A1** up to ~**2–4 OCPU** + **12–24 GB** RAM when capacity exists; and/or **E2.1.Micro** (x86_64) |
| Storage | Free block volume + object storage within free-tier caps |
| Network | Free egress / VCN within free-tier caps |

```text
Oracle Cloud Always Free
        │
        ├── E2.1.Micro (live today) ──► linux/amd64 acp-node in debian:bookworm-slim
        └── Ampere A1 (when capacity) ► native linux/arm64 build on-box
             │
             ▼
        peer sync → https://acp1.ancap.cloud/rpc
             │
             ├── public read RPC :8545
             └── P2P listen :30333
```

**2026-10-02 capacity note:** `VM.Standard.A1.Flex` returned `Out of host capacity` in `eu-zurich-1`. The live secondary node therefore runs on the existing Always Free **E2.1.Micro** with a production `linux/amd64` binary inside a CA-enabled slim runtime. Re-try Ampere when OCI frees A1 inventory; keep the same peer URL / DNS plan.

---

## Current truth

| Item | State |
|------|--------|
| Oracle Cloud registration + API key | **[x] Done** |
| Always Free VM + Public IP | **[x] Done** — IP `152.67.79.206` |
| Security list SSH `22` / RPC `8545` / P2P `30333` | **[x] Done** |
| Swap + Docker CE on Oracle Linux 9 | **[x] Done** |
| Independent `acp-node` process | **[x] Done** — `ancap/acp-node:oracle` container |
| Sync to primary tip family | **[x] Done** — height 12 / 210M hard cap |
| Public peer URL documented | **[x] Done** — IP RPC above; `acp2.ancap.cloud` pending DNS/TLS |
| Ampere A1 native ARM64 path | `[~]` Scripted; blocked on OCI host capacity |

Primary production node remains Docker `acp-node` behind `acp1.ancap.cloud`. Oracle is a **parallel / secondary** node.

### Operator bootstrap

```powershell
# Prefer opc on Oracle Linux images; ubuntu on Canonical images.
.\scripts\deploy-oracle-acp-node.ps1 `
  -HostIp 152.67.79.206 `
  -KeyPath $env:USERPROFILE\Downloads\ssh-key-2026-09-30.key `
  -User opc `
  -Arch amd64 `
  -BinaryPath $env:TEMP\acp-oracle\acp-node
```

Or GitHub Actions [`Deploy Oracle ACP node`](../.github/workflows/deploy-oracle-acp-node.yml) with secret `ORACLE_ACP_SSH_KEY` and input `host_ip`.

Do **not** commit private SSH / OCI API keys. Rotate any key that was pasted into chat.

---

## ARM64 requirement (Ampere path)

Oracle Ampere A1 is **aarch64**. When capacity returns, build on-box:

```bash
cd ACP-crypto
docker build -f acp-node/Dockerfile -t ancap/acp-node:arm64 .
```

Or use `-Arch arm64` in `scripts/deploy-oracle-acp-node.ps1`.

---

## Phased action plan

### Phase O0 — Account & tenancy `[x]`
### Phase O1 — VM + Public IP `[x]` (E2 Micro live; A1 retry open)
### Phase O2 — Host baseline `[x]` (swap, Docker, firewalld, security list)
### Phase O3 — Run `acp-node` `[x]` (peer env `ACP_PEER_RPC_URLS`, miner off on secondary)
### Phase O4 — Public edge `[~]` (raw IP RPC live; TLS hostname + CF rate-limit open)
### Phase O5 — Validator / miner posture `[ ]` (secondary stays full-node first)
### Phase O6 — GitHub transparency `[x]` (this plan + STATUS + deploy script/workflow)

---

## Security & hygiene

- Never commit OCI API keys, SSH private keys, `ACP_RPC_TOKEN`, miner keystores, or tenancy OCID dump files.
- Secondary node: `ACP_MINER_ENABLED=false` unless an operator-funded reward address is intentional.
- Peer sync must send a `User-Agent` (Cloudflare in front of `acp1` rejects bare POSTs) and must **not** forward the local admin RPC token to peers.
- Free Tier ≠ anonymous: fail2ban / SSH key-only / unattended updates still apply.
- RocksDB on micro: keep `db_cache_mb` low and maintain swap.

---

## Success criteria

1. Secondary tip matches primary tip family (regenesis v3 / hard cap 210M)
2. Public read RPC reachable for peers and explorers
3. Documented peer URL without publishing admin tokens
4. No secrets in git history
5. Ampere migration path remains scripted for when capacity returns

---

## Related

- Node crate: [`ACP-crypto/acp-node/`](../ACP-crypto/acp-node/)
- Deploy script: [`scripts/deploy-oracle-acp-node.ps1`](../scripts/deploy-oracle-acp-node.ps1)
- Workflow: [`.github/workflows/deploy-oracle-acp-node.yml`](../.github/workflows/deploy-oracle-acp-node.yml)
- Prod compose service: `acp-node` in [`docker-compose.prod.yml`](../docker-compose.prod.yml)
- Lean chain notes: [`docs/ACP_LEAN_CHAIN.md`](ACP_LEAN_CHAIN.md)
