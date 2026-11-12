---
name: img-to-html-flow
description: >-
  Recria um mock de UI (imagem) como HTML + CSS + JS estáticos (sem framework),
  em etapas com aprovação do usuário: wireframe ASCII tipado com plano → fundo
  completo → componentes com fontes → assets restantes → revisão final. Variante local do
  img-to-html (rtadewald/skills @99d0b39) que gera os assets no ChatGPT (Plus) ou no Google
  Flow (AI Pro) pelo navegador integrado, sem OpenRouter. Use when the user mentions
  img-to-html-flow.
disable-model-invocation: true
---

# Img → HTML (ChatGPT / Flow)

> **Variante local.** Igual ao `img-to-html` original, exceto o **procedimento de assets**, que usa o
> ChatGPT (conta Plus) ou o Google Flow (Nano Banana, conta Google AI Pro) no navegador integrado em
> vez da OpenRouter, e os comandos de abrir arquivo, que são de Windows. O upload dos recortes é
> **do usuário** nos dois: o navegador integrado não lê arquivo local, e anexar por script é barrado
> pela política de permissões do Claude Code.
>
> ⚠️ **Sigilo:** recortes e prompts vão para a conta Google ou OpenAI. Nunca usar com tela de caso,
> print de extração ou qualquer material do acervo.

## O que é

Skill para transformar um **mock de interface** (PNG/JPG/WebP) numa **recriação HTML** fiel, passo a passo.

**Entrada:** uma imagem de referência (anexada no chat, path, ou URL). Se faltar, peça.

**Saída:** pasta `design-systems/<slug>/` com a referência copiada, o wireframe, o **`index.html`** e uma pasta **`assets/`** com o CSS, o JS e as mídias geradas.

O entrypoint final deve se chamar exatamente **`index.html`**. Não use outro nome para o HTML principal.

`<slug>` = nome curto do mock em kebab-case (ex.: `chatgpt-glass-dash`). Se o usuário não indicar, derive do nome do arquivo ou pergunte.

## Por que em etapas

Recriar a tela inteira de uma vez falha (cores, glass, ícones e fontes misturam erros). O fluxo é **bottom-up**: cada camada só começa depois da anterior **aprovada** pelo usuário. O wireframe define *o que* existe e seu plano indica *quando* e *como* implementar cada região. Assets entram conforme sua função: imagens que compõem o fundo são feitas junto dele.

## Pipeline

```
1. reference → $to-wireframe format=ascii → wireframe.txt + plano → [usuário aprova ambos]
2. fundo completo (CSS e/ou imagens)       → [usuário aprova]
3. estrutura e componentes + fontes       → [usuário aprova]
4. assets restantes (ícones, imagens etc.) → [usuário aprova, se houver]
5. revisão final integrada                → [usuário aprova]
```

## Gate de aprovação (vale para todas as etapas)

Ao terminar uma etapa:

1. Mostre o resultado (path + `start index.html` no Windows / `open` no macOS e/ou screenshot no browser).
2. Pergunte se está correto / se mudaria algo.
3. **Pare.** Não inicie a etapa seguinte.

Só avance com confirmação explícita ("aprovado", "pode seguir", "ok"). Se o usuário pedir correção: edite, mostre de novo, aguarde nova aprovação.

A aprovação do plano autoriza a sequência proposta, sem substituir os gates de implementação. Se não houver assets restantes, indique isso no plano e omita a etapa 4; depois da aprovação da etapa 3, siga para a revisão final.

## Layout da pasta

```
design-systems/<slug>/
  reference.[ext]      # cópia da imagem de entrada
  wireframe.txt        # planta tipada criada por $to-wireframe format=ascii; plano apresentado junto
  index.html           # markup — só estrutura, sem <style>/<script> inline
  assets/
    styles.css         # todo o CSS
    app.js             # todo o JS (só se o mock precisar de comportamento)
    crops/             # recortes da reference
    *.png / *.mp4 …    # imagens, ícones, vídeos gerados
```

### Stack: HTML + CSS + JS separados

**Sem build, sem bundler, sem framework, sem `node_modules`, sem dev server** — abre com duplo clique no `index.html` e funciona. (Para screenshot com Playwright, que bloqueia `file://`, servir a pasta com `python -m http.server <porta> --bind 127.0.0.1 --directory design-systems/<slug>`.)

