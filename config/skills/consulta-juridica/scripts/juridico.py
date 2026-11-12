#!/usr/bin/env python3
"""Consulta e conferência de citações jurídicas sobre dois clones locais:
LawCodex/br (legislação federal em Markdown) e advocacia-aberta (súmulas, temas, teses em JSON).
Só biblioteca padrão. Nada sai da máquina."""
import argparse, json, os, re, sys, unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("JURIDICO_ROOT") or Path(__file__).resolve().parents[3])
LEIS = ROOT / "lawcodex"
OVERLAY = ROOT / "atualizados"  # versões mais novas gravadas pela rotina semanal; o clone fica intocado
DATA = ROOT / "advocacia" / "ferramentas" / "pesquisa" / "vade-mecum" / "data"

CODIGOS = {
    "CP": "codigos/codigo-penal-del-2848-1940.md",
    "CPP": "codigos/codigo-de-processo-penal-del-3689-1941.md",
    "CPM": "codigos/codigo-penal-militar-del-1001-1969.md",
    "CPPM": "codigos/codigo-de-processo-penal-militar-del-1002-1969.md",
    "CF": "constituicao/constituicao-1988.md",
    "CC": "codigos/codigo-civil-lei-10406-2002.md",
    "CPC": "codigos/codigo-de-processo-civil-lei-13105-2015.md",
    "CLT": "codigos/consolidacao-das-leis-do-trabalho-clt-del-5452-1943.md",
    "CTN": "codigos/codigo-tributario-nacional-lei-5172-1966.md",
    "CDC": "codigos/codigo-de-defesa-do-consumidor-lei-8078-1990.md",
    "CTB": "codigos/codigo-de-transito-brasileiro-lei-9503-1997.md",
    "CE": "codigos/codigo-eleitoral-lei-4737-1965.md",
    "ECA": "codigos/estatuto-da-crianca-e-do-adolescente-lei-8069-1990.md",
}
SIGLAS_TEXTO = {"CRFB": "CF", "CF/88": "CF", "LGPD": "lei:13709"}
NOMES = {  # nome por extenso (sem acento, minúsculo) -> sigla ou lei:N
    "codigo penal militar": "CPM", "codigo de processo penal militar": "CPPM",
    "codigo de processo penal": "CPP", "codigo penal": "CP",
    "codigo de processo civil": "CPC", "codigo civil": "CC",
    "codigo tributario nacional": "CTN", "codigo de defesa do consumidor": "CDC",
    "constituicao federal": "CF", "constituicao da republica": "CF",
    "lei de drogas": "lei:11343", "marco civil da internet": "lei:12965",
    "lei de lavagem de dinheiro": "lei:9613", "lei de lavagem": "lei:9613",
    "lei de organizacao criminosa": "lei:12850", "lei de organizacoes criminosas": "lei:12850",
    "lei das organizacoes criminosas": "lei:12850", "lei maria da penha": "lei:11340",
    "lei de execucao penal": "lei:7210", "lei de interceptacao telefonica": "lei:9296",
    "lei geral de protecao de dados": "lei:13709",
}
TIPOS = {"lei": ("leis", "lei"), "lc": ("leis-complementares", "lcp"), "dl": ("decretos-lei", "del")}

ART_START = re.compile(r"^(?:#{1,6}\s*|\*\*)Art\.?\s*(\d+(?:\.\d{3})*)\s*[º°o]?\s*(?:-\s*([A-Za-z]))?\b")  # nível do # varia (LC 105 usa ##)
MAX_LINHAS = 60
RUBRICA = re.compile(r"[A-ZÀ-Ý][^.:;§\d]{2,70}")  # linha curta, sem pontuação final nem número: título, não dispositivo


def fold(s):  # tira acento e caixa preservando o comprimento (posições batem com o original)
    return "".join(unicodedata.normalize("NFD", c)[0].lower() for c in s)


def chave_art(num, suf=None):
    return num.replace(".", "") + (("-" + suf.lower()) if suf else "")


def ano4(a):
    if not a:
        return None
    if len(a) == 3 or (len(a) == 4 and a[:2] not in ("19", "20")):
        a = a[:2]  # número de nota de rodapé colado ao ano: "/063" é 06 + nota 3
    a = int(a)
    return a if a > 99 else (1900 + a if a >= 30 else 2000 + a)


# ---------- legislação ----------
def efetivo(p):
    """Versão mais recente do arquivo: overlay da rotina se existir, senão o clone."""
    o = OVERLAY / p.relative_to(LEIS) if p.is_relative_to(LEIS) else None
    return o if o and o.exists() else p


def resolver_lei(ref, ano=None):
    """ref: 'CP', 'lei:12850', 'lc:105', 'dl:2848'. Devolve (Path|None, nota)."""
    ref = ref.strip()
    if ref.upper() in CODIGOS:
        p = LEIS / CODIGOS[ref.upper()]
        return (efetivo(p) if p.exists() else None), ""
    tipo, _, num = ref.partition(":")
    if tipo not in TIPOS:
        return None, ""
    pasta, pref = TIPOS[tipo]
    cand = sorted(LEIS.glob(f"{pasta}/*/{pref}-{num}-*.md"))
    if tipo in ("lei", "dl"):  # os códigos saem de leis/ e decretos-lei/
        cand += sorted(LEIS.glob(f"codigos/*-{pref}-{num}-*.md"))
    if not cand:
        return None, ""
    if ano:
        certo = [c for c in cand if c.stem.endswith(f"-{ano}")]
        if certo:
            return efetivo(certo[0]), ""
        return efetivo(cand[0]), f"ano divergente: o diploma {num} é de {cand[0].stem.rsplit('-', 1)[1]}, não de {ano}"
    return efetivo(cand[0]), ""


def parse_ref_lei(s):
    s = s.strip()
    if s.upper() in CODIGOS or s.lower().startswith(("lei:", "lc:", "dl:")):
        return s, None
    m = re.match(r"(?i)(lei complementar|lc|lei|decreto[- ]lei|dl)\s*(?:n[º°o]?\.?\s*)?([\d\.]+)(?:/(\d+))?$", s)
    if not m:
        return None, None
    t = m.group(1).lower()
    tipo = "lc" if t in ("lei complementar", "lc") else ("lei" if t == "lei" else "dl")
    return f"{tipo}:{m.group(2).replace('.', '')}", ano4(m.group(3))


def frontmatter(linhas):
    meta = {}
    if linhas and linhas[0].strip() == "---":
        for l in linhas[1:]:
            if l.strip() == "---":
                break
            k, _, v = l.partition(":")
            meta[k.strip()] = v.strip().strip('"')
    return meta


def ler_lei(path):
    linhas = path.read_text(encoding="utf-8").splitlines()
    return linhas, frontmatter(linhas)


