# SourceCraft dual-remote / post-import helper.
# Preferred path for ANCAP: use SourceCraft UI Migrate existing + mirror sync
# (see docs/SOURCECRAFT_GITHUB_MIRROR.md). Use this script only when sync is OFF
# and you need explicit dual-push remotes.
#
# Prerequisites:
#   1. ~/.ssh/id_rsa.pub added in SourceCraft → Access → SSH keys
#   2. Repos already imported in SourceCraft (UI Import/Mirror)
#   3. ssh -T ssh://ssh.sourcecraft.dev succeeds
#
# Usage:
#   .\scripts\setup-sourcecraft-dual-remote.ps1 -OrgSlug YOUR_ORG -RepoSlug ancap -LocalPath C:\Users\drago\Desktop\ANCAP

param(
  [Parameter(Mandatory = $true)]
  [string]$OrgSlug,

  [string]$RepoSlug = "ancap",
  [string]$LocalPath = "",
  [string]$GitHubOwner = "ancapcloud",
  [switch]$UsePort443
)

$ErrorActionPreference = "Stop"
$hostPort = if ($UsePort443) { "ssh://ssh.sourcecraft.dev:443" } else { "ssh://ssh.sourcecraft.dev" }

function Test-SourceCraftAuth {
  Write-Host "Testing SourceCraft SSH..."
  $out = & ssh -o BatchMode=yes -T "ssh://ssh.sourcecraft.dev" 2>&1 | Out-String
  Write-Host $out
  if ($out -notmatch "successfully authenticated") {
    throw "SourceCraft SSH auth failed. Add ~/.ssh/id_rsa.pub in SourceCraft → Access → SSH keys, then retry."
  }
}

function Ensure-DualRemote {
  param([string]$Path, [string]$Slug)
  Push-Location $Path
  try {
    $scUrl = "$hostPort/$OrgSlug/$Slug.git"
    $ghUrl = "https://github.com/$GitHubOwner/$Slug.git"

    $remotes = @(git remote 2>$null)
    if ($remotes -notcontains "github") {
      $origin = (git remote get-url origin 2>$null)
      if ($origin) {
        git remote rename origin github
      } else {
        git remote add github $ghUrl
      }
    }
    if ($remotes -notcontains "sourcecraft") {
      git remote add sourcecraft $scUrl
    } else {
      git remote set-url sourcecraft $scUrl
    }

    if ((git remote) -notcontains "all") {
      git remote add all (git remote get-url github)
    }
    git remote set-url all (git remote get-url github)
    git remote set-url --add --push all (git remote get-url github) 2>$null
    git remote set-url --add --push all $scUrl 2>$null

    Write-Host "Remotes:"
    git remote -v
    Write-Host "NOTE: If SourceCraft mirror sync is ON, push only to github — SC updates automatically."
    Write-Host "Dual push (sync OFF only): git push all <branch>"
  } finally {
    Pop-Location
  }
}

Test-SourceCraftAuth
if (-not $LocalPath) { $LocalPath = (Get-Location).Path }
Ensure-DualRemote -Path $LocalPath -Slug $RepoSlug
