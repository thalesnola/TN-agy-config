---
name: consulta-juridica
description: Consulta local de legislação federal brasileira (CF, códigos, leis, LCs, decretos-lei), súmulas (STJ, STF, vinculantes), temas de repercussão geral e repetitivos e Jurisprudência em Teses, e conferência das citações de uma peça (existe? está revogado/cancelado? o que diz?). Use ao redigir ou revisar informação policial, parecer ou peça com artigo, súmula ou tema citado, e sempre que precisar do texto literal de um dispositivo ou da tese de um precedente, em vez de citar de memória. Não serve para acórdão integral, decreto regulamentar, portaria, resolução nem jurisprudência de TJ/TRF.
---

# consulta-juridica

Camada fina sobre dois clones locais em `C:\LegalRef` (nada sai da máquina, tudo é dado público):
`lawcodex/` (legislação em Markdown, fonte Planalto) e `advocacia/` (súmulas, temas, teses em JSON).
Script: `scripts/juridico.py` (só biblioteca padrão). Rodar com `python -I`.

```
python -I scripts/juridico.py lei CP 121-A                 # texto literal do artigo
python -I scripts/juridico.py lei "lei 12850" 10-A         # lei por número; aceita lc 105, dl 2848
python -I scripts/juridico.py lei "lei 12965" --busca guarda registros   # artigos que contêm os termos
python -I scripts/juridico.py sumula stj 444               # stj | stf | sv
python -I scripts/juridico.py tema stf 990                 # stf | stj
python -I scripts/juridico.py busca compartilhamento dados fiscais     # súmulas, temas e teses; todos os termos
python -I scripts/juridico.py conferir peca.txt            # .txt, .pdf ou - (stdin); --json para máquina
python -X utf8 scripts/juridico.py conferir peca.pdf       # PDF: lê a camada de texto com `pdftotext -enc UTF-8` (sem o `-enc` o Windows devolve U+FFFD no lugar dos acentos); só se o texto vier vazio faz OCR local em memória (~1 s/página); sem -I, que esconde requests/pytesseract
python -X utf8 scripts/juridico.py pertinencia peca.pdf --saida C:\Casos\<caso>_Analise\conferencia.md   # pertinência + juízo de valor, modelo LOCAL
python -I scripts/juridico.py status                       # datas dos dados
```

Siglas: CP, CPP, CPM, CPPM, CF, CC, CPC, CLT, CTN, CDC, CTB, CE, ECA. Demais leis por número.

## Regras de uso

1. **Citar só o que a ferramenta devolveu**, com o link. O texto vem do Planalto compilado (redação vigente, riscados removidos), mas o `status` é indicativo e os dados são fotografia: a data vai em cada saída.
2. **Antes de citar em peça que sai da unidade, conferir na fonte oficial** (Planalto, STF, STJ). A ferramenta reduz a busca; não substitui a conferência. Informar ao usuário quando o dado tiver mais de ~30 dias (`status`).
3. **`conferir` prova existência e texto, não pertinência.** `[OK]` significa que o dispositivo ou precedente existe; se ele sustenta o que a peça afirma é leitura humana (e do `redacao-forense`). `[ATENCAO]` pede olhar: tribunal não informado, ano divergente, status diferente de ativa. `[NAO ACHEI]` pode ser erro de citação **ou** lacuna de cobertura: checar à mão antes de acusar erro.
4. A extração das citações é por regex. Citação fora do padrão ("art. cento e vinte e um") escapa. Sempre dizer isso quando relatar o resultado. Em PDF com OCR, `§` sai como `8` ou `81º` e ordinal pode errar: o conferidor trata `8 4º` como parágrafo e marca `[ATENCAO]` número ≥10 com `º`, mas ainda vale olhar o PDF nas marcadas. `[REVOGADO]` e `VETADO` podem ser menção histórica correta da peça: ler o contexto antes de dizer que há erro.
   - **Peça de caso: nunca colar o texto no contexto.** Rodar `conferir` direto no arquivo; a saída só traz o nome do diploma, o número e o texto da lei. Para depurar uma extração, mostrar o contexto com as palavras mascaradas, nunca o trecho cru.
5. **Fora da cobertura**: decretos regulamentares, portarias, resoluções (CNJ, CNMP), tratados, acórdão integral, TJ/TRF, jurisprudência posterior à data dos dados. Nesses casos a ferramenta diz que não cobre; consultar a fonte.
6. **Sigilo**: não gravar nesta pasta nem em consulta externa dado de caso. As buscas locais não saem da máquina; pesquisa em site de tribunal deve usar termos genéricos.
7. A CF repete o art. 5º no ADCT; a consulta devolve o corpo permanente.

## Pertinência e juízo de valor (`pertinencia`)

Para cada **uso** de cada citação (a mesma súmula citada duas vezes é avaliada duas vezes), um modelo **local** (Ollama, `gpt-oss:20b`; troque com `JURIDICO_MODELO`) lê a frase da peça e o texto literal do dispositivo, súmula ou tese, e devolve: o que a peça afirma, **veredito** (`sustenta`, `sustenta_em_parte`, `nao_sustenta`, `indeterminado`), **peso** do fundamento (`forte`, `razoavel`, `fraco`, `inadequado`), avaliação, ressalvas, sugestão de redação e, quando o fundamento é fraco, candidatos na base para apoiar melhor o ponto. Leva ~25 s por uso (17 usos ≈ 7 min); `ollama serve` precisa estar de pé.