def achar_artigo(linhas, key):
    """Primeira ocorrência (a CF repete o art. 5 no ADCT: vale o corpo permanente)."""
    for i, l in enumerate(linhas):
        m = ART_START.match(l)
        if m and chave_art(m.group(1), m.group(2)) == key:
            fim = i + 1
            while fim < len(linhas) and not ART_START.match(linhas[fim]) and not linhas[fim].startswith("#"):
                fim += 1
            corpo = [x for x in linhas[i:fim] if x.strip()]
            # o LawCodex deixa a rubrica do artigo SEGUINTE ("Concurso formal") como último parágrafo deste: não é texto da norma
            while len(corpo) > 1 and RUBRICA.fullmatch(corpo[-1].strip()) and len(corpo[-1].split()) <= 8:
                corpo.pop()
            return i, corpo
    return None, None


def cmd_lei(args):
    ref, ano = parse_ref_lei(args.lei)
    path, nota = resolver_lei(ref, ano) if ref else (None, "")
    if not path:
        print(f"[NAO ACHEI] diploma '{args.lei}' (cobertura: federal, ver README do LawCodex)")
        return 1
    linhas, meta = ler_lei(path)
    if args.busca:
        termos = [fold(t) for t in args.busca]
        n = 0
        for i, l in enumerate(linhas):
            if ART_START.match(l):
                _, corpo = achar_artigo(linhas, chave_art(*ART_START.match(l).groups()))
                if corpo and all(t in fold(" ".join(corpo)) for t in termos):
                    print(f"{' '.join(x.lstrip('#* ').strip() for x in corpo)[:110]}  (linha {i + 1})")
                    n += 1
        print(f"-- {n} artigo(s) em {meta.get('title', path.stem)}")
        return 0 if n else 1
    m = re.match(r"(\d+(?:\.\d{3})*)\s*[º°]?\s*(?:-\s*([A-Za-z]))?$", args.artigo.strip())
    if not m:
        print("artigo inválido; exemplos: 121, 121-A, 1.228, 5º")
        return 2
    i, corpo = achar_artigo(linhas, chave_art(*m.groups()))
    if corpo is None:
        print(f"[NAO ACHEI] art. {args.artigo} em {meta.get('title', path.stem)}")
        return 1
    print(f"{meta.get('title', path.stem)}   [{path.name}:{i + 1}]")
    if nota:
        print(f"[ATENCAO] {nota}")
    for l in corpo[:MAX_LINHAS]:
        print(l.lstrip("# ").strip())
    if len(corpo) > MAX_LINHAS:
        print(f"[truncado: {len(corpo)} linhas; ver {path}:{i + 1}]")
    print(f"-- status LawCodex: {meta.get('status', '?')} (indicativo) | coletado {meta.get('retrieved', '?')} | {meta.get('source', '')}")
    print("-- conferir no Planalto antes de citar")
    return 0


# ---------- jurisprudência ----------
_cache = {}


def carregar(arq, chave):
    if (arq, chave) not in _cache:
        d = json.loads((DATA / arq).read_text(encoding="utf-8"))
        c = d[chave]
        itens = list(c.values()) if isinstance(c, dict) else c
        _cache[(arq, chave)] = (d.get("_meta", {}), itens)
    return _cache[(arq, chave)]


FONTES_SUM = {"stj": "sumulas_stj.json", "stf": "sumulas_stf.json", "sv": "sumulas_vinculantes.json"}
FONTES_TEMA = {"stf": ("temas_rg_stf.json", "temas"), "stj": ("flash_temas_stj.json", "temas")}
NOME_SUM = {"stj": "Súmula STJ", "stf": "Súmula STF", "sv": "Súmula Vinculante"}


def achar_sumula(trib, num):
    meta, itens = carregar(FONTES_SUM[trib], "sumulas")
    return next((x for x in itens if str(x.get("numero")) == str(num)), None), meta


def achar_tema(trib, num):
    arq, chave = FONTES_TEMA[trib]
    meta, itens = carregar(arq, chave)
    return next((x for x in itens if str(x.get("numero")) == str(num)), None), meta


def link(v):
    if isinstance(v, str) and v.startswith("{"):
        try:
            import ast
            v = ast.literal_eval(v)
        except Exception:
            return v[:100]
    return (v.get("paginaTema") or v.get("pagina") or "") if isinstance(v, dict) else (v or "")


def fmt_sumula(trib, x):
    return f"{NOME_SUM[trib]} {x['numero']} [{x.get('status', '?')}] ({x.get('data', '')}): {x.get('enunciado', '')}\n   {x.get('url', '')}"


def fmt_tema(trib, x):
    if trib == "stf":
        return (f"Tema {x['numero']} STF [{x.get('situacao', '?')}] {x.get('leadingCase', '')}: {x.get('titulo', '')}\n"
                f"   Tese: {x.get('tese') or '(sem tese fixada)'}\n   {link(x.get('links'))}")
    return (f"Tema {x['numero']} STJ [{x.get('situacao', '?')}] {x.get('processo', '')}: {x.get('questao', '')}\n"
            f"   Tese: {x.get('teseFirmada') or '(sem tese firmada)'}\n   {link(x.get('links'))}")


def cmd_sumula(args):
    x, _ = achar_sumula(args.tribunal, args.numero)
    print(fmt_sumula(args.tribunal, x) if x else f"[NAO ACHEI] {NOME_SUM[args.tribunal]} {args.numero}")
    print("-- conferir no tribunal antes de citar")
    return 0 if x else 1


def cmd_tema(args):
    x, _ = achar_tema(args.tribunal, args.numero)
    print(fmt_tema(args.tribunal, x) if x else f"[NAO ACHEI] Tema {args.numero} {args.tribunal.upper()}")
    print("-- conferir no tribunal antes de citar")
    return 0 if x else 1


def buscar_jur(termos_brutos):
    """Súmulas, temas e teses cujo texto contém todos os termos (sem acento). Devolve linhas já formatadas."""
    termos = [fold(t) for t in termos_brutos]
    achados = []
    for trib in FONTES_SUM:
        for x in carregar(FONTES_SUM[trib], "sumulas")[1]:
            if all(t in fold(x.get("enunciado", "")) for t in termos):
                achados.append(fmt_sumula(trib, x))
    for trib, (arq, ch) in FONTES_TEMA.items():
        for x in carregar(arq, ch)[1]:
            txt = " ".join(str(x.get(k) or "") for k in ("titulo", "tese", "questao", "teseFirmada"))
            if all(t in fold(txt) for t in termos):
                achados.append(fmt_tema(trib, x))
    for x in carregar("jt_stj.json", "teses")[1]:
        if all(t in fold(x.get("enunciado", "")) for t in termos):
            achados.append(f"Jurisprudência em Teses STJ ed. {x.get('edicao')} tese {x.get('tese_numero')}: {x.get('enunciado')}\n   {x.get('url', '')}")
    return achados


