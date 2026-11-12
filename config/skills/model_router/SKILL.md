---
name: model-router-ollama
description: Direciona o roteamento automático em escada (Cérebro: Argon -> Opus; Agentes Rápidos sem limite de arquivo: Flash 3.8 -> Sonnet; Executores Locais Ollama sob comando do Cérebro ou distribuídos pelos Agentes Rápidos).
---

# Roteador de Modelos em Escada & Economia de Tokens no Antigravity

Esta skill estabelece a arquitetura operacional de **Roteamento em Escada e Higiene de Contexto** no Google Antigravity.

> **Premissa Operacional:** O usuário é o único responsável pelo que decide inserir ou não na sessão de trabalho. Não há camada ou filtro automático de sigilo. O papel do agente é estritamente **analisar a complexidade e o volume da solicitação do usuário e distribuir a execução** entre as camadas adequadas.

---

## 1. Hierarquia em Escada de Modelos

1. **Camada 1 — Cérebro Orquestrador (em Escada: `Gemini 4 Argon` → `Claude Opus`):**
   - **1º Degrau:** `Gemini 4 Argon`
   - **2º Degrau:** `Claude Opus` (`Opus 5.5` / `Opus`)
   - **Papel:** Analisa a demanda, arquiteta as soluções, elabora o planejamento estratégico, decide trade-offs, redige a entrega final, edita diretamente até 2 arquivos conhecidos e **comanda/distribui tarefas aos agentes rápidos e modelos locais**.
   - **Proteção de Janela:** O Cérebro nunca lê > 3 arquivos brutos nem despeja logs extensos em sua própria janela.

2. **Camada 2 — Agentes Rápidos (em Escada: `Gemini 3.8 Flash` → `Claude Sonnet`):**
   - **1º Degrau:** `Gemini 3.8 Flash` (`Model: "flash"` via `invoke_subagent`)
   - **2º Degrau:** `Claude Sonnet` (`Sonnet 5.5` / `Sonnet`)
   - **Sem Limite de Tamanho de Arquivo:** Os Agentes Rápidos **não têm limite de tamanho de arquivo ou número de linhas**. Podem ler e processar arquivos, logs, CSVs ou módulos de qualquer extensão em seu contexto isolado e devolver apenas uma **síntese executiva limpa de 1 a 3 parágrafos** ao Cérebro.
   - **Distribuição aos Modelos Locais (sob demanda do Cérebro):** Os Agentes Rápidos **podem despachar subtarefas diretamente aos modelos locais do Ollama (Camada 3)** (`dsh-local`, `qwen-local`, `opencode-local`, MCP `ollama-router`), **desde que o Cérebro (`Argon` / `Opus`) demande expressamente essa distribuição**.

3. **Camada 3 — Executores Locais Ollama (Custo Zero de Crédito):**
   - Acionados diretamente pelo Cérebro ou distribuídos pelos Agentes Rápidos (`Flash 3.8` / `Sonnet`) sob demanda do Cérebro:
     - **`dsh-local` (`gpt-oss:20b` via DSH 0.2.0-rc.2):** 1 a 4 arquivos (~70 s), código e revisão de 2ª família local.
     - **`qwen-local` (`Qwen3-Coder-Next :NOTPL`, ~36 GB):** lote mecânico grande (≥ 5 arquivos num único prompt, piso 2–4 min, sem fatiar).
     - **`opencode-local` (`nemotron-3.5-lightning:30b-a3b`) + `LightRAG` (porta 9621):** consultas estruturadas a acervos e bases de dados locais.
     - **MCP `ollama-router` (`qwen3-coder:30b` e `qwen2.5-coder:7b`):** `ollama_refactor`, `ollama_code_review` e `ollama_worker_task`.
   - Todo resultado de modelo local é **não revisado por definição** e deve ser conferido antes de integrar.

---

## 2. Matriz Decisória de Distribuição

| Tipo de Demanda | Camada / Executor | Escada de Modelos | Regra Operacional / Saída |
|---|---|---|---|
| **Planejamento, arquitetura, trade-offs, redação e síntese final** | Camada 1 (Cérebro) | **1º `Gemini 4 Argon` → 2º `Claude Opus`** | Decisão de alto nível e comando de distribuição |
| **Varredura (> 3 arquivos) ou leitura de arquivos/logs de qualquer tamanho** | Camada 2 (Agentes Rápidos) | **1º `Gemini 3.8 Flash` → 2º `Claude Sonnet`** | **Sem limite de tamanho de arquivo**; retorna síntese de 1–3 parágrafos |
| **Coordenação e despacho para modelos locais** | Camada 2 → Camada 3 | **`Flash 3.8` / `Sonnet` → Ollama Local** | Permitido **sempre que o Cérebro demandar a distribuição** |
| **Código pequeno/médio (1–4 arq) ou revisão de 2ª família** | Camada 3 (`dsh-local` / MCP) | `gpt-oss:20b` / `qwen2.5-coder:7b` | Diff auditável e diagnóstico local (~70 s) |
| **Lote mecânico grande (≥ 5 arquivos)** | Camada 3 (`qwen-local` / MCP) | `Qwen3-Coder-Next :NOTPL` / `qwen3-coder:30b` | Lote inteiro num só prompt sem fatiamento |
| **Busca em bases indexadas e grafo de entidades** | Camada 3 (`opencode-local` / LightRAG) | `nemotron-3.5-lightning:30b-a3b` | Síntese e cruzamento local |

---

## 3. Ordem de Chaveamento de Contingência (Estouro de Tokens)

1. **Escada Entre Modelos:** Comutação imediata na escada do Cérebro (`Gemini 4 Argon` → `Claude Opus`) e na escada dos Agentes Rápidos (`Gemini 3.8 Flash` → `Claude Sonnet`).
2. **PLANO A (Contingência Primária) — OMNI ROUTE:** Proxy local (`http://localhost:20128/v1`) com Routing Combos `priority` e compressão RTK em erro HTTP 429.
3. **PLANO B (Contingência Secundária / Bunker Offline) — OLLAMA LOCAL:** Ativação da MCP `ollama-router`, `claude-local`, DSH, Qwen Code e OpenCode (execução estrita em série `OLLAMA_NUM_PARALLEL=1`, `CTX=32768`, `KV=q8_0`).
