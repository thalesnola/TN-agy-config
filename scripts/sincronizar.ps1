# Sincroniza alterações locais de ~/.gemini/config e ~/.gemini/antigravity de volta para o repositório AGY-CONFIG
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$UserHome = $env:USERPROFILE

Copy-Item "$UserHome\.gemini\config\AGENTS.md" "$RepoRoot\config\AGENTS.md" -Force
Copy-Item "$UserHome\.gemini\config\AGENTS.md" "$RepoRoot\AGENTS.md" -Force
Copy-Item "$UserHome\.gemini\config\config.json" "$RepoRoot\config\config.json" -Force
Copy-Item "$UserHome\.gemini\config\hooks.json" "$RepoRoot\config\hooks.json" -Force
Copy-Item "$UserHome\.gemini\config\mcp_config.json" "$RepoRoot\config\mcp_config.json" -Force
Copy-Item "$UserHome\.gemini\config\skills.json" "$RepoRoot\config\skills.json" -Force
Copy-Item "$UserHome\.gemini\config\hooks\agy_hooks.py" "$RepoRoot\config\hooks\agy_hooks.py" -Force
Copy-Item "$UserHome\.gemini\config\plugins\*" "$RepoRoot\config\plugins" -Recurse -Force
Copy-Item "$UserHome\.gemini\config\skills\*" "$RepoRoot\config\skills" -Recurse -Force
Copy-Item "$UserHome\.gemini\config\agents\*" "$RepoRoot\config\agents" -Recurse -Force
Copy-Item "$UserHome\.gemini\antigravity\mcp\*" "$RepoRoot\antigravity\mcp" -Recurse -Force
Copy-Item "$UserHome\.gemini\antigravity\ollama_router\*" "$RepoRoot\antigravity\ollama_router" -Recurse -Force

Get-ChildItem -Recurse -Force "$RepoRoot\config","$RepoRoot\antigravity" -Directory | Where-Object { $_.Name -eq ".git" -or $_.Name -eq "__pycache__" } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "[+] Repositório AGY-CONFIG sincronizado com o estado local!" -ForegroundColor Green