def cmd_busca(args):
    achados = buscar_jur(args.termos)
    for a in achados[: args.max]:
        print(a)
    print(f"-- {len(achados)} resultado(s), mostrando {min(len(achados), args.max)}")
    return 0 if achados else 1


# ---------- conferência de citações ----------
NUM = r"(?:n\.?\s*[º°o]?\.?\s*)?"  # n.º, nº, n°, no, n.
RE_SUM = re.compile(rf"\bsumulas?\s*(vinculantes?\s*)?({NUM}\d+(?:\s*(?:,|e|/)\s*{NUM}\d+)*)(?:\s*(?:[-/,]|d[oa]s?)?\s*(stj|stf|superior tribunal de justica|supremo tribunal federal))?")
RE_SV = re.compile(rf"\bsv\s*{NUM}(\d+)")
RE_TEMA = re.compile(rf"\btemas?\s*({NUM}\d+(?:\s*(?:,|e)\s*{NUM}\d+)*)")
RE_NOMES = re.compile("|".join(sorted((re.escape(n).replace("\\ ", r"\s+") for n in NOMES), key=len, reverse=True)))
RE_SIGLA = re.compile(r"\b(CPPM|CPP|CPM|CRFB|CF/88|CF|CP|CC|CPC|CLT|CTN|CDC|CTB|ECA|LGPD)\b")  # maiúscula só
RE_LEI = re.compile(rf"\b(lei\s+complementar|decreto[- ]lei|lc|lei)\s*(?:federal\s*)?{NUM}(\d+(?:\.\d{{3}})*)\s*(?:/\s*(\d{{2,4}})|,\s*de\s*[^,]{{0,25}}?de\s*(\d{{4}}))?")
RE_ART = re.compile(r"\bart(?:s|igos?)?\b")
RE_RUIDO = re.compile(r"§+\s*\d+\s*[º°o]?(?:-[a-z])?|\bparagrafo unico|\binc(?:iso|isos|\.)?\s*[ivxlc]+\b|\balinea\s*\"?[a-z]\"?|\bc/c\b|(?<![\d.\w])8\s+\d+\s*[º°]")  # o último: OCR lê "§ 4º" como "8 4º"
RE_NUMART = re.compile(r"(?<![\d./])(\d+(?:\.\d{3})*)\s*([º°])?(?:\s*-\s*([a-z])\b)?(?![\d/])")
RE_FRASE = re.compile(r"(?<!art)(?<!arts)(?<!inc)\.\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")
RE_DEPOIS = re.compile(r"^\s*,?\s*\(?\s*arts?\.?\s*")


def nums_sumula(txt):
    return [re.sub(r"\D", "", n) for n in re.findall(r"\d+", txt)]


def refs_de_lei(orig, f):
    """Posições (ini, fim, ref, ano) de leis citadas no texto."""
    achados = []
    for m in RE_SIGLA.finditer(orig):
        achados.append((m.start(), m.end(), SIGLAS_TEXTO.get(m.group(1), m.group(1)), None))
    for m in RE_NOMES.finditer(f):
        achados.append((m.start(), m.end(), NOMES[re.sub(r"\s+", " ", m.group(0))], None))
    for m in RE_LEI.finditer(f):
        t = re.sub(r"\s+", " ", m.group(1))
        tipo = "lc" if t in ("lei complementar", "lc") else ("lei" if t == "lei" else "dl")
        achados.append((m.start(), m.end(), f"{tipo}:{m.group(2).replace('.', '')}", ano4(m.group(3) or m.group(4))))
    achados.sort()
    limpo, fim = [], -1
    for a in achados:
        if a[0] >= fim:
            limpo.append(a)
            fim = a[1]
    return limpo


def numeros_de_artigos(seg):
    seg = RE_RUIDO.sub(" ", seg)
    # suspeito: "81º" não existe em texto bem grafado (ordinal só até 9); em OCR costuma ser "§ 1º"
    return [(chave_art(n, suf), bool(o) and int(n.replace(".", "")) >= 10) for n, o, suf in RE_NUMART.findall(seg)]


def extrair_citacoes(texto):
    f = fold(texto)
    cits, vistos = [], {}

    def add(c):  # uma entrada por citação; "posicoes" guarda cada ocorrência (a pertinência é julgada em cada uso)
        k = (c["tipo"], c.get("trib"), c.get("ref"), c["num"])
        if k not in vistos:
            c["posicoes"] = [c["pos"]]
            vistos[k] = c
            cits.append(c)
        else:
            vistos[k]["posicoes"].append(c["pos"])

    for m in RE_SUM.finditer(f):
        trib = "sv" if m.group(1) else ({"stj": "stj", "stf": "stf", "superior tribunal de justica": "stj", "supremo tribunal federal": "stf"}.get(m.group(3)))
        for n in nums_sumula(m.group(2)):
            add({"tipo": "sumula", "trib": trib, "num": n, "citada": texto[m.start():m.end()].strip(), "pos": m.start()})
    for m in RE_SV.finditer(f):
        add({"tipo": "sumula", "trib": "sv", "num": m.group(1), "citada": texto[m.start():m.end()].strip(), "pos": m.start()})
    for m in RE_TEMA.finditer(f):
        trib = None
        for ctx in (f[m.end(): m.end() + 30], f[max(0, m.start() - 40): m.start()]):  # primeiro o que vem logo depois
            stj, stf = bool(re.search(r"stj|superior tribunal|repetitiv", ctx)), bool(re.search(r"stf|supremo|repercussao", ctx))
            trib = "stj" if stj and not stf else ("stf" if stf and not stj else None)
            if trib:
                break
        for n in nums_sumula(m.group(1)):
            add({"tipo": "tema", "trib": trib, "num": n, "citada": texto[m.start():m.end()].strip(), "pos": m.start()})
    refs = refs_de_lei(texto, f)
    anterior = 0
    for ini, fim, ref, ano in refs:
        ini0 = max(anterior, ini - 250)
        quebras = list(RE_FRASE.finditer(texto, ini0, ini))  # só a frase da citação
        if quebras:
            ini0 = quebras[-1].end()
        janela = f[ini0:ini]
        a = RE_ART.search(janela)
        nums = numeros_de_artigos(janela[a.start():]) if a else []
        anterior = fim
        if not nums:  # "Lei 9.613/98, art. 1º"
            d = RE_DEPOIS.match(f[fim: fim + 40])
            if d:
                resto = re.split(r"\.\s|\s+d[oa]s?\s|;", f[fim + d.end(): fim + 40])[0]
                nums = numeros_de_artigos(resto)
                anterior = fim + d.end() + len(resto)
        for n, sus in nums:
            add({"tipo": "artigo", "ref": ref, "ano": ano, "num": n, "citada": texto[ini:fim], "suspeito": sus, "pos": ini})
    return cits


