# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Assets locais do img-to-html-flow: recorte da reference e remoção de fundo sólido.

  crop  REF OUT --bbox X Y W H [--pad N] [--min 512]
  key   IN OUT [--key RRGGBB] [--tol 60] [--soft 40] [--size W H] [--tint RRGGBB]
  sheet OUT IMG...          (folha de contato sobre xadrez, para conferir a alfa)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def crop(args) -> None:
    x, y, w, h = args.bbox
    with Image.open(args.ref) as im:
        p = args.pad
        box = (max(0, x - p), max(0, y - p), min(im.width, x + w + p), min(im.height, y + h + p))
        out = im.crop(box)
        if args.min and min(out.size) < args.min:  # o Flow recusa referência minúscula
            f = args.min / min(out.size)
            out = out.resize((round(out.width * f), round(out.height * f)), Image.LANCZOS)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        out.save(args.out)
    print(f"{args.out} {box} {out.width}x{out.height}")


def corner_key(im: Image.Image) -> tuple[int, int, int]:
    """Cor de fundo = mediana de faixas de 8 px nos quatro cantos."""
    w, h = im.size
    s = max(2, min(w, h) // 64)
    px = []
    for cx, cy in ((0, 0), (w - s, 0), (0, h - s), (w - s, h - s)):
        px += list(im.crop((cx, cy, cx + s, cy + s)).get_flattened_data())
    return tuple(sorted(c[i] for c in px)[len(px) // 2] for i in range(3))


def key(args) -> None:
    src = Image.open(args.inp)
    if src.mode in ("RGBA", "LA", "P") and src.convert("RGBA").getchannel("A").getextrema()[0] < 255:
        rgba = src.convert("RGBA")  # já veio com fundo transparente (ex.: ChatGPT): sem chroma
        if args.tint:
            t = tuple(int(args.tint[i:i + 2], 16) for i in (0, 2, 4))
            rgba = Image.merge("RGBA", (*Image.new("RGB", rgba.size, t).split(), rgba.getchannel("A")))
        return finish(rgba, args, "alpha")
    im = src.convert("RGB")
    k = tuple(int(args.key[i:i + 2], 16) for i in (0, 2, 4)) if args.key else corner_key(im)
    t0, t1 = args.tol, args.tol + args.soft
    kmax = max(range(3), key=lambda i: k[i])  # canal dominante do fundo, para tirar o vazamento
    out = []
    tint = tuple(int(args.tint[i:i + 2], 16) for i in (0, 2, 4)) if args.tint else None
    for r, g, b in im.get_flattened_data():
        d = ((r - k[0]) ** 2 + (g - k[1]) ** 2 + (b - k[2]) ** 2) ** 0.5
        a = 0 if d <= t0 else 255 if d >= t1 else round(255 * (d - t0) / (t1 - t0))
        if 0 < a < 255:  # borda: limita o canal do fundo ao maior dos outros dois
            c = [r, g, b]
            c[kmax] = min(c[kmax], max(c[i] for i in range(3) if i != kmax))
            r, g, b = c
        out.append((*tint, a) if tint else (r, g, b, a))
    rgba = Image.new("RGBA", im.size)
    rgba.putdata(out)
    finish(rgba, args, f"key=#{bytes(k).hex()}")


def finish(rgba: Image.Image, args, how: str) -> None:
    bbox = rgba.getchannel("A").getbbox()
    if not bbox:
        sys.exit(f"ERRO: tudo virou fundo ({how}); baixe --tol")
    rgba = rgba.crop(bbox)
    if args.size:
        rgba.thumbnail(tuple(args.size), Image.LANCZOS)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(args.out)
    print(f"{args.out} {how} {rgba.size[0]}x{rgba.size[1]}")


def sheet(args) -> None:
    ims = [Image.open(p).convert("RGBA") for p in args.imgs]
    cell = 160
    board = Image.new("RGBA", (cell * len(ims), cell), "white")
    d = ImageDraw.Draw(board)
    for x in range(0, board.width, 16):
        for y in range(0, cell, 16):
            if (x + y) // 16 % 2:
                d.rectangle([x, y, x + 15, y + 15], fill=(204, 204, 204, 255))
    for i, im in enumerate(ims):
        im.thumbnail((cell - 16, cell - 16), Image.LANCZOS)
        board.alpha_composite(im, (i * cell + (cell - im.width) // 2, (cell - im.height) // 2))
    board.save(args.out)
    print(args.out)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("crop")
    c.add_argument("ref", type=Path)
    c.add_argument("out", type=Path)
    c.add_argument("--bbox", nargs=4, type=int, required=True, metavar=("X", "Y", "W", "H"))
    c.add_argument("--pad", type=int, default=4)
    c.add_argument("--min", type=int, default=512, help="amplia até o menor lado ter N px (0 = não amplia)")
    c.set_defaults(fn=crop)
    k = sub.add_parser("key")
    k.add_argument("inp", type=Path)
    k.add_argument("out", type=Path)
    k.add_argument("--key", help="RRGGBB do fundo; padrão: mediana dos cantos")
    k.add_argument("--tol", type=float, default=60, help="distância RGB até onde é fundo puro")
    k.add_argument("--soft", type=float, default=40, help="faixa de transição da borda")
    k.add_argument("--tint", help="RRGGBB: repinta o desenho numa cor só (ícone monocromático), mantendo a alfa")
    k.add_argument("--size", nargs=2, type=int, metavar=("W", "H"), help="caber em WxH (mantém proporção)")
    k.set_defaults(fn=key)
    s = sub.add_parser("sheet")
    s.add_argument("out", type=Path)
    s.add_argument("imgs", nargs="+", type=Path)
    s.set_defaults(fn=sheet)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
