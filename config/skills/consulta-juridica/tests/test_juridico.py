"""Checagem mínima contra os dados reais: python -I tests/test_juridico.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import juridico as j

TEXTO = (
    "Condenado nos termos do art. 121, § 2º, IV, c/c art. 14, II, do Código Penal. "
    "Aplicou-se a Súmula 444 do STJ e a Súmula Vinculante 14. Nos termos do Tema 990 do STF "
    "e da Lei 12.850/2013, art. 3º-A. Também a Súmula 99999 do STJ, o art. 9999 do CPP "
    "e a Lei 12.850/2012, art. 1º. Arts. 33 e 35 da Lei 11.343/06. Ver Lei Complementar no 105/2001, art. 1o, e a Lei 9.613/984, art. 1º. "
    "No art. 33 da Lei n.º 11.343/2006, art. 2º, § 4º, II, da Lei nº 12.850/2013, e art. 13 da Lei Complementar n.º 105/2001. "
    "Do art. 1º, 8 4º, da Lei Complementar 105/2001 e art. 198, 81º, do Código Tributário Nacional. Lei 11.343/06, art. 11. "
    "Com fundamento no art. 198, §1º, I, do Código\r\n      Tributário Nacional e no artigo 1o., § 4o., da Lei\r\n      Complementar no 105/2001, e no art. 69 do Código Penal."
)


def main():
    res = {(r["tipo"], r.get("trib"), r.get("ref"), r["num"]): r for r in map(j.conferir_uma, j.extrair_citacoes(TEXTO))}
    ok = lambda *k: res[k]["ok"]
    assert ok("artigo", None, "CP", "121") is True
    assert ok("artigo", None, "CP", "14") is True
    assert ok("sumula", "stj", None, "444") is True
    assert ok("sumula", "sv", None, "14") is True
    assert ok("tema", "stf", None, "990") is True
    assert ok("artigo", None, "lei:12850", "3-a") is True
    assert ok("sumula", "stj", None, "99999") is False
    assert ok("artigo", None, "CPP", "9999") is False
    assert ok("artigo", None, "lei:11343", "33") is True and ok("artigo", None, "lei:11343", "35") is True
    assert "2" not in {k[3] for k in res if k[2] == "CP"}, "§ 2º não pode virar artigo"
    divergente = [r for k, r in res.items() if k[2] == "lei:12850" and k[3] == "1"]
    assert divergente and divergente[0]["ok"] is None and "divergente" in divergente[0]["msg"]
    assert ok("artigo", None, "lc:105", "1") is True, "LC 105 usa ## nos artigos e 'Art. 1o'"
    assert ok("artigo", None, "lei:9613", "1") is True, "inciso revogado não revoga o artigo; /984 = 98 + nota de rodapé"
    assert ("artigo", None, "lei:12850", "33") not in res, "art. 33 é da Lei 11.343, não da 12.850 (n.º com ponto)"
    assert ok("artigo", None, "lei:12850", "2") is True and ok("artigo", None, "lc:105", "13") is True
    assert ("artigo", None, "lc:105", "8") not in res, "'8 4º' é § 4º lido pelo OCR"
    assert ok("artigo", None, "CTN", "81") is None and ok("artigo", None, "CTN", "198") is True
    assert ok("artigo", None, "lei:11343", "11") is None and "VETADO" in res[("artigo", None, "lei:11343", "11")]["msg"]
    assert ("artigo", None, "CTN", "1") not in res, "quebra de linha entre 'Lei' e 'Complementar' desalinhava a janela e o art. 1º da LC virava CTN art. 1"
    assert ok("artigo", None, "CP", "69") is True
    linhas, _ = j.ler_lei(j.resolver_lei("CP")[0])
    corpo = j.achar_artigo(linhas, "69")[1]
    assert not corpo[-1].startswith("Concurso formal"), "rubrica do artigo seguinte colada no fim do art. 69"
    print(f"ok: {len(res)} citações conferidas")


main()
