# GitHub MCP Server

Provides comprehensive integration with GitHub repositories, issues, PRs, file updates, commits, and searches using the authenticated GitHub API.

## Repositórios Privados do Usuário (`owner: local-user`):

1. **`local-user/acervo-conhecimento`**:
   - Descrição: Base de conhecimento, Segundo Cérebro, templates e ferramentas de inteligência da ACERVO.
   - Caminho local: `C:\ACERVO`
   - Branch padrão: `main`

2. **`local-user/opencode-investigativo`**:
   - Descrição: Agente investigativo local com OpenCode + Ollama, 100% offline. RAG agentico, grafo de vínculos e cadeia de custódia.
   - Caminho local: `%USERPROFILE%\.config\opencode`
   - Branch padrão: `main`

3. **`local-user/claude-token-router`**:
   - Descrição: Roteador inteligente de modelos, otimização de tokens e scripts de contingência.
   - Caminho local: `%USERPROFILE%\claude-token-router`
   - Branch padrão: `main`

4. **`local-user/claude-config`**:
   - Descrição: Configurações, plugins, histórico e ambientes do Claude Code.
   - Caminho local: `%USERPROFILE%\.claude`
   - Branch padrão: `main`

5. **`local-user/redacao-forense`**:
   - Descrição: Metodologia, regras universais, templates de IPJ e personalização de redação forense para agentes de IA.
   - Caminho local: `C:\ACERVO\redacao-forense`
   - Branch padrão: `main`

6. **`local-user/antigravity-token-router`**:
   - Descrição: Roteamento inteligente de modelos, preservação de contexto e economia de tokens no Antigravity (Gemini HIGH como Cérebro, Flash/Ollama como Workers).
   - Caminho local: `%USERPROFILE%\antigravity-token-router`
   - Branch padrão: `main`

## Diretrizes de Uso:
- Ao interagir com repositórios usando as ferramentas do servidor `github` (`get_file_contents`, `create_issue`, `search_code`, etc.), utilize o owner `local-user` e o nome do repositório correspondente.
- As credenciais estão vinculadas à chave de autenticação do GitHub CLI do usuário (`gh`).