- `index.html` carrega os outros dois: `<link rel="stylesheet" href="assets/styles.css">` no `<head>` e `<script src="assets/app.js" defer></script>`.
- **Nada de `<style>` ou `<script>` inline** no HTML, e nada de `style="…"` nos elementos. Todo CSS vive em `assets/styles.css`.
- Um `styles.css` só. Se ele passar de ~1500 linhas, aí sim quebre por região (`assets/nav.css`, `assets/cards.css`) e adicione os `<link>` correspondentes — mas o default é um arquivo.
- `assets/` é a única pasta auxiliar: CSS, JS, imagens, ícones, vídeos e os crops moram todos lá.
- Sem Tailwind, sem CDN de framework. CSS puro, com **custom properties** no `:root` para o design system (cores, radius, sombras, tipografia).
- Cada região do wireframe vira uma **classe CSS** (`.nav`, `.hero`, `.card`, `.card2`, …) e cada tag tipada vira uma classe utilitária (`.h1`, `.t2`, `.btn`, `.lnk`, …). Mesmo id no wireframe = mesma classe.
- Conteúdo repetido (lista de cards, itens de nav) é escrito direto no HTML. Só crie `app.js` se o mock exigir comportamento real; não gere markup por loop de JS.
- Paths sempre relativos: `assets/{id}.png`.

Se o usuário pedir React/Vite explicitamente, aí sim mude a stack.

---

## Etapa 1 — Wireframe ASCII tipado + plano

Objetivo: a **planta estrutural** da tela — quais regiões existem e que texto tem dentro delas — acompanhada de um plano curto de implementação por região.

O wireframe é o **contrato** com o HTML: cada região e cada tag tipada vira depois uma **classe CSS** (mesmo id = mesmo visual). A criação, o vocabulário tipado, o aninhamento e a revisão estrutural pertencem exclusivamente a [`$to-wireframe`](../to-wireframe/SKILL.md). Não replique essas regras nesta skill.

### Criar o wireframe

1. Criar `design-systems/<slug>/` e copiar a imagem para `reference.[ext]`.
2. Invocar a skill **`$to-wireframe`** com `format=ascii`, `image=design-systems/<slug>/reference.[ext]` e `output=design-systems/<slug>/wireframe.txt`.
3. Manter `wireframe.txt` como o contrato canônico desta execução. Não gerar SVG nesta etapa.
4. Não alterar o wireframe depois da entrega do `$to-wireframe`; qualquer correção estrutural volta para `$to-wireframe` com a mesma imagem e `format=ascii`.

### Plano de implementação (na mesma aprovação)

Depois de receber o ASCII do `$to-wireframe`, indique para cada região **a etapa de implementação e a técnica prevista**. Agrupe regiões iguais. Apresente o plano na mensagem, em uma tabela curta. Ele não é adicionado ao ASCII: etapas e técnicas não fazem parte dos ids/classes nem do texto da interface.

Exemplo de plano (adaptar à referência):

| Região / elemento | Etapa | Técnica prevista |
|-------------------|-------|------------------|
| Fundo da tela + arte decorativa | 2 | Gradiente CSS + ilustração transparente |
| Nav, hero e cards | 3 | HTML/CSS; família e peso definidos antes do ajuste fino |
| Fundo ilustrado de um card | 3 | Imagem + CSS, junto da superfície do card |
| Área de mídia | 3 / 4 | Estrutura na 3; imagem de conteúdo na 4 |
| Ícones e avatares | 4 | Assets gerados a partir dos recortes |
| Tela completa | 5 | Comparação integrada e correções finais |

Escolha visualmente entre **CSS, imagem ou composição dos dois**, considerando fidelidade, esforço e facilidade de ajustar posição/escala. Cores, gradientes e formas simples favorecem CSS; arte e texturas complexas favorecem imagem; camadas separadas ajudam quando precisam de ajustes independentes. Uma imagem de fundo única também é válida quando reproduz melhor a composição. Preserve textos e controles como HTML.

