# ==============================================================================
# Instalador Completo Multi-Máquina: AGY-CONFIG (Windows PowerShell 5.1 / 7)
# Restaura 100% da configuração do Antigravity (Skills, Plugins, Hooks, MCPs,
# LLMs Locais Ollama, Perfis de Estação e Roteamento de Tokens em Escada)
# ==============================================================================

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Instalador Integral: AGY-CONFIG (Antigravity Full Ecosystem)    " -ForegroundColor Cyan
Write-Host "  Cérebro: Argon -> Opus | Rápidos: Flash 3.8 -> Sonnet | Ollama  " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$UserHome = $env:USERPROFILE
$UserHomeFwd = $UserHome -replace '\\', '/'
$UserHomeEsc = $UserHome -replace '\\', '\\'

$GeminiConfig = Join-Path $UserHome ".gemini\config"
$GeminiAgy    = Join-Path $UserHome ".gemini\antigravity"
$ClaudeHooks  = Join-Path $UserHome ".claude\hooks"

New-Item -ItemType Directory -Force -Path $GeminiConfig | Out-Null
New-Item -ItemType Directory -Force -Path $GeminiAgy | Out-Null
New-Item -ItemType Directory -Force -Path $ClaudeHooks | Out-Null

# 1. Copiar toda a árvore config/ para ~/.gemini/config
Copy-Item -Path (Join-Path $RepoRoot "config\*") -Destination $GeminiConfig -Recurse -Force
Write-Host "[+] ~/.gemini/config (AGENTS.md, config.json, hooks, 12 plugins, 97 skills, agents) instalado!" -ForegroundColor Green

# 2. Copiar scripts auxiliares de hooks para ~/.claude/hooks (caso ainda não existam)
if (Test-Path (Join-Path $RepoRoot "config\hooks\scripts")) {
    Copy-Item -Path (Join-Path $RepoRoot "config\hooks\scripts\*") -Destination $ClaudeHooks -Force
    Write-Host "[+] Scripts de ciclo de vida sincronizados em: $ClaudeHooks" -ForegroundColor Green
}

# 3. Copiar componentes de ~/.gemini/antigravity (mcp schemas, ollama_router, hooks GSD, mcp_config, settings)
Copy-Item -Path (Join-Path $RepoRoot "antigravity\*") -Destination $GeminiAgy -Recurse -Force
Write-Host "[+] ~/.gemini/antigravity (30 pastas de schemas MCP, servidor ollama_router, hooks GSD) instalado!" -ForegroundColor Green

# 4. Ajustar dinamicamente caminhos absolutos de usuário nos JSONs caso o nome do usuário mude na nova máquina
foreach ($jsonFile in @(
    (Join-Path $GeminiConfig "hooks.json"),
    (Join-Path $GeminiConfig "mcp_config.json"),
    (Join-Path $GeminiConfig "skills.json"),
    (Join-Path $GeminiConfig "hooks\agy_hooks.py"),
    (Join-Path $GeminiAgy "settings.json")
)) {
    if (Test-Path $jsonFile) {
        $raw = Get-Content $jsonFile -Raw -Encoding UTF8
        $raw = $raw.Replace("C:~", $UserHomeFwd).Replace("c:~", $UserHomeFwd)
        $raw = $raw.Replace("C:\\Users\\local-user", $UserHomeEsc).Replace("c:\\Users\\local-user", $UserHomeEsc)
        $raw = $raw.Replace("%USERPROFILE%", $UserHome).Replace("%USERPROFILE%", $UserHome)
        [System.IO.File]::WriteAllText($jsonFile, $raw, [System.Text.UTF8Encoding]::new($false))
    }
}
Write-Host "[+] Caminhos de usuário normalizados para: $UserHome" -ForegroundColor Green

# 5. Configurar variáveis de ambiente obrigatórias do Ollama Local (Escopo de Usuário)
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_PARALLEL", "1", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "32768", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_FLASH_ATTENTION", "1", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_KV_CACHE_TYPE", "q8_0", "User")
Write-Host "[+] Variáveis do Ollama (NUM_PARALLEL=1, CTX=32768, FLASH_ATTN=1, KV=q8_0) aplicadas!" -ForegroundColor Green

Write-Host "`nInstalação completa do AGY-CONFIG finalizada com sucesso!" -ForegroundColor Cyan