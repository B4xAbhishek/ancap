# Cursor Remote Control — Self-Hosted Worker (Windows workaround)

The message **"Waiting for self-hosted worker: No self-hosted workers are connected"** comes from **Cursor Remote Control**, not GitHub Actions. ANCAP CI uses `ubuntu-latest` only.

On Windows, the native Cursor agent worker often fails to start because of a `better-sqlite3` ABI mismatch (`NODE_MODULE_VERSION` 127 vs 137). Use one of the workarounds below.

## Quick checklist (Desktop)

1. Cursor **≥ 3.9.8** (Help → About).
2. Open **Agents Window** (not inline editor chat).
3. **Settings → Agents** → Remote Control **On**, Keep this computer awake **On**.
4. Privacy Mode must **not** be Legacy.
5. In Agents Window: `/remote-control` then send any follow-up message.
6. PC must stay online and awake.

If it still waits for a worker, use WSL (recommended) or the Windows ABI patch script.

## Option A — WSL worker (recommended)

Run from PowerShell:

```powershell
.\scripts\start-cursor-worker-wsl.ps1
```

Or manually inside WSL Ubuntu:

```bash
curl https://cursor.com/install -fsS | bash
agent login
mkdir -p ~/ancap && cd ~/ancap
git clone https://github.com/ancapcloud/ancap.git
cd ancap
agent worker start --verbose
```

Important:

- Clone the repo **inside WSL** (`~/ancap`), not under `/mnt/c/...`.
- Keep the WSL terminal open while using Remote Control from the phone.

## Option B — Windows ABI patch

If the worker crashes on startup with sqlite errors:

```powershell
.\scripts\fix-cursor-worker-sqlite.ps1
```

Then restart Cursor completely and retry `/remote-control`.

## Option C — Phone without local PC

Use a **Cloud Agent** in the Cursor iOS app (same account). No self-hosted worker required. Trade-off: no access to local Docker/secrets on your PC.

## Verify worker is running

In WSL or after patch:

```bash
agent worker start --verbose --label name=ancap-dev
```

You should see "connected" / heartbeat logs without sqlite crash.

## Related paths

- Windows worker logs: `%APPDATA%\Cursor\logs\*\exthost\anysphere.cursor-agent-worker\`
- Agent CLI versions: `%APPDATA%\Cursor\User\globalStorage\anysphere.cursor-agent-worker\`
