#!/usr/bin/env python3
"""Generator for the Republic of Valtessia passport spread (entry.png).

Deterministic: fixed geometry, fixed seed, no network, Pillow only.
Country (invented): Republic of Valtessia — a small island republic in the
Aurelian Strait. Capital Porto Aurelia. Languages: English / Valtessian
(shown as English / Valtessiano columns). Holder, dates and stamps are all
mutually consistent: passport issued 14 MAR 2021 in Porto Aurelia, every
stamp falls after issue and before expiry (14 MAR 2031).
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

random.seed(42)

W, H = 1024, 720
OUT = "entry.png"

FD = "/usr/share/fonts/truetype/dejavu/"
def font(name, size):
    return ImageFont.truetype(FD + name, size)

SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
MONO = "DejaVuSansMono.ttf"
MONO_B = "DejaVuSansMono-Bold.ttf"

# palette
PAPER = (243, 236, 218)
PAPER2 = (238, 229, 203)
TEAL = (18, 63, 82)          # deep Valtessian teal
TEAL2 = (31, 92, 110)
GOLD = (176, 141, 62)
GOLD_L = (203, 175, 105)
INK = (28, 32, 34)
GREY = (92, 96, 94)
LIGHT_LINE = (178, 168, 138)
GUIL = (196, 205, 188)
GUIL2 = (222, 205, 160)
RED = (158, 44, 44)
BLUE_STAMP = (36, 68, 140)
GREEN_STAMP = (30, 105, 74)
PURPLE_STAMP = (96, 52, 122)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img, "RGBA")

# ---------- background guilloche (procedural sine rosettes + waves) ----------
def guilloche(draw):
    for page_x in (18, 514):
        cx, cy = page_x + 240, 360
        # concentric wavy rosette, very pale
        for r in range(18, 250, 11):
            pts = []
            for a in range(0, 361, 3):
                rad = math.radians(a)
                rr = r + 5.0 * math.sin(rad * 7 + r * 0.11) + 3.0 * math.cos(rad * 3 - r * 0.05)
                pts.append((cx + rr * math.cos(rad) * 1.02, cy + rr * math.sin(rad) * 0.72))
            draw.line(pts, fill=GUIL + (70,), width=1)
        # horizontal wave bands
        for j, yy in enumerate(range(60, 690, 26)):
            pts = []
            for x in range(page_x + 6, page_x + 482):
                y = yy + 3.2 * math.sin((x - page_x) * 0.045 + j * 1.7) + 1.6 * math.sin((x - page_x) * 0.013 + j)
                pts.append((x, y))
            col = GUIL2 if j % 2 else GUIL
            draw.line(pts, fill=col + (52,), width=1)

guilloche(d)

# ---------- outer frame & centre fold ----------
d.rectangle([8, 8, W - 9, H - 9], outline=TEAL, width=3)
d.rectangle([14, 14, W - 15, H - 15], outline=GOLD, width=1)
# centre spine / fold shadow
for i in range(16):
    alpha = int(70 * (1 - i / 16))
    d.line([(506 + i, 14), (506 + i, H - 15)], fill=(120, 110, 84, alpha))
    d.line([(506 - i, 14), (506 - i, H - 15)], fill=(255, 252, 240, alpha // 2))
d.line([(512, 14), (512, H - 15)], fill=(140, 130, 100, 160), width=1)

# page panels
LEFT = (24, 24, 500, 696)
RIGHT = (524, 24, 1000, 696)
for box in (LEFT, RIGHT):
    d.rectangle(box, outline=(TEAL[0], TEAL[1], TEAL[2], 110), width=1)

def micro_line(x, y, x2, text, col=(120, 118, 96)):
    f = font(SANS, 5)
    s = text
    while d.textlength(s, font=f) < (x2 - x):
        s += text
    d.text((x, y), s[:120], font=f, fill=col)

# =========================================================
# RIGHT PAGE — DATA PAGE
# =========================================================
rx0, ry0, rx1, ry1 = RIGHT
# header band
d.rectangle([rx0 + 8, ry0 + 8, rx1 - 8, ry0 + 78], fill=TEAL)
d.rectangle([rx0 + 8, ry0 + 8, rx1 - 8, ry0 + 78], outline=GOLD, width=1)
# small emblem in header left (mini shield)
def mini_shield(cx, cy, s, outline=GOLD_L, fill=None):
    pts = [(cx - s, cy - s), (cx + s, cy - s), (cx + s, cy + s * 0.35),
           (cx, cy + s * 1.25), (cx - s, cy + s * 0.35)]
    if fill:
        d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=outline, width=2)
    # star above waves inside the shield
    d.ellipse([cx - 2, cy - s * 0.55, cx + 2, cy - s * 0.55 + 4], fill=outline)
    for k in range(2):
        yy = cy - 1 + k * 6
        d.arc([cx - s * 0.55, yy - 3, cx, yy + 5], 0, 180, fill=outline, width=1)
        d.arc([cx, yy - 3, cx + s * 0.55, yy + 5], 0, 180, fill=outline, width=1)

mini_shield(rx0 + 38, ry0 + 34, 13)
mini_shield(rx1 - 38, ry0 + 34, 13)
d.text(((rx0 + rx1) / 2, ry0 + 16), "REPUBLIC OF VALTESSIA", font=font(SERIF_B, 21), fill=(246, 240, 220), anchor="ma")
d.text(((rx0 + rx1) / 2, ry0 + 44), "REPUBBLICA VALTESSIANA  •  PASSPORT  •  PASSAPORTO", font=font(SANS_B, 9), fill=GOLD_L, anchor="ma")
micro_line(rx0 + 12, ry0 + 84, rx1 - 12, "REPUBLIC OF VALTESSIA • REPUBBLICA VALTESSIANA • ")

# --- coat of arms function (drawn from shapes); used in the lower panel ---
def coat_of_arms(acx, acy, s=30, flourish=True):
    shield = [(acx - s, acy - s), (acx + s, acy - s), (acx + s, acy + s * 0.4),
              (acx, acy + s * 1.35), (acx - s, acy + s * 0.4)]
    d.polygon(shield, fill=(232, 222, 188), outline=TEAL, width=2)
    d.line(shield + [shield[0]], fill=GOLD, width=1)
    sx, sy_, sr = acx, acy - 16, 7
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = sr if i % 2 == 0 else sr * 0.45
        star.append((sx + rr * math.cos(ang), sy_ + rr * math.sin(ang)))
    d.polygon(star, fill=GOLD)
    d.polygon([(acx - 5, acy + 12), (acx + 5, acy + 12), (acx + 3, acy - 8), (acx - 3, acy - 8)], fill=TEAL)
    d.rectangle([acx - 6, acy - 12, acx + 6, acy - 8], fill=RED)
    d.ellipse([acx - 2, acy - 11, acx + 2, acy - 7], fill=(255, 226, 120))
    for k in range(2):
        yy = acy + 18 + k * 7
        d.arc([acx - 20, yy - 4, acx, yy + 6], 0, 180, fill=TEAL2, width=2)
        d.arc([acx, yy - 4, acx + 20, yy + 6], 0, 180, fill=TEAL2, width=2)
    d.text((acx, acy + 48), "MARE  ET  FIDES", font=font(SERIF_B, 7), fill=TEAL, anchor="ma")
    if flourish:
        for sgn in (-1, 1):
            pts = []
            for t in range(0, 21):
                ang = t / 20 * math.pi * 0.9
                pts.append((acx + sgn * (44 + 8 * math.sin(ang)), acy - 18 + t * 3.4))
            d.line(pts, fill=GOLD, width=2)

# --- portrait (stylised, abstract — no real person) ---
px0, py0, px1, py1 = rx0 + 16, ry0 + 104, rx0 + 166, ry0 + 294
d.rectangle([px0, py0, px1, py1], fill=(226, 231, 222), outline=TEAL, width=2)
# portrait background waves
for j, yy in enumerate(range(py0 + 12, py1, 16)):
    pts = [(x, yy + 2.5 * math.sin(x * 0.06 + j * 1.3)) for x in range(px0 + 4, px1 - 3)]
    d.line(pts, fill=(170, 188, 178, 110), width=1)
cxp, cyp = (px0 + px1) // 2, py0 + 84
# hair (dark brown, to chin — framing the face)
d.ellipse([cxp - 44, cyp - 52, cxp + 44, cyp + 58], fill=(74, 52, 38))
# shoulders / top (teal dress)
d.polygon([(cxp - 52, py1 - 2), (cxp - 34, cyp + 62), (cxp - 14, cyp + 48), (cxp + 14, cyp + 48),
           (cxp + 34, cyp + 62), (cxp + 52, py1 - 2)], fill=(24, 84, 96))
d.polygon([(cxp - 14, cyp + 48), (cxp + 14, cyp + 48), (cxp, cyp + 66)], fill=(240, 232, 210))
# neck + face
d.rectangle([cxp - 10, cyp + 30, cxp + 10, cyp + 52], fill=(222, 178, 144))
d.ellipse([cxp - 31, cyp - 46, cxp + 31, cyp + 42], fill=(238, 196, 158))
# hair over top of face
d.pieslice([cxp - 33, cyp - 54, cxp + 33, cyp + 6], 180, 360, fill=(74, 52, 38))
d.rectangle([cxp - 33, cyp - 30, cxp - 24, cyp + 34], fill=(74, 52, 38))
d.rectangle([cxp + 24, cyp - 30, cxp + 33, cyp + 34], fill=(74, 52, 38))
# simple features
for ex in (-13, 13):
    d.ellipse([cxp + ex - 3, cyp - 6, cxp + ex + 3, cyp + 1], fill=(30, 28, 26))
    d.arc([cxp + ex - 7, cyp - 14, cxp + ex + 7, cyp - 4], 200, 340, fill=(90, 62, 40), width=2)
d.line([(cxp, cyp + 2), (cxp - 2, cyp + 14)], fill=(198, 148, 110), width=2)
d.arc([cxp - 8, cyp + 14, cxp + 8, cyp + 26], 20, 160, fill=(168, 74, 64), width=2)
# hair strand lines for texture
for hx in (-26, -17, 17, 26):
    d.line([(cxp + hx, cyp - 40), (cxp + hx * 1.05, cyp + 28)], fill=(96, 72, 52), width=1)
# soft cheek shading
d.ellipse([cxp - 24, cyp + 12, cxp - 12, cyp + 20], fill=(243, 205, 168))
d.ellipse([cxp + 12, cyp + 12, cxp + 24, cyp + 20], fill=(243, 205, 168))
# ghost (secondary) portrait, faint, lower-right of photo box
gx, gy = px1 - 30, py1 - 34
d.ellipse([gx - 13, gy - 16, gx + 13, gy + 14], outline=(90, 110, 104, 130), width=1)
d.arc([gx - 16, gy + 8, gx + 16, gy + 30], 180, 360, fill=(90, 110, 104, 130), width=1)
d.text((px0 + 6, py1 - 14), "VORNE", font=font(SANS, 6), fill=(90, 100, 94))

# --- data fields ---
fx = rx0 + 182
fy = ry0 + 100
def field(x, y, label_en, label_it, value, w_val=270, vsize=13):
    d.text((x, y), label_en, font=font(SANS_B, 7), fill=GREY)
    w_en = d.textlength(label_en, font=font(SANS_B, 7))
    d.text((x + w_en + 5, y + 1), "/ " + label_it, font=font(SANS, 6), fill=(140, 138, 122))
    d.text((x, y + 11), value, font=font(SANS_B, vsize), fill=INK)
    d.line([(x, y + 31), (x + w_val, y + 31)], fill=LIGHT_LINE, width=1)
    return y + 37

# top row: Type / Code / Passport No
ty = fy
d.text((fx, ty), "Type / Tipo", font=font(SANS_B, 7), fill=GREY)
d.text((fx, ty + 10), "P", font=font(SANS_B, 14), fill=INK)
d.text((fx + 52, ty), "Code / Codice", font=font(SANS_B, 7), fill=GREY)
d.text((fx + 52, ty + 10), "VTE", font=font(SANS_B, 14), fill=INK)
d.text((fx + 128, ty), "Passport No. / Passaporto N.", font=font(SANS_B, 7), fill=GREY)
d.text((fx + 128, ty + 10), "VT4829167", font=font(SANS_B, 14), fill=TEAL)
d.line([(fx, ty + 30), (fx + 282, ty + 30)], fill=LIGHT_LINE, width=1)

fy2 = ty + 36
fy2 = field(fx, fy2, "Surname", "Cognome", "VORNE", w_val=282, vsize=15)
fy2 = field(fx, fy2, "Given names", "Nomi", "ELENA MARIS", w_val=282, vsize=14)
fy2 = field(fx, fy2, "Nationality", "Cittadinanza", "VALTESSIAN", w_val=282, vsize=13)
# two-column row: DOB / Sex
d.text((fx, fy2), "Date of birth / Data di nascita", font=font(SANS_B, 7), fill=GREY)
d.text((fx, fy2 + 11), "12 JUN 1994", font=font(SANS_B, 13), fill=INK)
d.text((fx + 196, fy2), "Sex / Sesso", font=font(SANS_B, 7), fill=GREY)
d.text((fx + 196, fy2 + 11), "F", font=font(SANS_B, 13), fill=INK)
d.line([(fx, fy2 + 31), (fx + 282, fy2 + 31)], fill=LIGHT_LINE, width=1)
fy2 += 37
fy2 = field(fx, fy2, "Place of birth", "Luogo di nascita", "PORTO AURELIA", w_val=282, vsize=13)
# issue / expiry row (under portrait + fields, full width of data page)
iy = fy2 + 6
d.line([(rx0 + 16, iy - 6), (rx1 - 16, iy - 6)], fill=GOLD, width=1)
cols = [
    ("Date of issue / Data di rilascio", "14 MAR 2021", rx0 + 16),
    ("Date of expiry / Data di scadenza", "14 MAR 2031", rx0 + 172),
    ("Authority / Autorita", "PORTO AURELIA", rx0 + 328),
]
for lab, val, x in cols:
    en, _, it = lab.partition(" / ")
    d.text((x, iy), en, font=font(SANS_B, 7), fill=GREY)
    d.text((x, iy + 18), val, font=font(SANS_B, 12), fill=INK)
d.text((rx0 + 328, iy + 34), "Ministry of the Interior", font=font(SANS, 6), fill=GREY)
# holder signature (stylised squiggle)
sy = iy + 52
d.text((rx0 + 16, sy), "Holder's signature / Firma del titolare", font=font(SANS_B, 7), fill=GREY)
pts = []
for t in range(0, 61):
    x = rx0 + 22 + t * 2.1
    y = sy + 24 + 7 * math.sin(t * 0.42) * math.cos(t * 0.11) - (4 if 18 < t < 26 else 0)
    pts.append((x, y))
d.line(pts, fill=(26, 40, 88), width=2)
d.line([(rx0 + 16, sy + 36), (rx0 + 176, sy + 36)], fill=LIGHT_LINE, width=1)
# chip symbol
chx, chy = rx0 + 210, sy + 4
d.rectangle([chx, chy, chx + 34, chy + 26], outline=GOLD, width=2)
d.rectangle([chx + 10, chy + 7, chx + 24, chy + 19], outline=GOLD, width=1)
for yy in (chy + 4, chy + 12, chy + 20):
    d.line([(chx, yy), (chx + 10, yy)], fill=GOLD, width=1)
    d.line([(chx + 24, yy), (chx + 34, yy)], fill=GOLD, width=1)
d.text((chx + 44, chy + 2), "eMRTD", font=font(SANS_B, 8), fill=GREY)
d.text((chx + 44, chy + 13), "ICAO", font=font(SANS, 7), fill=GREY)

# --- telling detail: tide-window condition box ---
by = sy + 46
d.rectangle([rx0 + 16, by, rx1 - 16, by + 52], fill=(250, 245, 226), outline=TEAL, width=1)
d.rectangle([rx0 + 16, by, rx0 + 118, by + 52], fill=TEAL)
d.text((rx0 + 24, by + 8), "CONDITION", font=font(SANS_B, 9), fill=(246, 240, 220))
d.text((rx0 + 24, by + 22), "CONDIZIONE", font=font(SANS, 7), fill=GOLD_L)
d.text((rx0 + 24, by + 34), "TIDE WINDOW", font=font(SANS_B, 7), fill=(246, 240, 220))
d.text((rx0 + 126, by + 7),
       "Travel by sea: holder must hold a tide-window endorsement (p. 32)",
       font=font(SANS, 8), fill=INK)
d.text((rx0 + 126, by + 20),
       "and report to Harbour Control, Porto Aurelia, within 24 hours",
       font=font(SANS, 8), fill=INK)
d.text((rx0 + 126, by + 33),
       "of arrival.  Viaggi via mare: presentarsi al Controllo Portuale.",
       font=font(SANS, 8), fill=(70, 74, 72))

# --- lower panel: extra data fields, coat of arms, official seal ---
lyy = by + 64
d.line([(rx0 + 16, lyy - 8), (rx1 - 16, lyy - 8)], fill=GOLD, width=1)
def field2(x, y, label, value, w_val=150):
    d.text((x, y), label, font=font(SANS_B, 7), fill=GREY)
    d.text((x, y + 11), value, font=font(SANS_B, 11), fill=INK)
    d.line([(x, y + 29), (x + w_val, y + 29)], fill=LIGHT_LINE, width=1)

field2(rx0 + 16, lyy, "Height / Altezza", "168 CM")
field2(rx0 + 182, lyy, "Colour of eyes / Occhi", "BROWN")
field2(rx0 + 16, lyy + 35, "Residence / Residenza", "PORTO AURELIA")
field2(rx0 + 182, lyy + 35, "Personal No. / Codice pers.", "940612-4418")
# coat of arms, crisp, on the right of the lower panel
coat_of_arms(rx1 - 56, lyy + 26, s=20, flourish=False)
# embossed official seal overlapping the portrait's lower corner (as on real data pages)
seal = Image.new("RGBA", (124, 124), (0, 0, 0, 0))
sd = ImageDraw.Draw(seal)
sd.ellipse([6, 6, 118, 118], outline=(150, 118, 40, 165), width=3)
sd.ellipse([15, 15, 109, 109], outline=(150, 118, 40, 105), width=1)
sd.text((62, 32), "REPUBLIC OF", font=font(SANS_B, 8), fill=(120, 92, 30, 180), anchor="ma")
sd.text((62, 45), "VALTESSIA", font=font(SANS_B, 10), fill=(120, 92, 30, 190), anchor="ma")
sd.text((62, 63), "PORTO AURELIA", font=font(SANS, 6), fill=(120, 92, 30, 165), anchor="ma")
sd.text((62, 75), "14 MAR 2021", font=font(SANS_B, 7), fill=(120, 92, 30, 180), anchor="ma")
seal = seal.rotate(-9, expand=False, resample=Image.BICUBIC)
img.paste(seal, (583, 226), seal)
d = ImageDraw.Draw(img, "RGBA")

# --- MRZ ---
my = ry1 - 62
d.rectangle([rx0 + 8, my, rx1 - 8, ry1 - 8], fill=(250, 248, 240), outline=(150, 144, 118), width=1)
line1 = "P<VTEVORNE<<ELENA<MARIS<<<<<<<<<<<<<<<<<<<<"
line2 = "VT4829167<8VTE9406125F3103148<<<<<<<<<<<<<06"
line1 = (line1 + "<" * 44)[:44]
line2 = (line2 + "<" * 44)[:44]
d.text((rx0 + 18, my + 7), line1, font=font(MONO_B, 13), fill=(20, 20, 20))
d.text((rx0 + 18, my + 29), line2, font=font(MONO_B, 13), fill=(20, 20, 20))
d.text((rx1 - 16, ry0 + 92), "6", font=font(SANS, 8), fill=GREY, anchor="ra")

# =========================================================
# LEFT PAGE — VISAS & STAMPS
# =========================================================
lx0, ly0, lx1, ly1 = LEFT
d.text((lx0 + 14, ly0 + 12), "VISAS  •  VISTI", font=font(SERIF_B, 15), fill=TEAL)
d.text((lx0 + 14, ly0 + 36), "Arrival and departure stamps — neighbouring states of the Aurelian Strait",
       font=font(SANS, 7), fill=GREY)
d.line([(lx0 + 14, ly0 + 52), (lx1 - 14, ly0 + 52)], fill=GOLD, width=1)
micro_line(lx0 + 14, ly0 + 56, lx1 - 14, "VALTESSIA • VISTI • VISAS • ")
d.text((lx1 - 14, ly0 + 12), "7", font=font(SANS, 8), fill=GREY, anchor="ra")

# observations (printed, part of the document — reveals the place)
oy = ly0 + 68
d.rectangle([lx0 + 14, oy, lx1 - 14, oy + 56], outline=TEAL, width=1)
d.text((lx0 + 22, oy + 7), "OBSERVATIONS  /  OSSERVAZIONI", font=font(SANS_B, 8), fill=TEAL)
d.text((lx0 + 22, oy + 22), "This passport contains tide tables for the Aurelian Strait (pp. 30–32).",
       font=font(SANS, 7.5), fill=INK)
d.text((lx0 + 22, oy + 34), "The holder is a registered harbour resident of Porto Aurelia.",
       font=font(SANS, 7.5), fill=INK)
d.text((lx0 + 22, oy + 46), "Emergency contact: Harbour Office, Porto Aurelia — Tel. +991 2 441 880",
       font=font(SANS, 7), fill=GREY)

def stamp_rect(cx, cy, w_, h_, angle, color, lines, sub=None):
    """Draw a rotated rectangular border stamp on its own layer, then paste."""
    layer = Image.new("RGBA", (w_ + 30, h_ + 30), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([8, 8, w_ + 22, h_ + 22], radius=8, outline=color + (205,), width=3)
    ld.rounded_rectangle([14, 14, w_ + 16, h_ + 16], radius=5, outline=color + (130,), width=1)
    y = 22
    for i, (txt, sz, bold) in enumerate(lines):
        f = font(SANS_B if bold else SANS, sz)
        ld.text(((w_ + 30) / 2, y), txt, font=f, fill=color + (215,), anchor="ma")
        y += sz + 5
    if sub:
        ld.text(((w_ + 30) / 2, y + 1), sub, font=font(SANS, 7), fill=color + (180,), anchor="ma")
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

def stamp_round(cx, cy, r, angle, color, top, mid, bot):
    layer = Image.new("RGBA", (r * 2 + 30, r * 2 + 30), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    c = r + 15
    ld.ellipse([15, 15, 15 + r * 2, 15 + r * 2], outline=color + (205,), width=3)
    ld.ellipse([21, 21, 9 + r * 2, 9 + r * 2], outline=color + (120,), width=1)
    ld.text((c, c - 30), top, font=font(SANS_B, 9), fill=color + (215,), anchor="ma")
    ld.text((c, c - 12), mid, font=font(SANS_B, 12), fill=color + (225,), anchor="ma")
    ld.text((c, c + 8), bot, font=font(SANS, 8), fill=color + (190,), anchor="ma")
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

# visa sticker (Selvarra) — issued before the Sep 2023 trip, after passport issue
vx0, vy0, vx1, vy1 = lx0 + 14, ly0 + 140, lx0 + 238, ly0 + 248
d.rectangle([vx0, vy0, vx1, vy1], fill=(233, 238, 246), outline=BLUE_STAMP, width=2)
d.rectangle([vx0, vy0, vx1, vy0 + 24], fill=BLUE_STAMP)
d.text(((vx0 + vx1) / 2, vy0 + 5), "REPUBLIC OF SELVARRA  —  VISITOR VISA", font=font(SANS_B, 8), fill=(245, 247, 252), anchor="ma")
visa_rows = [
    ("Visa No.", "SV-2023-88417"),
    ("Holder", "VORNE, ELENA MARIS"),
    ("Valid", "01 SEP 2023 — 01 MAR 2024"),
    ("Entries", "SINGLE  •  Stay max 30 days"),
    ("Issued at", "VELMORA  •  Fee paid: 25 selvars"),
]
yy = vy0 + 32
for k, v in visa_rows:
    d.text((vx0 + 10, yy), k, font=font(SANS_B, 7), fill=GREY)
    d.text((vx0 + 62, yy - 1), v, font=font(SANS_B, 8), fill=INK)
    yy += 15

# stamps — chronological, all after 14 MAR 2021 issue, before 14 MAR 2031 expiry
stamp_rect(lx0 + 344, ly0 + 192, 150, 62, -7, BLUE_STAMP,
           [("KINGDOM OF KORDAVIA", 9, True), ("BRANKOV AIRPORT", 8, False), ("ARRIVAL  03 JUN 2022", 10, True)],
           sub="Admitted — 90 days")
stamp_rect(lx0 + 118, ly0 + 316, 150, 62, 5, PURPLE_STAMP,
           [("KINGDOM OF KORDAVIA", 9, True), ("BRANKOV AIRPORT", 8, False), ("DEPARTURE  11 JUN 2022", 10, True)])
stamp_round(lx0 + 348, ly0 + 322, 56, 9, GREEN_STAMP, "SELVARRA", "18 SEP 2023", "VELMORA • ARRIVAL")
stamp_rect(lx0 + 122, ly0 + 446, 156, 62, -4, GREEN_STAMP,
           [("REPUBLIC OF SELVARRA", 9, True), ("VELMORA PORT", 8, False), ("DEPARTURE  27 SEP 2023", 10, True)])
stamp_round(lx0 + 350, ly0 + 452, 56, -11, RED, "TARNWICK", "09 MAY 2024", "FREE PORT • ARRIVAL")
# small Valtessia exit stamp (home border, ties history together)
stamp_rect(lx0 + 238, ly0 + 566, 168, 56, 3, TEAL2,
           [("VALTESSIA — PORTO AURELIA", 9, True), ("EXIT BY SEA  07 MAY 2024", 10, True)],
           sub="Tide-window endorsement checked")

# faint page furniture
d.text((lx0 + 14, ly1 - 22), "This page is reserved for visas and stamps of competent authorities.",
       font=font(SANS, 7), fill=GREY)
micro_line(lx0 + 14, ly1 - 34, lx1 - 14, "REPUBLIC OF VALTESSIA • DO NOT WRITE OUTSIDE THE BOXES • ")

img.save(OUT, "PNG", optimize=True)
print("saved", OUT, img.size)
