"""Generator for the Republic of Tavora passport spread.

Deterministic: Python + Pillow only. Run: python3 draw.py -> entry.png
All printed fields and the MRZ are derived from the constants below so
they cannot disagree with each other.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- identity
COUNTRY = "REPUBLIC OF TAVORA"
COUNTRY_TAVORAN = "REPUBLIKA NAMI TAVORA"
CODE = "TAV"
SURNAME = "VOSS"
GIVEN = "MAREN ILSE"
NATIONALITY = "TAVORAN"
DOB_PRINT = "14 MAR 1992"
DOB_MRZ = "920314"
POB = "PORT ANSELM"
SEX = "F"
DOC_NO = "TV4829176"
ISSUE_PRINT = "20 MAY 2021"
EXPIRY_PRINT = "19 MAY 2031"
EXPIRY_MRZ = "310519"
AUTHORITY = "MINISTRY OF THE INTERIOR, PORT ANSELM"
PERSONAL_NO = "920314771"

W, H = 1024, 720
MID = W // 2

INK = (28, 38, 58)
FAINT = (110, 118, 132)
PAPER = (247, 243, 232)
NAVY = (32, 52, 96)
BLUE_INK = (38, 64, 140)
RED_INK = (148, 38, 52)
GREEN_INK = (30, 96, 74)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def f_sans(size):
    return font("DejaVuSans.ttf", size)


def f_sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def f_serif(size):
    return font("DejaVuSerif.ttf", size)


def f_serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def f_mono(size):
    return font("DejaVuSansMono.ttf", size)


def f_mono_b(size):
    return font("DejaVuSansMono-Bold.ttf", size)


# ---------------------------------------------------------------- MRZ
def check_digit(data):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(data):
        if ch.isdigit():
            v = int(ch)
        elif ch == "<":
            v = 0
        else:
            v = ord(ch) - 55  # A=10
        total += v * weights[i % 3]
    return str(total % 10)


def build_mrz():
    line1 = ("P<" + CODE + SURNAME + "<<" + GIVEN.replace(" ", "<")).ljust(44, "<")
    personal_field = PERSONAL_NO.ljust(14, "<")
    body = (
        DOC_NO + check_digit(DOC_NO)
        + CODE
        + DOB_MRZ + check_digit(DOB_MRZ)
        + SEX
        + EXPIRY_MRZ + check_digit(EXPIRY_MRZ)
        + personal_field + check_digit(personal_field)
    )
    line2 = body + check_digit(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- helpers
def centred(draw, cx, y, text, fnt, fill=INK):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((cx - (bbox[2] - bbox[0]) / 2, y), text, font=fnt, fill=fill)


def field(draw, x, y, label, value, vf=None):
    draw.text((x, y), label, font=f_sans(8), fill=FAINT)
    draw.text((x, y + 11), value, font=vf or f_sans_b(13), fill=INK)


def guilloche(draw, box, colour=(226, 221, 203)):
    x0, y0, x1, y1 = box
    for k in range(9):
        pts = []
        for x in range(x0, x1 + 1, 8):
            y = (y0 + y1) / 2 + math.sin((x - x0) / 46.0 + k * 0.9) * (10 + k * 7)
            if y0 <= y <= y1:
                pts.append((x, y))
        if len(pts) > 1:
            draw.line(pts, fill=colour, width=1)


def draw_emblem(draw, cx, cy):
    """Shield with three tide-waves and a gull — drawn, restrained."""
    w, h = 54, 62
    x0, y0, x1, y1 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    draw.polygon(
        [(x0, y0), (x1, y0), (x1, y0 + 34), (cx, y1), (x0, y0 + 34)],
        outline=NAVY, width=2,
    )
    draw.line([(x0, y0 + 20), (x1, y0 + 20)], fill=NAVY, width=1)
    # gull: two arcs
    draw.arc([cx - 13, y0 + 5, cx - 1, y0 + 17], 200, 330, fill=NAVY, width=2)
    draw.arc([cx + 1, y0 + 5, cx + 13, y0 + 17], 210, 340, fill=NAVY, width=2)
    # three waves
    for i, yy in enumerate((y0 + 30, y0 + 39, y0 + 48)):
        pts = []
        for x in range(x0 + 7, x1 - 6):
            pts.append((x, yy + math.sin((x - x0) / 5.5 + i) * 2.2))
        draw.line(pts, fill=NAVY, width=2)


def make_stamp(w, h, draw_fn):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, w, h)
    return layer


def paste_rotated(base, layer, cx, cy, angle):
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    base.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), rot)


# ---------------------------------------------------------------- stamps
def stamp_norhaven_entry(d, w, h):
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=10, outline=BLUE_INK + (215,), width=3)
    centred(d, w / 2, 10, "KINGDOM OF NORHAVEN", f_sans_b(13), BLUE_INK)
    centred(d, w / 2, 30, "KESTREL HARBOUR FERRY TERMINAL", f_sans(9), BLUE_INK)
    centred(d, w / 2, 47, "ENTRY  14 JUN 2022", f_sans_b(14), BLUE_INK)


def stamp_norhaven_exit(d, w, h):
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=10, outline=BLUE_INK + (200,), width=3)
    centred(d, w / 2, 10, "KINGDOM OF NORHAVEN", f_sans_b(13), BLUE_INK)
    centred(d, w / 2, 30, "KESTREL HARBOUR FERRY TERMINAL", f_sans(9), BLUE_INK)
    centred(d, w / 2, 47, "EXIT  21 JUN 2022", f_sans_b(14), BLUE_INK)


def stamp_bresk_entry(d, w, h):
    d.ellipse([3, 3, w - 4, h - 4], outline=RED_INK + (210,), width=3)
    centred(d, w / 2, 16, "REPUBLIC OF BRESK", f_sans_b(12), RED_INK)
    centred(d, w / 2, 35, "VEYRA CAUSEWAY", f_sans(9), RED_INK)
    centred(d, w / 2, 50, "ENTRY  03 OCT 2023", f_sans_b(13), RED_INK)


def stamp_luthmere_entry(d, w, h):
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=6, outline=GREEN_INK + (210,), width=3)
    centred(d, w / 2, 10, "PRINCIPALITY OF LUTHMERE", f_sans_b(12), GREEN_INK)
    centred(d, w / 2, 30, "PORT SABLE AIRPORT", f_sans(9), GREEN_INK)
    centred(d, w / 2, 47, "ENTRY  18 FEB 2025", f_sans_b(14), GREEN_INK)


def stamp_luthmere_exit(d, w, h):
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=6, outline=GREEN_INK + (195,), width=3)
    centred(d, w / 2, 10, "PRINCIPALITY OF LUTHMERE", f_sans_b(12), GREEN_INK)
    centred(d, w / 2, 30, "PORT SABLE AIRPORT", f_sans(9), GREEN_INK)
    centred(d, w / 2, 47, "EXIT  25 FEB 2025", f_sans_b(14), GREEN_INK)


# ---------------------------------------------------------------- main
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # faint security pattern on both pages
    guilloche(d, (18, 120, MID - 18, 560))
    guilloche(d, (MID + 18, 120, W - 18, 640))

    # page edges + centre spine
    d.rectangle([0, 0, W - 1, H - 1], outline=(178, 170, 148), width=2)
    for i in range(26):
        alpha = int(70 * (1 - i / 26))
        d.line([(MID - 13 + i, 0), (MID - 13 + i, H)], fill=(120, 112, 92, alpha))
        d.line([(MID + 13 - i, 0), (MID + 13 - i, H)], fill=(120, 112, 92, alpha))

    # ============================================================ DATA PAGE
    lx, rx = 30, MID - 28
    draw_emblem(d, 66, 62)
    centred(d, 276, 26, COUNTRY, f_serif_b(19), NAVY)
    centred(d, 276, 52, COUNTRY_TAVORAN, f_sans(10), FAINT)
    centred(d, 276, 72, "PASSPORT  ·  PASOS", f_sans_b(13), INK)
    d.line([(lx, 100), (rx, 100)], fill=NAVY, width=2)
    d.line([(lx, 104), (rx, 104)], fill=NAVY, width=1)

    # photo: 35:45 ratio box, photoreal portrait composited, thin border
    px, py, pw, ph = 34, 128, 140, 180
    portrait = Image.open(os.path.join(HERE, "portrait.png")).convert("RGB")
    # centre-crop to 35:45 then resize
    tw, th = pw * 3, ph * 3
    scale = max(tw / portrait.width, th / portrait.height)
    rs = portrait.resize((int(portrait.width * scale) + 1,
                          int(portrait.height * scale) + 1), Image.LANCZOS)
    ox = (rs.width - tw) // 2
    oy = max(0, (rs.height - th) // 5)  # bias crop upward: keep head + shoulders
    face = rs.crop((ox, oy, ox + tw, oy + th)).resize((pw, ph), Image.LANCZOS)
    img.paste(face, (px, py))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([px, py, px + pw, py + ph], outline=INK, width=2)
    # faint ghost image at right, as on real data pages
    ghost = face.resize((54, 70)).convert("L").point(lambda v: 255 - int((255 - v) * 0.18))
    img.paste(Image.merge("RGB", (ghost, ghost, ghost)), (424, 300))
    d = ImageDraw.Draw(img, "RGBA")

    fx = 196
    field(d, fx, 122, "TYPE / VRSTA", "P")
    field(d, fx + 110, 122, "CODE / KOD", CODE)
    field(d, fx + 205, 122, "PASSPORT No. / ST. PASOSA", DOC_NO)
    field(d, fx, 160, "SURNAME / PRIIMEK", SURNAME)
    field(d, fx, 198, "GIVEN NAMES / IMENA", GIVEN)
    field(d, fx, 236, "NATIONALITY / DRZAVLJANSTVO", NATIONALITY)
    field(d, fx, 274, "DATE OF BIRTH / DATUM ROJSTVA", DOB_PRINT)
    field(d, fx + 205, 274, "SEX / SPOL", SEX)
    field(d, fx, 312, "PLACE OF BIRTH / KRAJ ROJSTVA", POB)
    field(d, fx, 350, "PERSONAL No. / OSEBNA ST.", PERSONAL_NO)
    field(d, fx, 388, "DATE OF ISSUE / DATUM IZDAJE", ISSUE_PRINT)
    field(d, fx + 180, 388, "DATE OF EXPIRY / VELJA DO", EXPIRY_PRINT)
    field(d, 34, 430, "ISSUING AUTHORITY / IZDAL ORGAN", AUTHORITY, vf=f_sans_b(11))

    # signature
    d.line([(34, 512), (220, 512)], fill=FAINT, width=1)
    d.text((34, 518), "HOLDER'S SIGNATURE / PODPIS", font=f_sans(8), fill=FAINT)
    # cursive-style signature strokes ("M. Voss")
    sig = [
        (40, 506), (46, 490), (52, 504), (58, 488), (64, 503), (70, 498),
        (76, 506), (86, 494), (94, 492), (100, 500), (106, 506), (114, 496),
        (122, 494), (128, 502), (136, 497), (146, 495), (156, 500),
        (166, 498), (176, 503),
    ]
    d.line(sig, fill=(40, 44, 80), width=2, joint="curve")

    # MRZ band
    d.rectangle([18, 566, MID - 14, 700], fill=(238, 233, 216), outline=(196, 188, 164))
    line1, line2 = build_mrz()
    mf = f_mono_b(16)
    d.text((30, 596), line1, font=mf, fill=(20, 20, 20))
    d.text((30, 632), line2, font=mf, fill=(20, 20, 20))
    d.text((30, 574), "MACHINE READABLE ZONE", font=f_sans(7), fill=FAINT)

    # ============================================================ VISAS PAGE
    vx0, vx1 = MID + 30, W - 30
    centred(d, (vx0 + vx1) / 2 + 15, 30, "VISAS", f_serif_b(20), NAVY)
    centred(d, (vx0 + vx1) / 2 + 15, 60, "VIZE  ·  VISUMS", f_sans(10), FAINT)
    d.line([(vx0, 88), (vx1, 88)], fill=NAVY, width=2)
    d.line([(vx0, 92), (vx1, 92)], fill=NAVY, width=1)
    d.text((vx1 - 24, 660), "12", font=f_sans(11), fill=FAINT)

    base = img.convert("RGBA")
    paste_rotated(base, make_stamp(300, 78, stamp_norhaven_entry), 672, 150, -4)
    paste_rotated(base, make_stamp(300, 78, stamp_norhaven_exit), 800, 238, 3)

    # --- telling detail: Bresk visa sticker with tidal-causeway condition.
    # Tavora and Bresk are joined by a causeway that floods at high tide;
    # the visa is only usable in the posted low-tide windows.
    sx, sy, sw, sh = MID + 44, 292, 300, 148
    sticker = Image.new("RGBA", (sw, sh), (226, 238, 218, 255))
    sd = ImageDraw.Draw(sticker)
    sd.rectangle([2, 2, sw - 3, sh - 3], outline=GREEN_INK + (255,), width=2)
    sd.rectangle([7, 7, sw - 8, sh - 8], outline=GREEN_INK + (160,), width=1)
    sd.text((16, 12), "REPUBLIC OF BRESK — VISA", font=f_sans_b(13), fill=GREEN_INK)
    sd.text((16, 36), "CONSULATE OF BRESK, PORT ANSELM", font=f_sans(8), fill=INK)
    sd.text((16, 54), "ISSUED  12 SEP 2023", font=f_sans_b(10), fill=INK)
    sd.text((16, 72), "VALID  01 OCT 2023 — 31 MAR 2024 · SINGLE ENTRY", font=f_sans_b(9), fill=INK)
    sd.text((16, 94), "CONDITION: VEYRA CAUSEWAY CROSSINGS ONLY", font=f_sans_b(10), fill=RED_INK)
    sd.text((16, 112), "WITHIN POSTED LOW-TIDE WINDOWS.", font=f_sans_b(10), fill=RED_INK)
    sd.text((16, 130), "STAMPED TIDE TABLE TO BE CARRIED.", font=f_sans(8), fill=INK)
    base.paste(sticker.rotate(1.5, expand=True, resample=Image.BICUBIC),
               (sx, sy), sticker.rotate(1.5, expand=True, resample=Image.BICUBIC))

    paste_rotated(base, make_stamp(244, 84, stamp_bresk_entry), 842, 478, -6)
    paste_rotated(base, make_stamp(300, 78, stamp_luthmere_entry), 660, 544, 3)
    paste_rotated(base, make_stamp(300, 78, stamp_luthmere_exit), 812, 606, -3)

    out = base.convert("RGB")
    out.save(os.path.join(HERE, "entry.png"), optimize=True)
    print("MRZ1:", line1)
    print("MRZ2:", line2)
    print("wrote entry.png", out.size)


if __name__ == "__main__":
    main()
