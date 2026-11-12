# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, r"C:\ACERVO\Ferramentas")
import estilo_forense as ef

W = 1280
H = 900

# Paleta Okabe-Ito (acessível para daltonismo e escala de cinza) + Traços distintos (Norma Gráfica Regra 4)
COR_CEREBRO = ef.OKABE_ITO[0]     # #0072B2 Azul escuro - Camada 1 (Sólido, 2.4px)
COR_SUBAGENTE = ef.OKABE_ITO[5]   # #56B4E9 Azul claro - Camada 2 (Tracejado longo '8 3', 2.0px)
COR_LOCAL = ef.OKABE_ITO[2]       # #009E73 Verde - Camada 3 (Traço-ponto '8 3 2 3', 2.2px)
COR_CONTING = ef.OKABE_ITO[1]     # #E69F00 Âmbar - Contingência (Tracejado médio '5 3', 1.8px)
COR_GUARDA = ef.OKABE_ITO[3]      # #D55E00 Vermelho-alaranjado - Sigilo/Guarda (Pontilhado '2 2.5', 2.0px)

CATEGORIAS = {
    "camada1": ("Camada 1: Cérebro em Escada (Argon -> Opus)", "#eaf3f9", COR_CEREBRO, "", 2.4),
    "camada2": ("Camada 2: Agentes Rápidos (Flash 3.8 -> Sonnet)", "#eef8fd", COR_SUBAGENTE, "8 3", 2.0),
    "camada3": ("Camada 3: Executores Locais (Ollama)", "#eaf7f2", COR_LOCAL, "8 3 2 3", 2.2),
    "contingencia": ("Contingência (429 / Fim de Crédito)", "#fdf5e6", COR_CONTING, "5 3", 1.8),
    "guarda": ("Guarda de Sigilo & Restrição", "#fdede4", COR_GUARDA, "2 2.5", 2.0),
}


def legenda_custom(y, x=ef.MARGEM):
    out, cx = [f'<rect x="{x - 8}" y="{y - 16}" width="{{LW}}" height="26" rx="3" fill="{ef.PAINEL}" stroke="{ef.BORDA}"/>'], x
    for k, (rot, fill, stroke, dash, peso) in CATEGORIAS.items():
        d_attr = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<rect x="{cx}" y="{y - 10}" width="22" height="14" fill="{fill}" stroke="{stroke}" stroke-width="{peso}"{d_attr}/>')
        out.append(ef.t(cx + 28, y + 1, rot, 10.8))
        cx += 28 + ef.largura(rot, 10.8) + 20
    out[0] = out[0].replace("{LW}", str(round(cx - x)))
    return "\n".join(out)


def caixa(x, y, w, h, cat_key, titulo_txt, linhas_txt, badge=None):
    _, bg_header, cor_borda, dash, peso_borda = CATEGORIAS[cat_key]
    d_attr = f' stroke-dasharray="{dash}"' if dash else ""
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#ffffff" stroke="{cor_borda}" stroke-width="{peso_borda}"{d_attr}/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="4" fill="{bg_header}" stroke="{cor_borda}" stroke-width="1"/>',
        ef.t(x + 12, y + 20, titulo_txt, 11.8, "bold", cor="#1a2230"),
    ]
    if badge:
        bw = ef.largura(badge, 9.5) + 12
        bx = x + w - bw - 8
        out.append(f'<rect x="{bx}" y="{y + 6}" width="{bw}" height="18" rx="3" fill="{cor_borda}" stroke="none"/>')
        out.append(ef.t(bx + bw / 2, y + 18, badge, 9.5, "bold", cor="#ffffff", ancora="middle"))
    cy = y + 48
    for l_txt, peso, cor in linhas_txt:
        out.append(ef.t(x + 12, cy, l_txt, 10.6, peso, cor=cor))
        cy += 17
    return "\n".join(out)


def seta(x1, y1, x2, y2, cor="#4a5364", dash="", peso=1.8, rotulo=None, rx=None, ry=None, ancora="middle"):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ""
    out = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cor}" stroke-width="{peso}"{d_attr} marker-end="url(#arrow-{cor.lstrip("#")})"/>'
    ]
    if rotulo:
        tx = rx if rx is not None else (x1 + x2) / 2
        ty = ry if ry is not None else (y1 + y2) / 2 - 6
        out.append(ef.t(tx, ty, rotulo, 10.0, "bold", cor=cor, ancora=ancora))
    return "\n".join(out)


