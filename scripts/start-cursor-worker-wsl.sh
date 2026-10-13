#!/usr/bin/env bash
# Start Cursor self-hosted agent worker inside WSL (recommended Windows workaround).
set -euo pipefail

REPO_URL="${ANCAP_REPO_URL:-https://github.com/ancapcloud/ancap.git}"
WORK_DIR="${ANCAP_WSL_WORK_DIR:-$HOME/ancap/ancap}"

echo "==> Cursor WSL worker bootstrap"
echo "    work dir: $WORK_DIR"

if ! command -v agent >/dev/null 2>&1; then
  echo "==> Installing Cursor agent CLI..."
  curl https://cursor.com/install -fsS | bash
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! agent --version >/dev/null 2>&1; then
  echo "ERROR: agent CLI not found after install. Add ~/.local/bin to PATH." >&2
  exit 1
fi

mkdir -p "$(dirname "$WORK_DIR")"
if [ ! -d "$WORK_DIR/.git" ]; then
  echo "==> Cloning repo into WSL filesystem (not /mnt/c)..."
  git clone "$REPO_URL" "$WORK_DIR"
fi

cd "$WORK_DIR"
echo "==> Pull latest..."
git pull --ff-only || true

echo "==> Starting worker (Ctrl+C to stop)..."
exec agent worker start --verbose --label "name=ancap-wsl"
