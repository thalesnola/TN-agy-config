p = r"C:\LegalRef\skill\consulta-juridica\tests\test_juridico.py"
s = open(p, encoding="utf-8", newline="").read()
i = s.index("Lei 11.343/06, art. 11. Com fundamento")
j = s.index('"\n)', i)
novo = ('Lei 11.343/06, art. 11. Com fundamento no art. 198, §1º, I, do Código\\r\\n      Tributário Nacional e no artigo 1o., § 4o., da Lei\\r\\n'
        '      Complementar no 105/2001, e no art. 69 do Código Penal.')
s = s[:i] + novo + s[j:]
open(p, "w", encoding="utf-8", newline="").write(s)
print("ok")