def seta_poli(pontos, cor="#4a5364", dash="", peso=1.8, rotulo=None, rx=None, ry=None, ancora="middle"):
    pts = " ".join(f"{x},{y}" for x, y in pontos)
    d_attr = f' stroke-dasharray="{dash}"' if dash else ""
    out = [
        f'<polyline points="{pts}" fill="none" stroke="{cor}" stroke-width="{peso}"{d_attr} marker-end="url(#arrow-{cor.lstrip("#")})"/>'
    ]
    if rotulo and rx is not None and ry is not None:
        out.append(ef.t(rx, ry, rotulo, 10.0, "bold", cor=cor, ancora=ancora))
    return "\n".join(out)


defs = []
for c in [COR_CEREBRO, COR_SUBAGENTE, COR_LOCAL, COR_CONTING, COR_GUARDA, "#4a5364"]:
    cid = c.lstrip("#")
    defs.append(
        f'<marker id="arrow-{cid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{c}"/></marker>'
    )

corpo = ['<defs>' + "".join(defs) + '</defs>', legenda_custom(92)]

# ZONA SUPERIOR: DOMÍNIO NUVEM & ESCADA DE COMANDO (y=120..375)
corpo.append(f'<rect x="30" y="120" width="1220" height="255" rx="6" fill="#f8fafc" stroke="{ef.BORDA}" stroke-width="1.2"/>')
corpo.append(ef.t(44, 140, "DOMÍNIO NUVEM — HIERARQUIA EM ESCADA (CÉREBRO: ARGON -> OPUS  |  AGENTES RÁPIDOS: FLASH 3.8 -> SONNET)", 11.5, "bold", cor="#4a5364"))
corpo.append(ef.t(1235, 140, "Repositório Multi-Máquina: github.com/local-user/antigravity-token-router", 10.5, "bold", cor=COR_CEREBRO, ancora="end"))

# Caixa 0: Hooks & Segundo Cérebro (x=45..295, w=250)
corpo.append(caixa(
    45, 155, 250, 205, "guarda",
    "0. Guarda & Segundo Cérebro",
    [
        ("Hooks Nativos (~/.gemini/config):", "bold", "#1a2230"),
        ("• SessionStart: perfil-maquina.py", "normal", "#1a2230"),
        ("• PreInvocation: consultar.py (Vault)", "normal", "#1a2230"),
        ("• PreToolUse: guardar.py (bloqueia PII)", "normal", "#1a2230"),
        ("• Stop: auditar.py (zero vazamento)", "normal", "#1a2230"),
        ("• Git Hook: instalar-hook-git.py", "normal", "#1a2230"),
        ("Grafo local: graphify query primeiro", "bold", COR_GUARDA),
        ("Regra: Evidência original intocável", "bold", COR_GUARDA),
    ],
    badge="PRE-FLIGHT"
))

# Caixa 1: Camada 1 - Cérebro Orquestrador em Escada (x=360..765, w=405)
corpo.append(caixa(
    360, 155, 405, 205, "camada1",
    "1. Cérebro em Escada (Decisão & Comando)",
    [
        ("Escada do Cérebro: 1º Gemini 4 Argon -> 2º Claude Opus", "bold", COR_CEREBRO),
        ("Exclusivo: Arquitetura, trade-offs, redacao-forense", "normal", "#1a2230"),
        ("Ação Direta: <= 2 arquivos conhecidos (edição rápida)", "normal", "#1a2230"),
        ("Comando Local: Demanda distribuição aos modelos locais", "bold", "#1a2230"),
        ("PROTEÇÃO DA JANELA DO CÉREBRO (Proibido ler direto):", "bold", COR_GUARDA),
        ("• Varredura > 3 arquivos brutos -> Delegar Camada 2", "normal", "#4a5364"),
        ("• Arquivos/logs volumosos -> Delegar Camada 2", "normal", "#4a5364"),
        ("• Acervo documental bruto -> Delegar Camada 2/3", "normal", "#4a5364"),
    ],
    badge="ARGON -> OPUS"
))

