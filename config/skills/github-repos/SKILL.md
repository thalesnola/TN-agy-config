---
name: github-repos
description: Gerencia, inspeciona e sincroniza os repositórios privados do GitHub do usuário (local-user), mapeando seus caminhos locais e autenticação via gh CLI e MCP GitHub.
---

# Catálogo e Operação de Repositórios Privados do GitHub

Este skill guia o Antigravity na interação com os repositórios privados do usuário no GitHub (`owner: local-user`), mapeando cada repositório ao seu diretório local, propósito e ferramentas disponíveis.

## 1. Mapeamento de Repositórios

| Repositório Remoto | Caminho Local | Finalidade Principal | Antigravity Project |
|---|---|---|---|
| `local-user/AGY-CONFIG` | `%USERPROFILE%\AGY-CONFIG` | Ecossistema completo do Antigravity (Skills, Plugins, MCPs, Hooks, LLMs locais Ollama e Roteamento em Escada). | `AGY-CONFIG` |
| `local-user/antigravity-token-router` | `%USERPROFILE%\antigravity-token-router` | Roteamento em escada de modelos (Argon->Opus / Flash 3.8->Sonnet), preservação de contexto e workers Ollama no Antigravity. | `antigravity-token-router` |
| `local-user/claude-token-router` | `%USERPROFILE%\claude-token-router` | Roteador de modelos e economia de tokens, contingência e scripts auxiliares no Claude Code. | `claude-token-router` |
| `local-user/claude-config` | `%USERPROFILE%\.claude` | Configurações centrais, plugins, cache e ambientes do Claude Code. | `claude-config` |
| `local-user/acervo-conhecimento` | `C:\ACERVO` | Base de conhecimento, Segundo Cérebro, templates e ferramentas de investigação. | `ACERVO` |
| `local-user/opencode-investigativo` | `%USERPROFILE%\.config\opencode` | Agente investigativo local com OpenCode + Ollama 100% offline, RAG agentico e grafo de vínculos. | `opencode-investigativo` |
| `local-user/redacao-forense` | `C:\ACERVO\redacao-forense` | Metodologia universal, regras de redação forense e templates de IPJ para agentes IA. | `redacao-forense` |

## 2. Autenticação e Credenciais

- **GitHub CLI (`gh`)**: O usuário está autenticado na conta `local-user` via Git Credential Manager / keyring do Windows com os escopos `repo`, `read:org`, `gist`.
- **Git Nativo**: `git config --get credential.helper` utiliza `manager` (GCM). Comandos git (`git push`, `git pull`, `git fetch`) autenticam diretamente sem requerer senhas interativas.
- **MCP GitHub**: Configurado em `~/.gemini/config/mcp_config.json` e `~/.claude.json` utilizando a autenticação nativa do GitHub CLI (`gh auth`).

## 3. Diretrizes de Operação

1. **Inspeção de Estado**: Sempre verifique o status do git local (`git -C <dir> status -s -b`) antes de fazer commits ou modificações em lote.
2. **Segundo Cérebro e Dados Sensíveis**: NUNCA commitar nomes de casos, dados protegidos ou informações pessoais identificáveis nos repositórios.
3. **Sincronização**:
   ```powershell
   git -C "<caminho_local>" fetch origin
   git -C "<caminho_local>" status -s -b
   ```