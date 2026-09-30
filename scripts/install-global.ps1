param(
  [ValidateSet("all","codex","claude","gemini")]
  [string]$Target = "all"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Skills = @("architecture-orchestrator","architecture-programming","site-regulation-research","concept-design-review","cad-bim-automation","drawing-qa","area-quantity-audit","presentation-review","architecture-red-team")
$Agents = @("architect-lead","site-code-researcher","design-critic","bim-automation-specialist","drawing-reviewer","quantity-auditor")

function Copy-Skills([string]$Dest,[string]$Backup) {
  New-Item -ItemType Directory -Force -Path $Dest,$Backup | Out-Null
  foreach ($Name in $Skills) {
    $D = Join-Path $Dest $Name
    if (Test-Path $D) { Copy-Item -Recurse $D (Join-Path $Backup $Name); Remove-Item -Recurse -Force $D }
    Copy-Item -Recurse (Join-Path $Root "skills\$Name") $D
  }
}
function Copy-Agents([string]$Src,[string]$Dest,[string]$Backup) {
  New-Item -ItemType Directory -Force -Path $Dest,$Backup | Out-Null
  foreach ($Name in $Agents) {
    $D = Join-Path $Dest "$Name.md"
    if (Test-Path $D) { Copy-Item $D (Join-Path $Backup "$Name.md") }
    Copy-Item (Join-Path $Src "$Name.md") $D -Force
  }
}
function Install-Codex {
  $HomeDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
  Copy-Skills (Join-Path $HomeDir "skills") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\skills")
  Write-Host "Codex: installed $($Skills.Count) skills."
}
function Install-Claude {
  $HomeDir = Join-Path $HOME ".claude"
  Copy-Skills (Join-Path $HomeDir "skills") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\skills")
  Copy-Agents (Join-Path $Root "providers\claude\agents") (Join-Path $HomeDir "agents") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\agents")
  Write-Host "Claude Code: installed skills + agents."
}
function Install-Gemini {
  $HomeDir = Join-Path $HOME ".gemini"
  Copy-Skills (Join-Path $HomeDir "skills") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\skills")
  Copy-Agents (Join-Path $Root "agents") (Join-Path $HomeDir "agents") (Join-Path $HomeDir "backups\architect-agent-superpowers-$Stamp\agents")
  Write-Host "Gemini CLI: installed skills + agents."
}

switch ($Target) {
  "codex" { Install-Codex }
  "claude" { Install-Claude }
  "gemini" { Install-Gemini }
  "all" { Install-Codex; Install-Claude; Install-Gemini }
}
Write-Host "Installation complete. Start a fresh agent session or reload provider capabilities before verification."
