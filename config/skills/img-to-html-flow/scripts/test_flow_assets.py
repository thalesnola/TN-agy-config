# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Checagem do `key`: ícone roxo sobre verde com ruído vira PNG com alfa, sem halo verde."""
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

here = Path(__file__).with_name("flow_assets.py")
with tempfile.TemporaryDirectory() as tmp:
    src, out = Path(tmp, "in.png"), Path(tmp, "out.png")
    random.seed(1)
    im = Image.new("RGB", (256, 256))
    im.putdata([(random.randint(0, 25), random.randint(225, 255), random.randint(0, 25)) for _ in range(256 * 256)])
    ImageDraw.Draw(im).ellipse([64, 64, 192, 192], fill=(93, 85, 218))
    im.save(src)
    subprocess.run([sys.executable, str(here), "key", str(src), str(out)], check=True)
    res = Image.open(out)
    assert res.mode == "RGBA" and 126 <= res.width <= 131, res.size  # aparado ao círculo
    cx = res.width // 2
    assert res.getpixel((cx, cx)) == (93, 85, 218, 255)
    assert res.getpixel((0, 0))[3] == 0  # canto fora do círculo
    edge = [p for p in res.get_flattened_data() if 0 < p[3] < 255]
    assert all(g <= max(r, b) for r, g, b, _ in edge), "vazamento de verde na borda"
    subprocess.run([sys.executable, str(here), "key", str(src), str(out), "--tint", "645AB8"], check=True)
    assert {p[:3] for p in Image.open(out).get_flattened_data() if p[3]} == {(0x64, 0x5A, 0xB8)}
    small = Path(tmp, "small.png")
    subprocess.run([sys.executable, str(here), "crop", str(src), str(small), "--bbox", "100", "100", "30", "30"], check=True)
    assert min(Image.open(small).size) == 512
    # PNG que já chega com alfa (ChatGPT): apara e repinta, sem chroma
    alpha_in, alpha_out = Path(tmp, "alpha.png"), Path(tmp, "alpha_out.png")
    a_im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(a_im).rectangle([50, 60, 149, 139], fill=(10, 200, 10, 255))  # verde de propósito
    a_im.save(alpha_in)
    subprocess.run([sys.executable, str(here), "key", str(alpha_in), str(alpha_out), "--tint", "3A3B42"], check=True)
    r = Image.open(alpha_out)
    assert r.size == (100, 80) and r.getpixel((50, 40)) == (0x3A, 0x3B, 0x42, 255), (r.size, r.getpixel((50, 40)))
print("ok")
