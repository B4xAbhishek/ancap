# SourceCraft ↔ GitHub (Import / Mirror UI)

Official guide: https://sourcecraft.dev/portal/docs/en/sourcecraft/operations/migration

## Recommended for ANCAP

Use SourceCraft UI **Migrate existing** + **Activate synchronization** so GitHub stays the primary write target and SourceCraft auto-pulls branches. That gives you a second copy without fighting mirror branch locks.

If you need to **push commits into SourceCraft yourself** (true dual-write), import **without** synchronization, then add a `sourcecraft` remote and use `git push all`.

## UI steps (per repo)

1. Open https://sourcecraft.dev and sign in.
2. Left panel → **Create repository**.
3. Tab **Migrate existing**.
4. Source → **GitHub**.
5. Create a GitHub PAT (classic or fine-grained) with:
   - `repo` (list + read private/public repos)
   - `read:org` (optional; collaborators / LFS)
6. Paste PAT → **Authenticate**.
7. Owner: `ancapcloud`
8. Repository: pick one of:
   - `ancap` (main)
   - `assets`
   - `ancap-docs`
   - `Theodore`
   - `harem`
9. Under **Synchronization**:
   - **Mirror mode (recommended):** enable **Activate synchronization**, branches e.g. `master`, `main`, `release/*`
   - **Dual-write mode:** leave sync **off** (one-shot import only)
10. Create / start migration. Repeat for each repo.

## After mirror is live

- Day-to-day: keep pushing **GitHub** (`origin` / `github`). SourceCraft updates via sync.
- SSH key: `~/.ssh/id_rsa.pub` must be in SourceCraft → Access → SSH keys (already prepared locally; Host `sourcecraft` in `~/.ssh/config`).
- Clone URL shape: `ssh://ssh.sourcecraft.dev/<org_slug>/<repo_slug>.git`

## Optional: dual-push remotes (only if sync is OFF)

```powershell
cd C:\Users\drago\Desktop\ANCAP
.\scripts\setup-sourcecraft-dual-remote.ps1 -OrgSlug <YOUR_ORG> -RepoSlug ancap -LocalPath C:\Users\drago\Desktop\ANCAP
# then: git push all master
```

## Check SSH

```powershell
ssh -T ssh://ssh.sourcecraft.dev
# expect: Hi <user>! You've successfully authenticated...
```

## HTTPS + personal access token (PAT)

SourceCraft account for this workspace: user `andrew-ptichka`, repo `https://git.sourcecraft.dev/andrew-ptichka/ancap.git`.

1. Create PAT in SourceCraft → Access → Personal access tokens (copy once).
2. Store locally only (never commit): repo-root `.env.sourcecraft` → `SOURCECRAFT_TOKEN=pv1_...` (gitignored).
3. Auth check (API):

```powershell
$h = @{ Authorization = "Bearer $env:SOURCECRAFT_TOKEN" }
Invoke-RestMethod -Uri https://api.sourcecraft.tech/user -Headers $h
```

4. Git over HTTPS (password = PAT; username can be `x-access-token` or any label):

```powershell
git ls-remote https://x-access-token:$env:SOURCECRAFT_TOKEN@git.sourcecraft.dev/andrew-ptichka/ancap.git HEAD
```

### Mirror mode vs dual-write

If **Activate synchronization** is ON, SourceCraft rejects direct pushes to mirrored branches:

`branch policy prevent_all_changes violated (details: 'Cannot push to mirrored branches')`

That is expected. Day-to-day: `git push origin master` (GitHub); SourceCraft follows via sync. Do **not** force-push into a mirrored `master`.

If you need dual-write, turn sync **off** in the SourceCraft UI, then push to the `sourcecraft` remote.

### Lag check (mirror stuck behind GitHub)

As of 2026-09-11, GitHub `master` can be ahead while SourceCraft still shows an older SHA (e.g. GitHub `c5e2d06…`, SourceCraft stuck at `d6219f8…`). Direct push cannot fix that under mirror policy — even non-`master` refs were rejected with the same error.

```powershell
cd C:\Users\drago\Desktop\ANCAP
$gh = git rev-parse origin/master
$token = (Select-String -Path .env.sourcecraft -Pattern '^SOURCECRAFT_TOKEN=(.+)$').Matches[0].Groups[1].Value.Trim()
$sc = (git ls-remote "https://x-access-token:${token}@git.sourcecraft.dev/andrew-ptichka/ancap.git" refs/heads/master).Split("`t")[0]
"GitHub=$gh"
"SourceCraft=$sc"
if ($gh -ne $sc) { "LAG — open SourceCraft UI → repo → Sync / re-import, or disable Activate synchronization" }
```

Operator actions when lagging:
1. SourceCraft UI → `andrew-ptichka/ancap` → mirror / sync controls → **Sync now** (or re-run Migrate with sync ON).
2. Or disable **Activate synchronization**, then `git push sourcecraft master` (true dual-write).
3. Prefer (1) so GitHub remains the only write path.