# Caixa 2: Camada 2 - Agentes Rápidos em Escada (x=870..1235, w=365)
corpo.append(caixa(
    870, 155, 365, 205, "camada2",
    "2. Agentes Rápidos em Escada",
    [
        ("Escada Rápida: 1º Gemini 3.8 Flash -> 2º Claude Sonnet", "bold", COR_CEREBRO),
        ("CAPACIDADE DE LEITURA: SEM LIMITE de tamanho de arquivo!", "bold", COR_LOCAL),
        ("• Lê arquivos, logs e CSVs de qualquer extensão/linhas", "normal", "#1a2230"),
        ("• Varre codebase (> 3 arquivos) e extrai anomalias", "normal", "#1a2230"),
        ("• Devolve síntese limpa (1-3 parágrafos) ao Cérebro", "normal", "#4a5364"),
        ("DISTRIBUIÇÃO PARA MODELOS LOCAIS (Camada 3):", "bold", COR_CEREBRO),
        ("• Pode distribuir tarefas ao Ollama local (DSH, Qwen,", "normal", "#1a2230"),
        ("  OpenCode) desde que o CÉREBRO demande a distribuição!", "bold", COR_GUARDA),
    ],
    badge="FLASH 3.8 -> SONNET"
))

# Setas da Zona Superior
corpo.append(seta(295, 255, 358, 255, COR_CEREBRO, peso=2.0, rotulo="Contexto", rx=326, ry=245))
corpo.append(seta(765, 215, 868, 215, COR_SUBAGENTE, dash="8 3", peso=2.0, rotulo="Delega + Demanda", rx=816, ry=204))
corpo.append(seta(868, 265, 765, 265, COR_CEREBRO, dash="4 2", peso=1.6, rotulo="Síntese 1-3 par.", rx=816, ry=282))

# Faixa central de roteamento e eixos de decisão (y=390..436)
corpo.append(f'<rect x="30" y="390" width="1220" height="46" rx="4" fill="#eef2f6" stroke="{ef.BORDA}" stroke-width="1"/>')
corpo.append(ef.t(44, 408, "PORTA DE DISTRIBUIÇÃO PARA MODELOS LOCAIS (ACIONADA PELO CÉREBRO OU DISTRIBUÍDA PELOS AGENTES RÁPIDOS SOB DEMANDA DO CÉREBRO)", 11.2, "bold", cor="#1a2230"))
corpo.append(ef.t(44, 426, "Hardware: workstation 16 (Core Ultra 9 285H | 64 GB DDR5 | RTX PRO 1000 8 GB)  |  Regra Ollama: OLLAMA_NUM_PARALLEL=1 (em série) | CTX=32768 | FLASH_ATTN=1 | KV=q8_0", 10.5, "normal", cor="#4a5364"))

# Duas entradas na Porta Local: 1) Direto do Cérebro (x=562) e 2) Distribuído pelos Agentes Rápidos sob demanda do Cérebro (x=1052)
corpo.append(seta_poli([(562, 360), (562, 388)], COR_CEREBRO, peso=2.2, rotulo="Despacho Direto do Cérebro", rx=554, ry=380, ancora="end"))
corpo.append(seta_poli([(1052, 360), (1052, 388)], COR_SUBAGENTE, dash="8 3", peso=2.2, rotulo="Agente Rápido distribui (sob demanda do Cérebro)", rx=1044, ry=380, ancora="end"))

# Setas saindo da Porta Local para os 4 executores locais
corpo.append(seta_poli([(168, 436), (168, 464)], COR_LOCAL, dash="8 3 2 3", peso=1.8, rotulo="1-4 arq / Revisão (~70s)", rx=176, ry=455, ancora="start"))
corpo.append(seta_poli([(468, 436), (468, 464)], COR_LOCAL, dash="8 3 2 3", peso=1.8, rotulo="Lote >= 5 arq (sem fatiar)", rx=476, ry=455, ancora="start"))
corpo.append(seta_poli([(775, 436), (775, 464)], COR_LOCAL, dash="8 3 2 3", peso=1.8, rotulo="Acervo / Entidades (~2m)", rx=783, ry=455, ancora="start"))
corpo.append(seta_poli([(1085, 436), (1085, 464)], COR_CONTING, dash="5 3", peso=1.8, rotulo="MCP Direta / HTTP 429", rx=1093, ry=455, ancora="start"))

