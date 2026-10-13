# Deploy acp-node to an Oracle Cloud Always Free VM over SSH.
# NEVER commit the private key. Pass paths as parameters.
#
# Supports:
#   - Ampere A1 (aarch64): build on-box with Docker
#   - E2.1.Micro (x86_64): ship a prod linux/amd64 binary + slim runtime image
#
# Example (E2 Micro, already given Public IP):
#   .\scripts\deploy-oracle-acp-node.ps1 `
#     -HostIp 152.67.79.206 `
#     -KeyPath "$env:USERPROFILE\Downloads\ssh-key-2026-09-30.key" `
#     -User opc `
#     -Arch amd64 `
#     -BinaryPath "$env:TEMP\acp-oracle\acp-node"
#
# Example (Ampere when capacity exists):
#   .\scripts\deploy-oracle-acp-node.ps1 -HostIp <IP> -KeyPath <key> -User ubuntu -Arch arm64

param(
  [string]$HostIp = $env:ORACLE_ACP_HOST_IP,
  [Parameter(Mandatory = $true)][string]$KeyPath,
  [string]$User = "opc",
  [ValidateSet("amd64", "arm64")][string]$Arch = "amd64",
  # Prefer direct HTTP peer on primary (:18545) — Oracle binary historically lacked
  # reqwest TLS, and Cloudflare IPv6 from OCI is unreliable. Public HTTPS works after
  # rebuilding acp-node with reqwest rustls-tls.
  [string]$PeerRpc = "http://185.114.117.241:18545/rpc",
  [string]$RepoUrl = "https://github.com/ancapcloud/ancap.git",
  [string]$BinaryPath = ""
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($HostIp)) {
  throw "HostIp required (pass -HostIp or set ORACLE_ACP_HOST_IP to the OCI Primary VNIC Public IP)."
}
if (-not (Test-Path -LiteralPath $KeyPath)) {
  throw "SSH key not found: $KeyPath"
}

icacls $KeyPath /inheritance:r | Out-Null
icacls $KeyPath /grant:r "${env:USERNAME}:R" | Out-Null

$ssh = @(
  "-i", $KeyPath,
  "-o", "StrictHostKeyChecking=accept-new",
  "-o", "IdentitiesOnly=yes",
  "${User}@${HostIp}"
)

Write-Host "==> Probe SSH ${User}@${HostIp}"
& ssh @ssh "uname -m && free -h | head -n 2"