Regras:
1. **Peça de caso: `--saida` obrigatório e eu não leio o relatório.** Ele reproduz trechos da peça. Gravar na pasta do caso (`C:\Casos\<caso>_Analise`), nunca em `C:\LegalRef`. A saída do terminal só traz contagens e os nomes das citações a olhar primeiro. `--stdout` só para texto sem dado de caso. O script recusa `JURIDICO_OLLAMA` fora de localhost e nunca sobrescreve um relatório existente.
2. **É triagem, não parecer, e erra nos dois sentidos.** Medido em texto sintético com falhas plantadas (gpt-oss:20b): pega o uso indevido de súmula e a afirmação absoluta sobre sigilo bancário; mas (a) julgava `nao_sustenta` a frase que misturava fatos do caso com a norma, corrigido pedindo que julgue só a proposição jurídica; e (b) **não pegou confusão de instituto** (o art. 69 do CP descreve concurso material e o modelo aceitou "concurso formal" mesmo em `JURIDICO_PENSAR=high`). Falta conhecimento ao modelo, não raciocínio. Num PDF real, 6 de 17 usos saíram `nao_sustenta` sem eu poder verificar quantos são acerto. Por isso: ler todo veredito diferente de `sustenta`, e **não tomar `sustenta` como aprovação** (o falso `sustenta` é o risco maior).
   - Melhorar exige medir contra a sua leitura: marque no relatório quais vereditos estavam certos e rodo a concordância sem ler o texto.
3. Modelos maiores (`nemotron-3.5-lightning:30b-a3b`) levaram 3 a 4 min por uso neste notebook: inviáveis para a peça inteira.

## Segunda opinião de modelo maior (só proposição abstrata, com revisão do usuário)

Fluxo, nesta ordem; nenhum passo envia nada à nuvem antes do 4:
1. `pertinencia peca.pdf --saida relatorio.md` (modelo local; relatório fica na pasta do caso).
2. `proposicoes relatorio.md --origem peca.pdf --saida proposicoes_para_revisao.md`: lista cada **proposição jurídica** (sem trecho da peça e sem o veredito local), com `[ ]` para marcar e `ALERTA` onde a checagem automática achou cara de dado de caso (valor, data, número solto, nome próprio ou sigla, CPF, telefone, e-mail, IP, via o `auditar.py` da vault).
3. **O usuário edita cada proposição até não restar fato do caso e marca `[x]` nas que podem ir.** Eu não leio esse arquivo.
4. `pacote proposicoes_para_revisao.md --saida pacote.md`: monta o pedido + só os itens `[x]` + o texto oficial público da norma. **Recusa o pacote inteiro (código 3) se qualquer item marcado ainda tiver alerta**, sem opção de forçar: o usuário reescreve.
5. Despacho a um modelo maior **por subagente** `token-router:*` (Opus não chama AGY nem Codex direto): AGY/Gemini (em 21/10 o `agy models` listou `gemini-4-argon-low/medium/high`; usado o `high`: 3m31s, 36 mil tokens de entrada e 18 mil de saída para 17 proposições) ou Codex (Astra só por pedido explícito). Peça a resposta como "não revisada" e conferir cada súmula/tema citado pelo modelo na base (`sumula`, `tema`) antes de usar: modelo grande também inventa número.

Lições do primeiro envio: o pacote de 41 KB estoura a linha de comando do Windows, então vai por `--input-format stream-json` via stdin; sem uma linha pedindo "não use ferramentas", o Gemini tentou rodar um script da vault local (negado pelo `agy` em modo headless): **o AGY carrega instruções que mandam consultar `C:\ACERVO`**, risco real se rodar interativo ou com permissão. O texto da norma que `texto_citado` entrega tinha a rubrica do artigo seguinte colada no fim ("Concurso formal" no art. 69 do CP), corrigido em `achar_artigo`; mesmo limpo, o modelo local continuou aceitando "concurso formal" para o art. 69, então o erro dele é de conhecimento.
A checagem é rede de segurança heurística; quem garante o sigilo é a revisão do passo 3. Testes: `tests/test_segunda_opiniao.py`.

## Atualização

Tarefa agendada `LegalRef-AtualizarJuridico` (segundas, 08:00; recupera se o notebook estava desligado): `C:\LegalRef\rotina\atualizar.py`.
Ela alinha os dois clones (`advocacia` e `lawcodex`, só se limpos) e recoleta no Planalto os diplomas de `rotina\watchlist.txt` (editável), gravando-os em `C:\LegalRef\atualizados\`, que a consulta prefere ao clone. Log em `C:\LegalRef\logs\atualizar-AAAA-MM.log`: `ALTEROU` marca texto de lei que mudou desde a coleta anterior. Rodar à mão: `python C:\LegalRef\rotina\atualizar.py`. `status` mostra as datas e avisa se o dado de lei passou de 14 dias.

Fora da watchlist vale o clone (coleta de 12/10). Súmulas, temas e teses só andam quando o upstream do advocacia publica (hoje: súmulas de julho). Para um diploma novo, acrescentar a linha na watchlist e rodar a rotina. `rotina\vendor` é cópia auditada dos scripts de coleta do LawCodex (com duas correções locais: página UTF-16 e travessão `&#150;`); não importar código do clone.

## Teste

`python -I tests/test_juridico.py` confere 19 citações reais (existente, inexistente, ano divergente, § não vira artigo, "n.º", LC 105 com ##, artigo vetado, "8 4º" do OCR).