Classifique imagens pela **função**, não pelo formato: fundo da tela → etapa 2; fundo de componente → etapa 3; imagem de conteúdo, ícone ou avatar → etapa 4. Nenhuma superfície deve ser aprovada com parte essencial do seu fundo ainda pendente. Planejar esses assets na etapa 1 não significa recortá-los ou gerá-los ali.

Faça somente a revisão do plano: ele cobre todas as regiões do wireframe e distingue assets de fundo dos assets restantes? Depois mostre `wireframe.txt` junto do plano e aplique o **gate único para estrutura + sequência/técnicas propostas**.

---

## Etapa 2 — Fundo completo (CSS e/ou imagens)

Pré-requisito: wireframe e plano aprovados.

1. Criar `index.html` (esqueleto mínimo com o `<link>` para `assets/styles.css` e `<body>` vazio) e `assets/styles.css` (reset curto + `:root` com as custom properties que já der para definir).
2. Recriar o fundo completo com a técnica escolhida no plano: CSS, imagem única ou composição de camadas. Produzir agora as imagens necessárias, usando o procedimento de assets abaixo; não deixá-las para a etapa 4. Quando houver várias camadas independentes, peça todas ao Flow no mesmo lote (um envio por camada, ~45 s entre envios) e só componha o fundo depois que todas estiverem baixadas.
3. Sem navbar, cards ou conteúdo. O `<body>` pode receber elementos decorativos quando necessários para compor o fundo; também podem ser usados backgrounds CSS e pseudo-elementos.
4. Ajustar posição, escala, recorte, transparência e mistura entre camadas. Abrir o arquivo no browser e comparar o fundo composto com a referência.
5. **Gate.**

---

## Etapa 3 — Estrutura e componentes + fontes

Aqui entram a estrutura e os textos do wireframe (markup no `index.html`, estilo no `assets/styles.css`): primeiro o chrome (`nav` — top bar e/ou sidebar), depois cada tipo de card (`card`, `card2`, …) e as demais regiões. Imagens que compõem o fundo de um componente entram junto dele; as independentes usam o mesmo lote do procedimento de assets. Um gate só, no fim.

### Fontes antes do ajuste fino

1. Para cada tipo de tag distinto (`h1`…`t3`, `btn`, `lnk`, …), identificar **família + peso**. Se a skill/API local `find-font` estiver disponível, usar crop de uma linha com `text=` case-sensitive; caso contrário, escolher por julgamento visual a Google Font mais próxima e informar a aproximação.
2. Aplicar o `<link>` do Google Fonts no `index.html` ou `@font-face` no `styles.css`, com `font-family` / `font-weight` nas classes correspondentes. Mesmo id de tag = mesma tipografia.
3. Confirmar o carregamento das fontes antes de ajustar quebras de linha, dimensões e espaçamentos. Não adiar a escolha da família/peso para a revisão final.

Meta: cada superfície **indistinguível** da referência. Iterar medindo, não chutando:

- cores (eyedropper / sample de pixels na `reference`)
- gradientes (ângulo + stops)
- transparência (glass vs opaco)
- bordas / rim light (direção, soft vs hairline)
- glow / sombra externa e inset
- radius, padding, espaçamento entre elementos
- tipografia já aplicada (família/peso, tamanho, altura de linha e espaçamento)

Fluxo por superfície (nav primeiro, depois card a card):

1. Crop da referência (ou lab side-by-side no browser).
2. Amostrar pixels (fill, rim TL/BR, texto, meta).
3. Escrever o markup no `index.html` e a classe em `assets/styles.css`; valores reutilizados viram custom property no `:root`.
4. Screenshot recreate vs crop; ajustar até bater.

Somente os assets atribuídos à etapa 4 continuam como placeholders, com dimensões reservadas. Fundos e fontes dos componentes já devem estar completos. Com as regiões implementadas e comparadas → **gate**.

---

## Etapa 4 — Assets restantes

Implementar os `[ico:]` / `[img:]` / `[av:]` e demais assets que o plano deixou para esta etapa. Reutilizar os assets de fundo já aprovados; não regenerá-los apenas para cumprir esta etapa. Preparar todos os recortes da etapa, passar o upload ao usuário e gerar os assets em lote pelo procedimento abaixo; depois comparar o conjunto e apresentar o **gate**. Se não houver pendências, omitir esta etapa conforme o plano.