# ZONA INFERIOR: DOMÍNIO LOCAL — BUNKER OLLAMA 0.34.x (y=467..742)
corpo.append(f'<rect x="30" y="467" width="1220" height="275" rx="6" fill="#f4fbf7" stroke="{COR_LOCAL}" stroke-width="1.5" stroke-dasharray="8 3 2 3"/>')
corpo.append(ef.t(44, 486, "DOMÍNIO LOCAL (CUSTO ZERO DE CRÉDITO — NENHUM DADO SAI DA MÁQUINA)", 11.5, "bold", cor=COR_LOCAL))
corpo.append(ef.t(1235, 486, "Regra de Ouro: Sempre o modelo completo instalado (nunca rebaixar; descarregar residentes com ollama stop)", 10.5, "bold", cor="#1a2230", ancora="end"))

# Caixa 3A: dsh-local
corpo.append(caixa(
    45, 497, 280, 188, "camada3",
    "3A. dsh-local (DSH 0.2.0-rc.2)",
    [
        ("Modelo: gpt-oss:20b", "bold", "#1a2230"),
        ("Split: 59% CPU / 41% GPU (CTX 32768)", "normal", "#4a5364"),
        ("Escopo: 1 a 4 arquivos (~70 s)", "normal", "#1a2230"),
        ("Uso 1: Código pequeno/médio sigiloso", "normal", "#1a2230"),
        ("Uso 2: Revisor de 2ª família local", "normal", "#1a2230"),
        ("Saída: Diff auditável (Cérebro/Rápido)", "bold", COR_LOCAL),
    ],
    badge="CAMADA 3"
))

# Caixa 3B: qwen-local
corpo.append(caixa(
    343, 497, 295, 188, "camada3",
    "3B. qwen-local (Qwen Code 0.24.7)",
    [
        ("Modelo: Qwen3-Coder-Next :NOTPL (~36 GB)", "bold", "#1a2230"),
        ("Split: 84% CPU / 16% GPU (UD-Q3_K_XL)", "normal", "#4a5364"),
        ("Escopo: Lote mecânico >= 5 arquivos", "normal", "#1a2230"),
        ("Piso: 2-4 min (~26k tokens preâmbulo)", "normal", "#1a2230"),
        ("Regra: Enviar lote inteiro num só prompt", "bold", "#1a2230"),
        ("BLOQUEIO: Modo yolo -> SEM MCP forense", "bold", COR_GUARDA),
    ],
    badge="LOTE YOLO"
))

# Caixa 3C: opencode-local + LightRAG + Forense
corpo.append(caixa(
    656, 497, 295, 188, "camada3",
    "3C. opencode-local & LightRAG",
    [
        ("Modelo: nemotron-3.5-lightning:30b-a3b", "bold", "#1a2230"),
        ("Agente: investigador (~2 min, 25 GB)", "normal", "#4a5364"),
        ("MCPs Exclusivos: rag + forense + LightRAG", "bold", "#1a2230"),
        ("Escopo: Busca semântica/exata, timeline,", "normal", "#1a2230"),
        ("  grafo de entidades (porta 9621)", "normal", "#1a2230"),
        ("Saída: Síntese + proveniência (custódia)", "bold", COR_LOCAL),
    ],
    badge="ACERVO"
))

# Caixa 3D / 4: Contingência & MCP ollama-router
corpo.append(caixa(
    969, 497, 266, 188, "contingencia",
    "4. Contingência & ollama-router",
    [
        ("MCP AGY: ollama_refactor (qwen3:30b)", "bold", "#1a2230"),
        ("MCP AGY: ollama_code_review (7b)", "normal", "#1a2230"),
        ("Plano A (AGY): OmniRoute + RTK", "bold", COR_CONTING),
        ("  (comutação priority em HTTP 429)", "normal", "#4a5364"),
        ("Plano B (Bunker): claude-local / MCP", "bold", COR_CONTING),
        ("  (hook StopFailure no fim de crédito)", "normal", "#4a5364"),
    ],
    badge="PLANO A/B"
))

