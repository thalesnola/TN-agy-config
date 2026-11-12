# Economia de Tokens, Escada de Agentes & Executores Locais (token-router no Antigravity)

Estas regras sincronizam o ecossistema `antigravity-token-router` com o Antigravity (AGY).

> **Premissa Operacional:** Não há camada ou filtro automático de sigilo. O usuário é o único responsável pelo que decide inserir ou não na sessão de trabalho. O papel do agente é estritamente **analisar a complexidade e o volume do comando e distribuir a execução** entre as camadas adequadas.

## 1. Hierarquia de Comando em Escada e Delegação

| Camada | Escada de Modelos | Executa & Regras Operacionais |
|---|---|---|
| **1. Cérebro Orquestrador** | **1º `Gemini 4 Argon`** → **2º `Claude Opus`** (`Opus 5.5`) | Analisa o pedido, planeja, arquiteta, decide trade-offs, redige entrega final, sintetiza e **comanda/distribui tarefas aos agentes rápidos e modelos locais**. Protegido contra leitura bruta (> 3 arquivos). |
| **2. Agentes Rápidos** | **1º `Gemini 3.8 Flash`** → **2º `Claude Sonnet`** (`Sonnet 5.5`) | **SEM LIMITE de tamanho de arquivo** (lê arquivos, logs e bases de qualquer extensão/linhas). Varre múltiplos arquivos (> 3 arquivos), devolve síntese limpa (1–3 parágrafos) e **pode despachar tarefas mecânicas aos modelos locais (Camada 3) sob demanda do Cérebro**. |
| **3. Executores Locais (Ollama)** | MCP `ollama-router`, `dsh-local`, `qwen-local`, `opencode-local` | Trabalho mecânico em lote, refatoração de boilerplate, revisão e consulta ao acervo indexado (`rag`/`forense`/`LightRAG`), acionados pelo Cérebro ou distribuídos pelos Agentes Rápidos. |

- **Sem limite de tamanho de arquivo na Camada 2:** Os Agentes Rápidos (`Flash 3.8` e `Sonnet`) processam arquivos de qualquer extensão ou volume sem restrição de linhas em seus contextos isolados, mantendo a janela do Cérebro (`Argon` / `Opus`) limpa e focada.
- **Distribuição pragmática aos modelos locais:** Sempre que o Cérebro (`Argon` / `Opus`) demandar a distribuição, os Agentes Rápidos (`Flash 3.8` / `Sonnet`) podem despachar subtarefas diretamente para `dsh-local`, `qwen-local`, `opencode-local` ou `ollama-router`, conferindo o resultado antes de devolver a síntese ao Cérebro.
- **Todo trabalho de modelo local é não revisado por definição:** sempre revise o diff/resultado antes de consolidar.

## 2. Perfil da Máquina: workstation Windows (e Multi-Estação)

- **Hardware (workstation 16):** Core Ultra 9 285H (16 núcleos, sem HT) · 64 GB DDR5-6400 · **RTX PRO 1000 8 GB** + Arc 140T + NPU.
- **Executores Locais (Ollama 0.34.x):**
  - **`dsh-local` (DeepSeek Harness 0.2.0-rc.2):** modelo **`gpt-oss:20b`** (59% CPU / 41% GPU, contexto 32768). Tarefa de 1–4 arquivos (~70 s) e revisão de segunda família local.
  - **`qwen-local` (Qwen Code 0.24.7):** modelo **`hf.co/unsloth/Qwen3-Coder-Next-GGUF:UD-Q3_K_XL` (`:NOTPL`)** (~36 GB, 84% CPU / 16% GPU). Piso de 2–4 min por chamada (~26k tokens de preâmbulo) — **nunca fatie**, despache o lote inteiro (≥ 5 arquivos).
  - **`opencode-local` (OpenCode 1.18.33, agente `investigador`):** modelo **`nemotron-3.5-lightning:30b-a3b`** (~2 min, MCPs `rag` + `forense`). Consulta estruturada a bases ingeridas.
  - **Contingência (`claude-local` / `ollama-router`):** **`qwen3-coder:30b`** e **`qwen2.5-coder:7b`**.
- **Regras de Operação do Ollama:**
  - **Sempre o modelo mais completo instalado, nunca o reserva:** se faltar VRAM (< 13 GB livres), descarregue modelos residentes (`ollama stop <modelo>`) e mantenha o modelo principal (o Ollama divide camadas com a CPU).
  - **Em série, nunca em paralelo (`OLLAMA_NUM_PARALLEL=1`):** nunca rode dois pesos grandes ao mesmo tempo (Qwen Code e OpenCode grande são mutuamente exclusivos).
  - **Variáveis obrigatórias:** `OLLAMA_CONTEXT_LENGTH=32768`, `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q8_0`. Nunca `num_gpu: 0` (prefill cai 7×). `num_thread` no padrão.

## 3. Graphify e Higiene de Contexto

- Existindo `graphify-out/graph.json`, consulte `graphify query "<pergunta>"` antes de ler arquivos; leia apenas os arquivos apontados pelo grafo.
- Console não recebe despejo bruto: imprima contagens e conclusões, gravando detalhes extensos em arquivo.
- No Windows o terminal abre no **PowerShell 5.1**, onde `&&` **não existe** (erro de parser). Use `;` entre comandos ou chame `pwsh`, e prefira `git -C <dir>` no lugar de `cd`.