### Procedimento de assets (usado nas etapas 2, 3 e 4) — via ChatGPT ou Google Flow

Script local: `~/.agents/skills/img-to-html-flow/scripts/flow_assets.py` (rodar com `uv run`;
autocontido, só Pillow). Checagem: `uv run .../scripts/test_flow_assets.py` → `ok`.

**Antes de gerar, decidir por asset se ele vai a um gerador.** Os geradores redesenham: texto
miúdo vira garatuja e logotipo muda de forma, mesmo pedindo para não redesenhar. Por isso:

- **logo, wordmark, selo, qualquer coisa com texto** → não gerar; usar o recorte da `reference`
  direto (`crop`, e `key` se o fundo for liso);
- **ícone, avatar, ilustração, textura, foto, camada de fundo** → ChatGPT ou Flow.

**Qual gerador** (medido 21/10/2026, mesmo ícone e mesmo recorte de 512 px):

| | ChatGPT (Plus) | Flow (Nano Banana, AI Pro) |
|---|---|---|
| Fundo | **PNG com alfa real** (pedir "transparent background") | sem alfa: chroma `#00FF00` + `key` |
| Fidelidade ao recorte | alta (forma, porta em arco, espessura) | alta com recorte de 512 px |
| Saída | PNG RGBA 1254×1254, ~40 s | JPEG 1024×1024, ~30 s |
| Upload | usuário anexa na caixa do chat, **um por conversa** | usuário sobe ao projeto, **vários de uma vez** |
| Download | `fetch` do `blob:` da página | `fetch` da URL `=s0` |

- **Padrão: ChatGPT** para ícone, avatar e ilustração recortada (alfa real, nada a recortar).
- **Flow** para lote grande (um upload serve a vários pedidos), foto e camada de fundo sem
  transparência, ou quando a cota de imagens do Plus acabar.
- Seguir os passos 1 (recorte) e 5 (fundo e encaixe) nos dois. Os passos 2–4 abaixo são do Flow;
  os do ChatGPT estão em "Alternativa: ChatGPT", antes do passo 5.

#### 1. Recortes (local)

```bash
uv run ~/.agents/skills/img-to-html-flow/scripts/flow_assets.py crop \
  design-systems/<slug>/reference.png design-systems/<slug>/assets/crops/{id}.png \
  --bbox X Y W H --pad 4
```

Fazer todos os recortes do lote antes de qualquer geração. O `crop` **amplia para 512 px** no menor
lado (`--min 512`, padrão): recorte de ícone com ~34 px **falhou 2 de 2 vezes** como referência no
Flow ("technical issue with processing the reference image", sem cobrança), enquanto o mesmo
pedido sem referência passou de primeira. **Ampliados a 512 px, os recortes geraram 2 de 2 na
primeira tentativa**, fiéis à forma da referência (medido 21/10/2026). Sem referência a forma
sai genérica (telhado pontudo onde o original era arredondado).

#### 2. Abrir o Flow e passar o upload ao usuário (gate de upload)

1. Abrir o navegador integrado: `preview_start` com `url=https://labs.google/fx/tools/flow`. Se cair
   na tela de login, **parar** e pedir que o usuário entre. Credencial é dele.
2. Abrir (ou pedir) um projeto do Flow para este `<slug>`.
3. **Mostrar ao usuário a lista de caminhos dos recortes do lote** e pedir que ele os envie ao
   projeto (arrastar para a página ou "+" › enviar). O agente **não consegue** anexar arquivo: o
   seletor é do Windows, e `fetch` a `127.0.0.1`, colar imagem e `clipboard.read()` são bloqueados
   no navegador integrado.
4. Esperar a confirmação ("subi"), e então conferir na grade que cada recorte aparece, pelo
   `aria-label` dos `flow-grid-tile-container`. Anotar o nome que o Flow deu a cada um.

#### 3. Gerar (agente do Flow, chat)

Um envio por asset, com o prompt literal. Modelo: Nano Banana; **1 imagem por pedido**; proporção
do recorte (1:1 para ícone). Molde:

```text
Use EXACTLY this prompt, verbatim, without rewriting it. Generate 1 image with Nano Banana,
aspect ratio 1:1, using the uploaded image "<nome do recorte no Flow>" as the reference, and name
the result "<id>":
"Recreate this UI icon exactly as in the reference: same shape, stroke weight and color
<#hex medido>. Centered, filling about 70% of the frame. Flat, clean edges, no shadow, no
gradient, no text, no frame. Background: solid pure green #00FF00, perfectly uniform."
```

- ⚠️ O agente pode dizer "The icon has been generated" depois de uma **falha**. A verdade é a grade:
  tile com "Falha" no `innerText` não gerou.
- Ícone simples de traço também sai **sem referência** (prompt descrevendo a forma): é o plano B
  quando a referência falha, e dispensa o upload.
- Fundo de chroma: **verde `#00FF00`**; se o asset tiver verde, **magenta `#FF00FF`**. Para camada
  de fundo da tela ou foto, **sem** chroma: pedir a arte com o fundo que ela tem.
- Fundo completo a partir do mock: pedir só a arte de fundo, sem textos, cards ou controles.
- Adaptar o estilo à arte (foto, textura, 3D); não impor "flat" a tudo.
- ⚠️ **Mensagem enviada com o agente ainda respondendo é descartada em silêncio.** Esperar ~45 s
  entre envios e conferir a contagem na grade. Se o agente anunciar e não gerar, responder
  "yes, go ahead". "Algo deu errado" pode ser falha só do texto: olhar a grade antes de reenviar.
- Enviar: focar o `[contenteditable=true]`, digitar, `Return`, **um** clique só (o 2º clique com o
  agente ativo é o botão Parar).

#### 4. Baixar (sem menu)

Na própria página, um arquivo por chamada (`javascript_exec`), a imagem na resolução original:

```js
const tile = document.querySelector('flow-grid-tile-container[aria-label="<id>"]');
const src = tile.querySelector('img').src.replace(/=s\d+(-rw)?$/, '=s0'); // sem isso vem a miniatura WebP 512
const blob = await (await fetch(src, {credentials: 'include'})).blob();
const a = Object.assign(document.createElement('a'), {href: URL.createObjectURL(blob), download: '<id>.png'});
document.body.append(a); a.click(); a.remove();
blob.size
```

O navegador integrado grava em `~/Downloads` como `<uuid>.tmp` (às vezes com o nome pedido) e o
`.tmp` **pode sumir em segundos**. Antes de baixar, deixar um vigia em segundo plano que copia todo
arquivo novo para uma pasta de staging, e casar arquivo × asset pelo **tamanho em bytes** que o
`blob.size` devolveu:

```bash
mkdir -p design-systems/<slug>/assets/raw; touch /tmp/marca
while true; do find ~/Downloads -maxdepth 1 -type f -newer /tmp/marca -exec sh -c \
  'cp -n "$1" "design-systems/<slug>/assets/raw/$(stat -c %s "$1").bin"' _ {} \; ; sleep 0.3; done
```

Renomear `raw/<bytes>.bin` → `raw/{id}.jpg` (o original do Nano Banana veio **JPEG 1024×1024**;
conferir o magic `FF D8` / `89 50 4E 47`).
Parar o vigia ao fim do lote.

#### Alternativa: ChatGPT (passos 2–4 no lugar dos do Flow)

1. Abrir `https://chatgpt.com/` no navegador integrado (`preview_start` com `url`). Login é do
   usuário. Uma **conversa nova por asset**, para o anexo e o resultado não se misturarem.
2. **Gate de upload:** pedir ao usuário que anexe o recorte (`assets/crops/{id}-512.png`) na caixa
   do chat, **sem enviar**. Conferir o anexo: `img[alt="{nome do arquivo}"]` dentro do `form`.
   ⚠️ Não tentar pôr o arquivo no `input[type=file]` por script: o classificador de permissões
   bloqueia como vazamento de arquivo, e `fetch` a `127.0.0.1` falha na página.
3. Focar a caixa (`textbox "Pergunte ao ChatGPT"`), digitar, `Return`. Molde:

```text
Generate an image (use the image generation tool, do not answer with text only). Recreate the UI
icon in the attached image exactly: <forma descrita>, same shape and the same stroke weight,
stroke color <#hex medido>, no fill. Square 1:1, icon centered, filling about 70% of the canvas.
Flat, clean edges, no shadow, no gradient, no text, no frame. Output a PNG with a fully
TRANSPARENT background.
```