def conferir_uma(c):
    r = dict(c)
    if c["tipo"] == "sumula":
        tribs = [c["trib"]] if c["trib"] else ["stj", "stf"]
        ach = [(t, achar_sumula(t, c["num"])[0]) for t in tribs]
        ach = [(t, x) for t, x in ach if x]
        if not ach:
            r.update(ok=False, msg=f"não existe súmula {c['num']} ({'/'.join(t.upper() for t in tribs)})")
        else:
            aviso = "" if c["trib"] else " [tribunal não informado: confira qual foi o citado]"
            r.update(ok=True if c["trib"] else None, msg=aviso + "\n    " + "\n    ".join(fmt_sumula(t, x) for t, x in ach))
            if any(x.get("status") not in ("ativa", "aprovada", None) for _, x in ach):
                r["ok"] = None
                r["msg"] = " [ATENÇÃO: status diferente de ativa/aprovada]" + r["msg"]
    elif c["tipo"] == "tema":
        tribs = [c["trib"]] if c["trib"] else ["stf", "stj"]
        ach = [(t, achar_tema(t, c["num"])[0]) for t in tribs]
        ach = [(t, x) for t, x in ach if x]
        if not ach:
            r.update(ok=False, msg=f"não existe tema {c['num']} ({'/'.join(t.upper() for t in tribs)})")
        else:
            aviso = "" if c["trib"] else " [tribunal não informado: confira qual foi o citado]"
            r.update(ok=True if c["trib"] else None, msg=aviso + "\n    " + "\n    ".join(fmt_tema(t, x) for t, x in ach))
    else:
        path, nota = resolver_lei(c["ref"], c["ano"])
        if not path:
            r.update(ok=None, msg="diploma fora da cobertura local (decretos, portarias, resoluções, tratados): conferir à mão")
        else:
            linhas, meta = ler_lei(path)
            i, corpo = achar_artigo(linhas, c["num"])
            if corpo is None:
                r.update(ok=False, msg=f"art. {c['num']} não existe em {meta.get('title', path.stem)}" + (f" ({nota})" if nota else ""))
            else:
                texto = " ".join(x.lstrip("# ").strip() for x in corpo)
                revog = bool(re.match(r"Art\.?\s*[\d.]+\s*[º°o]?(?:-[A-Za-z])?\.?\s*\(revogad[oa]", texto, re.I))  # só o caput; incisos revogados não contam
                vetado = bool(re.match(r"Art\.?\s*[\d.]+\s*[º°o]?(?:-[A-Za-z])?\.?\s*\(vetado\)", texto, re.I))
                ok = False if revog else (None if (nota or vetado or c.get("suspeito")) else True)
                msg = ("REVOGADO — " if revog else "") + ("VETADO — o artigo não vigorou. " if vetado else "") + \
                      ("[ATENÇÃO: número ≥10 com ordinal (º): provável erro de leitura, p. ex. '§ 1º' lido como '81º'] " if c.get("suspeito") else "") + (f"[ATENÇÃO: {nota}] " if nota else "") + f"{meta.get('title', path.stem)}: {texto[:220]}{'…' if len(texto) > 220 else ''}"
                r.update(ok=ok, msg=msg)
    return r


def _poppler(nome):
    import shutil
    from glob import glob
    return shutil.which(nome) or next(iter(glob(os.path.expandvars(rf"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*Poppler*\poppler-*\Library\bin\{nome}.exe"))), None)


def ler_pdf(caminho):
    """Texto de um PDF, só em memória (nada é gravado). Camada de texto sem Unicode (acentos viram U+FFFD) cai em OCR local."""
    import subprocess
    pdftotext = _poppler("pdftotext")
    if not pdftotext:
        raise SystemExit("pdftotext (poppler) não encontrado")
    t = subprocess.run([pdftotext, "-layout", "-enc", "UTF-8", str(caminho), "-"], capture_output=True).stdout.decode("utf-8", "replace")
    if len(t.strip()) >= 500 and t.count("\ufffd") / len(t) < 0.002:
        return t, "camada de texto do PDF"
    from concurrent.futures import ThreadPoolExecutor
    import io
    import pytesseract
    from PIL import Image
    pdftoppm = _poppler("pdftoppm")
    paginas = max(1, t.count("\f"))

    def ocr(n):
        ppm = subprocess.run([pdftoppm, "-r", "300", "-gray", "-f", str(n), "-l", str(n), str(caminho)], capture_output=True).stdout
        return pytesseract.image_to_string(Image.open(io.BytesIO(ppm)), lang="por", config="--psm 4")

    with ThreadPoolExecutor(6) as ex:
        return "\n\f".join(ex.map(ocr, range(1, paginas + 1))), f"OCR local de {paginas} página(s) (a camada de texto estava vazia ou ilegível)"


def carregar_texto(arquivo):
    if arquivo == "-":
        texto, modo = sys.stdin.read(), "entrada padrão"
    elif arquivo.lower().endswith(".pdf"):
        texto, modo = ler_pdf(arquivo)
    else:
        texto, modo = Path(arquivo).read_text(encoding="utf-8"), "arquivo de texto"
    print(f"[texto lido de: {modo}]", file=sys.stderr)
    if modo.startswith("OCR"):
        print("[OCR pode errar números e ordinais (Art. 19 por Art. 1º): confira no PDF as citações que chamarem a atenção]", file=sys.stderr)
    return texto, modo


def cmd_conferir(args):
    texto, _ = carregar_texto(args.arquivo)
    res = [conferir_uma(c) for c in extrair_citacoes(texto)]
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    rot = {True: "[OK]", False: "[NAO ACHEI]", None: "[ATENCAO]"}
    for r in res:
        t = (r.get("trib") or "?").upper()
        quem = {"sumula": f"Súmula {t} {r['num']}", "tema": f"Tema {t} {r['num']}"}.get(r["tipo"]) or f"{r.get('ref')} art. {r['num']}"
        rotulo = "[REVOGADO]" if r["ok"] is False and r["msg"].startswith("REVOGADO") else rot[r["ok"]]
        print(f"{rotulo} {quem}  (no texto: \"{r['citada']}\")  {r['msg']}")
    n = [sum(1 for r in res if r["ok"] is v) for v in (True, None, False)]
    print(f"\n{len(res)} citação(ões): {n[0]} ok, {n[1]} atenção, {n[2]} não achadas")
    print("A conferência diz só se a citação EXISTE e o que ela diz. Se a peça a usa para o ponto certo, é leitura sua.")
    print("Extração por regex: citações escritas fora do padrão podem escapar. " + estado_dados(curto=True))
    return 1 if n[2] else 0


