import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_mechanisms_html import SECTIONS, VIEWS, pct, MECH
from PIL import Image, ImageDraw, ImageFont
os.makedirs("/tmp/check", exist_ok=True)
try: F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
except Exception: F = ImageFont.load_default()
for sec in SECTIONS:
    v = VIEWS[sec["view"]]
    im = Image.open(os.path.join(MECH, sec["view"] + ".png")).convert("RGB")
    d = ImageDraw.Draw(im); W, H = im.size
    for i, (lab, sub, anc) in enumerate(sec["keys"], 1):
        L, T = pct(v, anc)
        x, y = L/100*W, T/100*H
        r = 20
        d.ellipse([x-r, y-r, x+r, y+r], fill=(247,248,248), outline=(20,24,27), width=3)
        d.text((x, y), str(i), fill=(20,24,27), anchor="mm", font=F)
    im.resize((900, int(900*H/W))).save(f"/tmp/check/{sec['view']}.png")
print("ok")