4. Esperar ~40 s: o texto da página mostra "Criando imagem N%" e termina em "Resposta concluída".
   A imagem gerada é `main img[alt^="Imagem 1 gerada"]`, com `src` em `blob:`.
5. Baixar com o vigia de `~/Downloads` ligado (o mesmo do passo 4 do Flow):

```js
const img = [...document.querySelectorAll('main img')].find(i => i.alt.startsWith('Imagem 1 gerada'));
const blob = await (await fetch(img.src)).blob();
const a = Object.assign(document.createElement('a'), {href: URL.createObjectURL(blob), download: '<id>.png'});
document.body.append(a); a.click(); a.remove();
blob.size  // casar com raw/<bytes>.bin
```

6. Renomear `raw/<bytes>.bin` → `raw/{id}.png` e seguir no passo 5. O `key` detecta a alfa e pula o
   chroma: só apara, repinta (`--tint`) e redimensiona.

- O ChatGPT também erra o hex: usar `--tint` em ícone de uma cor, como no Flow.

#### 5. Tirar o fundo e encaixar (local)

```bash
uv run ~/.agents/skills/img-to-html-flow/scripts/flow_assets.py key \
  design-systems/<slug>/assets/raw/{id}.png design-systems/<slug>/assets/{id}.png --size 96 96
uv run ~/.agents/skills/img-to-html-flow/scripts/flow_assets.py sheet \
  design-systems/<slug>/assets/raw/_sheet.png design-systems/<slug>/assets/*.png
```

- `key` pega a cor do fundo pelos cantos (ou `--key 00FF00`), gera a alfa com borda suave, tira
  o vazamento da cor na borda e apara. Se a imagem já tem alfa (ChatGPT), pula o chroma e a saída
  diz `alpha` em vez de `key=#...`. `--size` limita a 2–4× o tamanho de exibição.
- **Ícone de uma cor só: sempre `--tint <hex medido>`.** O Nano Banana não respeita hex: pedido
  `#645AB8`, entregou `#5862B3` (medido). O `--tint` repinta o desenho na cor exata e mantém a alfa.
  Ícone com duas cores (ex.: sino com ponto azul) fica sem `--tint`.
- Se sobrar halo, subir `--tol`; se comer o desenho, baixar. Conferir pela folha `sheet` (xadrez).
- Encaixar via `<img src="assets/{id}.png">` (ou `background-image`) e comparar com a ref.
- Asset que falhou: só ele volta ao passo 3, com o prompt ajustado e a restrição escrita em
  negativo ("NOT …"). Não regerar os que passaram.
- O gate é o da etapa que usa o asset, sem aprovação extra por arquivo.

---

## Etapa 5 — Revisão final integrada

1. Comparar uma screenshot da tela completa com a referência, no mesmo viewport, com fontes e assets carregados.
2. Conferir a cobertura do wireframe/plano e corrigir diferenças de integração: sobreposição de camadas, recortes, alinhamentos, quebras de linha e espaçamentos após a entrada dos assets.
3. Verificar paths relativos e os comportamentos implementados, se houver. Informar aproximações ou pendências reais.
4. Mostrar a tela completa e os arquivos finais → **Gate.** Esta etapa consolida o resultado; fontes e fundos já foram implementados nas etapas anteriores.

---

## Não fazer

- Pular gates ou "adiantar" várias etapas num único turno.
- Na etapa 1: medir, croppar, fazer OCR, desenhar arte, ou refinar o wireframe além da revisão única.
- Adiar imagens essenciais de fundo para a etapa 4, ou deixar a escolha de fontes para a revisão final.
- Inventar textos ilegíveis no wireframe.
- Desenhar caixa de componente sem label de região, ou achatar cards-filho em texto solto dentro do pai.
- Marcar nav ativo como `[lnk:]` (use `[btn:]` / variante).
- Tratar ícones/imagens com Lucide/placeholder "parecido" quando o plano pede asset gerado da ref.
- Escrever CSS inline (`<style>` no HTML ou `style="…"` no elemento) — todo estilo vai para `assets/styles.css`.
- Criar `package.json`, bundler, framework ou espalhar arquivos fora de `assets/`.
