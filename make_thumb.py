"""Text-only RepPath thumbnail generator (cloud + local, Linux/Windows fonts).

make(headline, kicker, out_path, theme) -> 1920x1080 PNG.
theme "dark"  = brand-blue background, white text.
theme "light" = white background, brand-blue text.
No photos. Kicker optional (pass "" to omit).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BLUE_TOP = (26, 95, 180)
BLUE_BOT = (17, 63, 122)
WHITE = (255, 255, 255)
KICKER_COL = (191, 214, 244)

def _font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.truetype(ImageFont.load_default().path if hasattr(ImageFont.load_default(), "path") else paths[0], size)

BLACK_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\arialbd.ttf",
]
BOLD_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
]

def _gradient(top, bot):
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        px_row = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = px_row
    return img

def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def make(headline, kicker, out_path, theme="dark"):
    if theme == "light":
        img = Image.new("RGB", (W, H), WHITE)
        head_col = kick_col = rule_col = border = word_col = (26, 95, 180)
        sub_col = (120, 140, 165)
    else:
        img = _gradient(BLUE_TOP, BLUE_BOT)
        head_col = rule_col = border = word_col = WHITE
        kick_col = sub_col = KICKER_COL
    d = ImageDraw.Draw(img)
    margin = 130
    d.rectangle([48, 48, W - 48, H - 48], outline=border, width=3)
    y = 210
    if kicker:
        kf = _font(BOLD_FONTS, 46)
        x = margin
        for ch in kicker.upper():
            d.text((x, y), ch, font=kf, fill=kick_col)
            x += d.textlength(ch, font=kf) + 8
    max_w = W - margin * 2
    size = 168
    hf = _font(BLACK_FONTS, size)
    lines = _wrap(d, headline, hf, max_w)
    while len(lines) > 3 and size > 90:
        size -= 8
        hf = _font(BLACK_FONTS, size)
        lines = _wrap(d, headline, hf, max_w)
    line_h = int(size * 1.14)
    start_y = (H - line_h * len(lines)) // 2 + 40
    d.rectangle([margin, start_y - 46, margin + 120, start_y - 34], fill=rule_col)
    for i, ln in enumerate(lines):
        d.text((margin, start_y + i * line_h), ln, font=hf, fill=head_col)
    wf = _font(BOLD_FONTS, 52)
    d.text((margin, H - 210), "RepPath", font=wf, fill=word_col)
    sf = _font(BOLD_FONTS, 34)
    d.text((margin, H - 150), "reppath.com", font=sf, fill=sub_col)
    img.save(out_path, "PNG")
    return out_path