if ($Arch -eq "amd64") {
  if ([string]::IsNullOrWhiteSpace($BinaryPath) -or -not (Test-Path -LiteralPath $BinaryPath)) {
    throw "For -Arch amd64 pass -BinaryPath to a linux/amd64 acp-node binary (extract from prod container)."
  }
  Write-Host "==> Upload amd64 binary"
  & scp @("-i", $KeyPath, "-o", "IdentitiesOnly=yes", $BinaryPath, "${User}@${HostIp}:/tmp/acp-node")

  $remote = @"
set -euo pipefail
if ! command -v docker >/dev/null 2>&1; then
  sudo dnf install -y docker-ce docker-ce-cli containerd.io || sudo yum install -y docker || sudo apt-get install -y docker.io
  sudo systemctl enable --now docker
fi
if ! swapon --show | grep -q .; then
  sudo dd if=/dev/zero of=/swapfile bs=1M count=2048 status=none
  sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab >/dev/null
fi
sudo mkdir -p /opt/acp/bin /etc/acp /var/lib/acp-node /tmp/acp-build
sudo install -m 755 /tmp/acp-node /opt/acp/bin/acp-node
sudo cp /opt/acp/bin/acp-node /tmp/acp-build/acp-node
sudo tee /tmp/acp-build/Dockerfile >/dev/null <<'DF'
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/* && update-ca-certificates
COPY acp-node /usr/local/bin/acp-node
RUN chmod 755 /usr/local/bin/acp-node
ENTRYPOINT ["/usr/local/bin/acp-node"]
DF
sudo docker build -t ancap/acp-node:oracle /tmp/acp-build
if [ ! -f /etc/acp/acp-node.toml ]; then
  TOKEN=`$(openssl rand -hex 32)
  sudo tee /etc/acp/acp-node.toml >/dev/null <<TOML
role = "full"

[rpc]
listen = "0.0.0.0:8545"
token = "`$TOKEN"

[storage]
data_dir = "/var/lib/acp-node"

peer_rpc_urls = ["$PeerRpc"]
TOML
  echo "Generated RPC token (store offline): `$TOKEN"
fi
sudo chown -R ${User}:${User} /var/lib/acp-node || sudo chown -R ${User} /var/lib/acp-node
sudo docker rm -f acp-node 2>/dev/null || true
sudo docker run -d --name acp-node --restart unless-stopped \
  --memory=768m --memory-swap=2g \
  -v /etc/acp/acp-node.toml:/etc/acp/acp-node.toml:ro \
  -v /var/lib/acp-node:/var/lib/acp-node \
  -e RUST_LOG=info \
  -e ACP_DATA_DIR=/var/lib/acp-node \
  -e ACP_PEER_RPC_URLS=$PeerRpc \
  -e ACP_MINER_ENABLED=false \
  -p 8545:8545 -p 30333:30333 \
  ancap/acp-node:oracle --config /etc/acp/acp-node.toml
sleep 4
sudo docker ps --filter name=acp-node
curl -sS -X POST http://127.0.0.1:8545/rpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"getblockcount","params":[]}' || true
echo
uname -m
"@
  Write-Host "==> Remote amd64 bootstrap"
  $remote | & ssh @ssh "bash -s"
} else {
  $remote = @"
set -euo pipefail
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends ca-certificates curl git docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$User" || true
mkdir -p "`$HOME/ancap-src"
if [ ! -d "`$HOME/ancap-src/.git" ]; then
  git clone --depth 1 "$RepoUrl" "`$HOME/ancap-src"
else
  git -C "`$HOME/ancap-src" fetch --depth 1 origin master
  git -C "`$HOME/ancap-src" reset --hard origin/master
fi
cd "`$HOME/ancap-src/ACP-crypto"
sudo docker build -f acp-node/Dockerfile -t ancap/acp-node:arm64 .
sudo mkdir -p /var/lib/acp-node /etc/acp
if [ ! -f /etc/acp/acp-node.toml ]; then
  sudo tee /etc/acp/acp-node.toml >/dev/null <<TOML
role = "full"

[rpc]
listen = "0.0.0.0:8545"

[storage]
data_dir = "/var/lib/acp-node"

peer_rpc_urls = ["$PeerRpc"]
TOML
fi
sudo docker rm -f acp-node 2>/dev/null || true
sudo docker run -d --name acp-node --restart unless-stopped \
  -v /var/lib/acp-node:/var/lib/acp-node \
  -v /etc/acp/acp-node.toml:/etc/acp/acp-node.toml:ro \
  -e ACP_DATA_DIR=/var/lib/acp-node \
  -e ACP_PEER_RPC_URLS=$PeerRpc \
  -e ACP_MINER_ENABLED=false \
  -e ACP_RPC_LISTEN=0.0.0.0:8545 \
  -p 127.0.0.1:8545:8545 \
  -p 30333:30333 \
  ancap/acp-node:arm64
sleep 3
sudo docker ps --filter name=acp-node
curl -sS -X POST http://127.0.0.1:8545/rpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"getblockcount","params":[]}' || true
echo
uname -m
"@
  Write-Host "==> Remote ARM64 bootstrap"
  $remote | & ssh @ssh "bash -s"
}

Write-Host "Done. Public peer (rate-limit later via Cloudflare/nginx): http://${HostIp}:8545/rpc"
Write-Host "Update docs/ORACLE_CLOUD_ACP_NODE_PLAN.md with live evidence; prefer acp2.ancap.cloud once DNS/TLS is ready."