# ---------- pertinência e juízo de valor (modelo LOCAL; a peça nunca sai da máquina) ----------
OLLAMA = os.environ.get("JURIDICO_OLLAMA", "http://127.0.0.1:11434")
MODELO = os.environ.get("JURIDICO_MODELO", "gpt-oss:20b")
PENSAR = os.environ.get("JURIDICO_PENSAR", "low")  # low | medium | high: mais raciocínio, mais tempo
VEREDITOS = ["sustenta", "sustenta_em_parte", "nao_sustenta", "indeterminado"]
PESOS = ["forte", "razoavel", "fraco", "inadequado"]
SCHEMA = {
    "type": "object",
    "properties": {
        "afirmacao": {"type": "string"}, "o_texto_diz": {"type": "string"}, "veredito": {"type": "string", "enum": VEREDITOS}, "fundamento": {"type": "string"},
        "peso": {"type": "string", "enum": PESOS}, "avaliacao": {"type": "string"}, "ressalvas": {"type": "string"}, "sugestao": {"type": "string"},
        "termos": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["afirmacao", "o_texto_diz", "veredito", "fundamento", "peso", "avaliacao", "ressalvas", "sugestao", "termos"],
}
SISTEMA = (
    "Você é revisor jurídico brasileiro, especialista em direito penal e processual penal, auxiliando uma autoridade de polícia judiciária a revisar uma peça. "
    "Avalie SOMENTE se a norma ou o precedente citado, exatamente como transcrito abaixo, sustenta a proposição jurídica que a peça lhe atribui. "
    "Use apenas o texto fornecido: não invente conteúdo de norma, de súmula ou de tese, e não cite outros precedentes. Seja técnico, objetivo e curto, em português.\n"
    "Método obrigatório:\n"
    "1) A passagem pode ter várias afirmações e várias citações. Julgue só a proposição jurídica ligada à CITAÇÃO AVALIADA.\n"
    "2) Ignore a parte fática do caso (quem fez o quê, valores, datas, número de pessoas): não é objeto da norma e você não tem como verificá-la. "
    "Julgue se a norma prevê, define, autoriza, veda ou disciplina o que a peça lhe atribui; quando a peça enquadra fatos na norma, julgue só se a descrição genérica "
    "corresponde aos elementos que o texto exige.\n"
    "3) Antes de decidir, preencha o_texto_diz com o que o texto fornecido de fato prevê, e só então compare. Nome de instituto ou conceito só vale se o texto o traz ou o descreve "
    "(ex.: se a peça diz 'decadência' e o texto trata de prescrição, não sustenta; confundir institutos é erro).\n"
    "4) Na dúvida entre nao_sustenta e indeterminado, escolha indeterminado e diga o que faltou.\n"
    "Campos: afirmacao = a proposição jurídica que a peça atribui a esta citação, sem os fatos do caso (até 30 palavras); "
    "o_texto_diz = o que o texto fornecido prevê, com os termos-chave; "
    "veredito = sustenta | sustenta_em_parte | nao_sustenta | indeterminado; "
    "fundamento = por que, apontando as palavras do texto fornecido que decidem; "
    "peso = juízo de valor sobre a força do fundamento no ponto: forte | razoavel | fraco | inadequado; "
    "avaliacao = uma ou duas frases justificando o peso (excesso, lacuna, alcance menor ou maior que o afirmado, hipótese diversa); "
    "ressalvas = limites do texto fornecido (redação dada por lei posterior, hipótese específica, súmula cancelada, tese restrita) ou vazio; "
    "sugestao = ajuste de redação ou de fundamento, ou vazio se não precisa; "
    "termos = 2 ou 3 palavras-chave jurídicas, no singular e sem acento, do ponto afirmado, para procurar súmula ou tese que o apoie melhor. "
    "Coerência: se o veredito for nao_sustenta, o peso é inadequado."
)


def texto_citado(c):
    """(rótulo, texto integral do dispositivo/precedente, link) ou None."""
    if c["tipo"] == "sumula":
        for t in ([c["trib"]] if c["trib"] else ["stj", "stf"]):
            x = achar_sumula(t, c["num"])[0]
            if x:
                return f"{NOME_SUM[t]} {x['numero']} [{x.get('status')}]", x.get("enunciado", ""), x.get("url", "")
    elif c["tipo"] == "tema":
        for t in ([c["trib"]] if c["trib"] else ["stf", "stj"]):
            x = achar_tema(t, c["num"])[0]
            if x:
                txt = (f"Título: {x.get('titulo')}\nTese: {x.get('tese') or '(sem tese fixada)'}" if t == "stf"
                       else f"Questão: {x.get('questao')}\nTese: {x.get('teseFirmada') or '(sem tese firmada)'}")
                return f"Tema {x['numero']} {t.upper()} [{x.get('situacao')}]", txt, link(x.get("links"))
    else:
        path, _ = resolver_lei(c["ref"], c["ano"])
        if path:
            linhas, meta = ler_lei(path)
            _, corpo = achar_artigo(linhas, c["num"])
            if corpo:
                return f"{meta.get('title', path.stem)}, art. {c['num']}", "\n".join(x.lstrip("# ").strip() for x in corpo)[:3000], meta.get("source", "")
    return None


def contexto(texto, pos):
    """Frase da citação (e a anterior, se esta for curta), até ~1.100 caracteres."""
    quebras = [m.end() for m in RE_FRASE.finditer(texto, max(0, pos - 1200), pos)]
    ini = quebras[-1] if quebras else max(0, pos - 400)
    if pos - ini < 150 and len(quebras) > 1:
        ini = quebras[-2]
    m = RE_FRASE.search(texto, pos)
    fim = m.start() + 1 if m and m.start() - pos < 700 else min(len(texto), pos + 500)
    return re.sub(r"\s+", " ", texto[ini:fim]).strip()[:1100]


def perguntar(trecho, rotulo, texto_norma):
    import urllib.error
    import urllib.parse
    import urllib.request
    if urllib.parse.urlparse(OLLAMA).hostname not in ("127.0.0.1", "localhost", "::1"):
        raise SystemExit(f"sigilo: o modelo precisa ser local, e JURIDICO_OLLAMA aponta para {OLLAMA}")
    corpo = {"model": MODELO, "stream": False, "format": SCHEMA, "think": PENSAR, "options": {"temperature": 0, "num_ctx": 8192},
             "messages": [{"role": "system", "content": SISTEMA},
                          {"role": "user", "content": f"TRECHO DA PEÇA:\n{trecho}\n\nCITAÇÃO AVALIADA: {rotulo}\n\nTEXTO DA NORMA/PRECEDENTE (fonte oficial, literal):\n{texto_norma}"}]}
    for tentativa in (0, 1):
        req = urllib.request.Request(OLLAMA + "/api/chat", json.dumps(corpo).encode(), {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(json.loads(r.read())["message"]["content"])
        except urllib.error.HTTPError as e:
            if e.code == 400 and tentativa == 0:  # modelo sem suporte a "think"
                corpo.pop("think", None)
                continue
            raise
        except urllib.error.URLError as e:
            raise SystemExit(f"Ollama não responde em {OLLAMA} ({e.reason}); iniciar com: ollama serve")


VAZIO = re.compile(r"\s*(nenhum[ao]?\b.{0,40}|n/?a|não há\b.{0,40}|-+|—)\s*\.?\s*", re.I)


def limpo(x):
    return "" if VAZIO.fullmatch(x or "") else (x or "").strip()


def cmd_pertinencia(args):
    if args.arquivo != "-" and not args.saida and not args.stdout:
        print("O relatório de pertinência reproduz trechos da peça. Informe --saida RELATORIO.md (pasta do caso) ou --stdout se a peça não tiver dado de caso.")
        return 2
    texto, modo = carregar_texto(args.arquivo)
    res = [conferir_uma(c) for c in extrair_citacoes(texto)]
    rot = lambda r: ({"sumula": f"Súmula {(r.get('trib') or '?').upper()} {r['num']}", "tema": f"Tema {(r.get('trib') or '?').upper()} {r['num']}"}.get(r["tipo"]) or f"{r.get('ref')} art. {r['num']}")
    for r in res:
        r["fonte"] = texto_citado(r) if r["ok"] is not False else None
        r["quem"] = r["fonte"][0].split(" [")[0] if r["fonte"] else rot(r)
        r["analises"] = []
    total = sum(len(r["posicoes"]) for r in res if r["fonte"])
    print(f"[modelo local {MODELO}; {total} ocorrência(s) de {sum(1 for r in res if r['fonte'])} citação(ões) a avaliar]", file=sys.stderr)
    n = 0
    for r in res:
        for pos in (r["posicoes"] if r["fonte"] else []):
            n += 1
            print(f"[{n}/{total}] {r['quem']}", file=sys.stderr, flush=True)
            trecho = contexto(texto, pos)
            a = perguntar(trecho, r["fonte"][0], r["fonte"][1])
            if a["veredito"] == "nao_sustenta":
                a["peso"] = "inadequado"  # o modelo às vezes mede a força da norma, não a do uso
            a["alternativas"] = []
            if a["veredito"] != "sustenta" or a["peso"] in ("fraco", "inadequado"):
                tm = [t for t in a["termos"] if t.strip()][:3]
                for k in (len(tm), 2):  # todos os termos; senão os dois primeiros
                    if k >= 2 and not a["alternativas"]:
                        a["alternativas"] = [x for x in buscar_jur(tm[:k]) if not x.startswith(r["fonte"][0].split(" [")[0])][:3]
            r["analises"].append((trecho, a))
    linhas = ["# Pertinência e juízo de valor das citações",
              f"*Texto: {modo}. Modelo local: {MODELO}. {estado_dados(curto=True)}*", "",
              "> **Triagem de apoio, não parecer.** Modelo local de 20 bilhões de parâmetros lendo só o dispositivo transcrito. Pode errar o alcance, "
              "ignorar jurisprudência contrária e confundir hipótese. Todo `nao_sustenta`, `sustenta_em_parte` e `indeterminado` merece leitura sua; "
              "todo `sustenta` ainda depende de você ter lido a norma. Conferir na fonte oficial antes de assinar.", ""]
    for i, r in enumerate(res, 1):
        linhas.append(f"## {i}. {r['quem']}  —  existência: {'ok' if r['ok'] else ('atenção' if r['ok'] is None else 'não achada/revogada')}")
        if r["msg"].strip() and r["ok"] is not True:
            linhas.append(f"- Conferência: {r['msg'].strip().splitlines()[0][:300]}")
        if not r["analises"]:
            linhas += ["- Sem análise de pertinência (citação não localizada ou revogada).", ""]
            continue
        linhas.append(f"- **Fonte:** {r['fonte'][0]} — {r['fonte'][2]}")
        for k, (trecho, a) in enumerate(r["analises"], 1):
            linhas += [f"### Uso {k} de {len(r['analises'])}", f"- **Trecho da peça:** {trecho}", f"- **O que a peça afirma (proposição jurídica):** {a['afirmacao']}", f"- **O que o texto da fonte diz:** {a['o_texto_diz']}",
                       f"- **Veredito:** `{a['veredito']}`  |  **Peso do fundamento:** `{a['peso']}`", f"- **Fundamento:** {a['fundamento']}",
                       f"- **Avaliação:** {a['avaliacao']}"]
            if limpo(a["ressalvas"]):
                linhas.append(f"- **Ressalvas:** {limpo(a['ressalvas'])}")
            if limpo(a["sugestao"]):
                linhas.append(f"- **Sugestão:** {limpo(a['sugestao'])}")
            if a.get("alternativas"):
                linhas.append("- **Candidatos na base para apoiar melhor o ponto (a pertinência de cada um é sua):**")
                linhas += [f"  - {x}" for x in a["alternativas"]]
        linhas.append("")
    rel = "\n".join(linhas)
    if args.saida:
        with open(args.saida, "x", encoding="utf-8") as f:  # "x": nunca sobrescreve
            f.write(rel)
    else:
        print(rel)
    feitos = [a for r in res for _, a in r["analises"]]
    cont = lambda campo, v: sum(1 for a in feitos if a[campo] == v)
    resumo = f"\n{len(res)} citação(ões), {len(feitos)} uso(s) avaliado(s): " + ", ".join(f"{v} {cont('veredito', v)}" for v in VEREDITOS) + " | peso: " + ", ".join(f"{v} {cont('peso', v)}" for v in PESOS)
    print(resumo, file=sys.stdout if args.saida else sys.stderr)
    if args.saida:
        pedem = [r["quem"] for r in res if any(a["veredito"] != "sustenta" or a["peso"] in ("fraco", "inadequado") for _, a in r["analises"])]
        print(f"Relatório gravado em {args.saida} (não foi lido por mim nem enviado a serviço externo). Para olhar primeiro: {', '.join(pedem) or 'nenhuma'}")
    return 0


# ---------- segunda opinião: só a proposição jurídica abstrata, revisada pelo usuário ----------
AUDITAR = Path(os.environ.get("JURIDICO_AUDITAR", r"C:\ACERVO\Segundo_Cerebro\.sistema\scripts\auditar.py"))
PERMITIDAS = set("""Lei Leis Código Constituição Federal Penal Processo Civil Tributário Nacional Estado Estados União Ministério Público Judiciário Polícia
Supremo Tribunal Superior Justiça Súmula Súmulas Tema Temas Vinculante Complementar Banco Central Brasil Receita Conselho Controle Atividades Financeiras
Artigo Artigos Parágrafo Inciso Constitucional República Brasília Direito Medida Provisória Decreto Decreto-Lei Repercussão Geral Repetitivo Recurso Extraordinário
Especial Habeas Corpus Inquérito Ação Pública Inteligência Financeira Sigilo Bancário Fiscal Judicial Penal Eleitoral Trabalho Delegado Juiz Autoridade
Organização Criminosa Lavagem Dinheiro Drogas Interceptação Telefônica Telemático Marco Civil Internet Proteção Dados""".split())
SIGLAS_OK = set("STF STJ CF CP CPP CPC CTN UIF COAF CTB CLT PF MP RFB BACEN CGU TCU CNJ CNMP LC DL OAB RE REsp ADI ADPF HC LGPD ECA".split())
_RE_REF = re.compile(r"(?i)\b(?:lei|lc|decreto-lei|decreto)\s*(?:complementar\s*)?(?:n\.?\s*[º°o]?\.?\s*)?[\d.]+(?:/\d{2,4})?|\bs[úu]mulas?\s*(?:vinculantes?\s*)?(?:n\.?\s*[º°o]?\.?\s*)?\d+|\btemas?\s*(?:n\.?\s*[º°o]?\.?\s*)?\d+|\b(?:arts?\.?|artigos?)\s*\d[\d.]*[º°o]?(?:-[a-z])?(?:\s*(?:,|e|a)\s*\d[\d.]*[º°o]?(?:-[a-z])?)*|§+\s*\d+[º°o]?(?:-[a-z])?|\b(?:inc|inciso|al[ií]nea)s?\.?\s*[ivxlc]+\b")


BRANDO = "possível nome próprio ou sigla"  # caixa alta não é nome próprio; único alerta que o usuário pode aceitar por item


def alertas(texto, detalhar=False):
    """Categorias de dado de caso que sobraram na proposição. Heurística de rede de segurança: não substitui a leitura do usuário.
    detalhar=True acrescenta os termos que dispararam o alerta brando (só para o arquivo de revisão do usuário, nunca para a tela)."""
    out = []
    if AUDITAR.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("auditar_vault", AUDITAR)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for r in mod.REGRAS:
            if r.get("so_nome"):
                continue
            for m in re.finditer(r["rx"], texto):
                if not mod.eh_ruido(m.group(0), texto, m.start()):
                    out.append(f"auditor: {r['nome']}")
                    break
    sem_refs = _RE_REF.sub(" ", texto)
    if re.search(r"R\$|\d+[.,]\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b", sem_refs):
        out.append("valor ou data")
    if re.search(r"\d{3,}", sem_refs):
        out.append("número solto")
    nomes = []
    for m in re.finditer(r"(?<![.!?]\s)(?<!^)\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-záéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ]{2,}\b", sem_refs):
        w = m.group(0)
        if w in PERMITIDAS or w in SIGLAS_OK:
            continue
        nomes.append(w)
    if nomes:
        out.append(BRANDO + (f" [{', '.join(sorted(set(nomes)))}]" if detalhar else ""))
    return sorted(set(out))


def _blocos_relatorio(rel):
    """[(i, rótulo, [(k, proposição, veredito)])] a partir do relatório de pertinência."""
    out = []
    for b in re.split(r"\n## ", rel)[1:]:
        cab = b.split("\n")[0]
        m = re.match(r"(\d+)\.\s*(.*?)\s+—\s+existência", cab)
        usos = []
        for k, u in enumerate(re.split(r"\n### Uso ", b)[1:], 1):
            pr = re.search(r"\*\*O que a peça afirma \(proposição jurídica\):\*\* (.*)", u)
            ve = re.search(r"Veredito:\*\* `(\w+)`", u)
            if pr and ve:
                usos.append((k, pr.group(1).strip(), ve.group(1)))
        out.append((int(m.group(1)), m.group(2), usos))
    return out


def cmd_proposicoes(args):
    rel = Path(args.relatorio).read_text(encoding="utf-8")
    texto, _ = carregar_texto(args.origem)
    res = [conferir_uma(c) for c in extrair_citacoes(texto)]
    blocos = _blocos_relatorio(rel)
    if len(blocos) != len(res):
        print(f"Relatório e peça não batem ({len(blocos)} blocos contra {len(res)} citações): gere de novo com `pertinencia`.")
        return 2
    linhas = ["# Proposições jurídicas para segunda opinião (revisão do usuário)", "",
              "**O que acontece com este arquivo:** só as proposições abaixo cujo quadrinho estiver marcado `[x]` e que passarem na checagem automática irão, com o texto "
              "oficial da norma (público), a um modelo maior em nuvem. **Nada do resto da peça vai**: nem trecho, nem o veredito do modelo local.", "",
              "**O que você deve fazer:** em cada item, (1) edite a proposição até não restar nenhum fato do caso: nome, empresa, valor, data, local, número de pessoas, "
              "relação entre investigados; deve ficar só o que a norma ou o precedente supostamente prevê; (2) marque `[x]` nos que podem ir. "
              "Itens com `ALERTA` sobraram dado que parece de caso: reescreva e a checagem roda de novo no envio.", ""]
    n = alerta = 0
    for (i, rotulo, usos), r in zip(blocos, res):
        cit = texto_citado(r) if r["ok"] is not False else None
        if cit and cit[0].split(" [")[0] != rotulo:
            print(f"Rótulo da citação {i} não confere com o relatório: gere de novo.")
            return 2
        for k, prop, vered in usos:
            n += 1
            al = alertas(prop, detalhar=True)
            alerta += bool(al)
            ref = {c: r.get(c) for c in ("tipo", "trib", "ref", "ano", "num")}
            linhas += [f"### P{i}.{k} — {rotulo}", "- [ ] enviar", f"- Proposição: {prop}",
                       f"- ALERTA ({', '.join(al)}): reescreva antes de marcar" if al else "- (sem alerta automático)",
                       f"- Veredito do modelo local, não vai no pacote: `{vered}`",
                       f"<!-- ref:{json.dumps(ref, ensure_ascii=False)} -->", ""]
    with open(args.saida, "x", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"{n} proposição(ões) em {args.saida}; {alerta} com alerta automático. Revise e marque [x]; não li o arquivo.")
    return 0


PEDIDO = """Você é o segundo revisor jurídico de uma peça de polícia judiciária brasileira (direito penal e processual penal). Abaixo há proposições jurídicas abstratas, \
já sem fatos de caso, cada uma com o texto oficial da norma ou do precedente que a peça cita como fundamento. Para CADA proposição responda, objetivamente:
1. O texto oficial sustenta a proposição? (sim / em parte / não / indeterminado) e por quê, apontando as palavras do texto.
2. Há confusão de institutos, excesso de alcance, hipótese diversa, ou ressalva que a proposição omite?
3. Há súmula, tese de repercussão geral ou repetitivo, ou entendimento consolidado que a contrarie, a limite ou a sustente melhor? Cite pelo número SOMENTE se tiver certeza; \
se não tiver, diga que não tem certeza em vez de citar de memória.
4. Sugestão curta de redação, se precisar.
Seja técnico e honesto sobre o que não sabe. Não peça fatos do caso: eles foram retirados de propósito.
"""


def cmd_pacote(args):
    md = Path(args.lista).read_text(encoding="utf-8")
    aceitos = {x.strip() for x in (getattr(args, "aceitar", None) or "").split(",") if x.strip()}
    itens, barrados, total = [], [], 0
    for b in re.split(r"\n### ", md)[1:]:
        total += 1
        if not re.search(r"^- \[\s*[xX]\s*\]\s*enviar", b, re.M):
            continue
        ident = b.split("\n")[0].split(" — ")[0]
        prop = re.search(r"^- Proposição: (.*)$", b, re.M)
        ref = re.search(r"<!-- ref:(.*?) -->", b)
        if not prop or not ref:
            barrados.append(f"{ident} (formato)")
            continue
        al = alertas(prop.group(1))
        if ident in aceitos:  # o usuário conferiu e disse que o alerta brando é falso
            al = [a for a in al if a not in (BRANDO, "número solto")]
        if al:
            barrados.append(f"{ident} ({', '.join(al)})")
            continue
        r = json.loads(ref.group(1))
        cit = texto_citado(r)
        if not cit:
            barrados.append(f"{ident} (norma não localizada)")
            continue
        itens.append((ident, cit, prop.group(1).strip()))
    if barrados:
        print("Pacote NÃO gerado. Itens marcados que a checagem barrou (corrija o texto na lista): " + "; ".join(barrados))
        return 3
    if not itens:
        print("Nenhum item marcado [x].")
        return 1
    partes = [PEDIDO, f"Total de proposições: {len(itens)}.", ""]
    for ident, (rotulo, norma, link_), prop in itens:
        partes += [f"## {ident} — fundamento citado: {rotulo}", f"**Proposição da peça:** {prop}", "", f"**Texto oficial ({link_}):**", norma, ""]
    with open(args.saida, "x", encoding="utf-8") as f:
        f.write("\n".join(partes))
    print(f"Pacote com {len(itens)} de {total} proposição(ões) em {args.saida}. Contém só: pedido, proposições revisadas por você e texto oficial das normas.")
    return 0


def estado_dados(curto=False):
    out = []
    p, _ = resolver_lei("CP")
    if p:
        out.append(f"LawCodex coletado {frontmatter(p.read_text(encoding='utf-8').splitlines()[:30]).get('retrieved', '?')}")
    for rotulo, arq, ch in (("súm.STJ", "sumulas_stj.json", "sumulas"), ("súm.STF", "sumulas_stf.json", "sumulas"),
                            ("temas STJ", "flash_temas_stj.json", "temas"), ("temas RG STF", "temas_rg_stf.json", "temas")):
        try:
            m = carregar(arq, ch)[0]
            out.append(f"{rotulo} {str(m.get('gerado_em') or m.get('generatedAt') or '?')[:10]}")
        except OSError:
            out.append(f"{rotulo} AUSENTE")
    if p:
        try:
            dias = (datetime.now().date() - datetime.fromisoformat(frontmatter(p.read_text(encoding="utf-8").splitlines()[:30]).get("retrieved", "")).date()).days
            n = len(list(OVERLAY.rglob("*.md"))) if OVERLAY.exists() else 0
            out.append(f"{n} diploma(s) recoletado(s) pela rotina" + (f" [ATENCAO: CP com {dias} dias, rodar rotina/atualizar.py]" if dias > 14 else ""))
        except ValueError:
            pass
    return "Dados: " + "; ".join(out)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lei", help="texto de um artigo: lei CP 121 | lei 'lei 12850' 3-A | lei CP --busca termo")
    p.add_argument("lei")
    p.add_argument("artigo", nargs="?", default="")
    p.add_argument("--busca", nargs="+")
    p.set_defaults(f=cmd_lei)
    p = sub.add_parser("sumula", help="sumula stj|stf|sv N")
    p.add_argument("tribunal", choices=list(FONTES_SUM))
    p.add_argument("numero")
    p.set_defaults(f=cmd_sumula)
    p = sub.add_parser("tema", help="tema stf|stj N")
    p.add_argument("tribunal", choices=list(FONTES_TEMA))
    p.add_argument("numero")
    p.set_defaults(f=cmd_tema)
    p = sub.add_parser("busca", help="termos em súmulas, temas e teses (todos os termos, sem acento)")
    p.add_argument("termos", nargs="+")
    p.add_argument("--max", type=int, default=15)
    p.set_defaults(f=cmd_busca)
    p = sub.add_parser("conferir", help="confere citações de um texto (arquivo ou -)")
    p.add_argument("arquivo")
    p.add_argument("--json", action="store_true")
    p.set_defaults(f=cmd_conferir)
    p = sub.add_parser("pertinencia", help="apura se cada citação sustenta o que a peça afirma (modelo local) e dá o juízo de valor")
    p.add_argument("arquivo")
    p.add_argument("--saida", help="relatório .md (não sobrescreve); obrigatório para peça de caso")
    p.add_argument("--stdout", action="store_true", help="imprime o relatório: só para texto sem dado de caso")
    p.set_defaults(f=cmd_pertinencia)
    p = sub.add_parser("proposicoes", help="lista de proposições abstratas, para o usuário revisar, a partir de um relatório de pertinência")
    p.add_argument("relatorio")
    p.add_argument("--origem", required=True, help="a peça (pdf/txt) de onde o relatório saiu")
    p.add_argument("--saida", required=True)
    p.set_defaults(f=cmd_proposicoes)
    p = sub.add_parser("pacote", help="monta o pacote de segunda opinião só com os itens marcados [x] e sem alerta")
    p.add_argument("lista")
    p.add_argument("--saida", required=True)
    p.add_argument("--aceitar", help="ids (P2.1,P6.2) cujo alerta de nome/sigla ou de número solto o usuário conferiu e é falso; auditor (CPF, telefone, e-mail, IP...), valor e data continuam barrando")
    p.set_defaults(f=cmd_pacote)
    p = sub.add_parser("status", help="datas dos dados")
    p.set_defaults(f=lambda a: print(estado_dados()) or 0)
    a = ap.parse_args()
    if a.cmd == "lei" and not a.busca and not a.artigo:
        ap.error("informe o artigo ou --busca")
    sys.exit(a.f(a))


if __name__ == "__main__":
    main()
