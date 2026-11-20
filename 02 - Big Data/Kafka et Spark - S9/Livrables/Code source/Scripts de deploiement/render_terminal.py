# Auteur : DRISS Amine  —  ESIS 2 (2025-2026)

"""Rend un texte en image PNG façon terminal (pour les screenshots du rapport).

Usage : python -m scripts.render_terminal "<titre>" <fichier_texte> <sortie.png>
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = (30, 30, 30)
FG = (220, 220, 220)
BAR = (48, 48, 52)
TITLE_FG = (210, 210, 210)
ACCENT = (90, 200, 250)   # lignes ===, [tag]
GREEN = (130, 220, 140)   # OK / succès
DOTS = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]

FONT_SIZE = 16
LINE_H = FONT_SIZE + 6
PAD = 16
BAR_H = 34


def _font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "cour.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _line_color(line: str) -> tuple:
    stripped = line.strip()
    if stripped.startswith("===") or stripped.startswith("["):
        return ACCENT
    if any(k in line for k in ("OK", "passed", "REPRISE OK", "aucune perte", "Termine")):
        return GREEN
    return FG


def render(title: str, text: str, out: Path) -> None:
    font = _font(FONT_SIZE)
    title_font = _font(FONT_SIZE - 2)
    lines = text.replace("\t", "    ").split("\n")

    char_w = font.getlength("M")
    width = int(max((font.getlength(line) for line in lines), default=0) + 2 * PAD)
    width = max(width, int(char_w * 60), 600)
    height = BAR_H + 2 * PAD + LINE_H * len(lines)

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Barre de titre + pastilles
    draw.rectangle([0, 0, width, BAR_H], fill=BAR)
    for i, color in enumerate(DOTS):
        cx = 16 + i * 20
        draw.ellipse([cx, BAR_H // 2 - 6, cx + 12, BAR_H // 2 + 6], fill=color)
    draw.text((90, BAR_H // 2 - FONT_SIZE // 2), title, font=title_font, fill=TITLE_FG)

    y = BAR_H + PAD
    for line in lines:
        draw.text((PAD, y), line, font=font, fill=_line_color(line))
        y += LINE_H

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"[screenshot] {out}  ({width}x{height})")


def main() -> int:
    title, text_file, out = sys.argv[1], sys.argv[2], sys.argv[3]
    text = Path(text_file).read_text(encoding="utf-8")
    render(title, text, Path(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