# Barra de Revisão Obrigatória & Exclusão Mútua (y=695..731)
corpo.append(f'<rect x="45" y="695" width="1190" height="36" rx="4" fill="#fff8eb" stroke="{COR_CONTING}" stroke-width="1.8" stroke-dasharray="5 3"/>')
corpo.append(ef.t(60, 717, "GATE OBRIGATÓRIO DE CONSOLIDAÇÃO: Todo trabalho de executor local é NÃO REVISADO por definição -> Revisar diff/proveniência (revisar-trabalho-ollama.py / forense_custodia) antes de integrar.", 10.8, "bold", cor="#1a2230"))

# Faixa de Decisão Arquitetural Vigente (y=755..815)
corpo.append(f'<rect x="30" y="755" width="1220" height="60" rx="4" fill="{ef.PAINEL}" stroke="{ef.BORDA}" stroke-width="1"/>')
corpo.append(ef.t(44, 775, "REGRAS DE COMANDO EM ESCADA (ATUALIZADO EM 28/10/2026):", 11.2, "bold", cor="#1a2230"))
corpo.append(ef.t(405, 775, "1) Cérebro em Escada: Gemini 4 Argon -> Claude Opus.  2) Agentes Rápidos em Escada: Gemini 3.8 Flash -> Claude Sonnet (SEM limite de arquivo).", 10.8, "normal", cor="#1a2230"))
corpo.append(ef.t(44, 797, "3) Agentes Rápidos podem distribuir tarefas aos modelos locais quando o Cérebro demandar.  4) Exclusão mútua Ollama: Qwen Code (36 GB) e OpenCode (25 GB) nunca rodam juntos.", 10.8, "normal", cor="#4a5364"))

dados_Regras = {
    "arquitetura": "token-router-2.1.0-escada-argon-opus-flash38-sonnet",
    "data_decisao": "2026-10-28",
    "cerebro_escada": ["Gemini 4 Argon", "Claude Opus"],
    "rapidos_escada": ["Gemini 3.8 Flash", "Claude Sonnet"],
    "limite_arquivo_rapidos": "sem_limite",
    "distribuicao_local_por_rapidos": "permitida_sob_demanda_do_cerebro",
    "locais": ["dsh-local (gpt-oss:20b)", "qwen-local (Qwen3-Coder-Next:NOTPL)", "opencode-local (nemotron-3.5-lightning:30b-a3b)", "ollama-router (qwen3-coder:30b / 7b)"]
}

prov = {
    "fonte": "Segundo Cérebro (AGENTS.md, antigravity-token-router e claude-token-router)",
    "folhas": "Vault Canônica ACERVO",
    "dados_sha512": ef.sha512_curto(dados_Regras),
    "data": "28/10/2026",
}

rod_svg, _ = ef.rodape(prov, W, 832)
svg_str = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{ef.FONTE}">\n'
    f'<rect width="{W}" height="{H}" fill="{ef.FUNDO}"/>\n'
    + ef.t(ef.MARGEM, 42, "Hierarquia em Escada e Roteamento de Tokens (Argon -> Opus | Flash 3.8 -> Sonnet | Ollama Local)", 19.5, "bold") + "\n"
    + ef.t(ef.MARGEM, 62, "Cérebro: Argon -> Opus  |  Agentes Rápidos (sem limite de arquivo + despacho local sob demanda): Flash 3.8 -> Sonnet  |  Bunker: Ollama Local", 11.8, cor="#4a5364") + "\n"
    + "\n".join(corpo) + "\n"
    + rod_svg + "\n</svg>\n"
)

out_svg = r"%USERPROFILE%\.gemini\antigravity\brain\e88d271f-85ea-4c5a-89c1-8a2412043aeb\roteamento-tokens-agy.svg"
with open(out_svg, "w", encoding="utf-8") as f:
    f.write(svg_str)

erros_xml = ef.verificar(out_svg)
estilos_check = {k: ("#ffffff", v[2], v[3]) for k, v in CATEGORIAS.items()}
erros_pal = ef.verificar_paleta(estilos_check)
print("Erros verificar(svg):", len(erros_xml), erros_xml)
print("Erros verificar_paleta:", len(erros_pal), erros_pal)