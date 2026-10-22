#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""玻璃拟态 / 极光风格的 GitHub 主页长图。

    py -3 scripts/build.py
"""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BASE = "#080D1A"
INK = "#F2F6FF"
SUB = "#9FB0CC"
DIM = "#6F82A0"
MINT = "#5EEAD4"
IRIS = "#818CF8"
PINK = "#F472B6"

SANS = '"PingFang SC", "Microsoft YaHei", "Inter", "Noto Sans SC", sans-serif'

DESK = dict(w=1200, pad=56, gap=24, two=True, name=84, sub=19,
            body=28, lh=44, small=20, smalllh=31,
            h=32, label=12.5, cardpad=34)
MOB = dict(w=680, pad=24, gap=16, two=False, name=58, sub=15,
           body=21, lh=34, small=16, smalllh=26,
           h=24, label=11, cardpad=26)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chw(c, size):
    if ord(c) < 128:
        if c in "ilj|.,:;'!()[]": return size * 0.32
        if c in "mwMW@": return size * 0.86
        if c.isupper(): return size * 0.66
        return size * 0.55
    return size * 1.0


def tw(s, size):
    return sum(chw(c, size) for c in s)


def wrap(text, maxw, size):
    toks, buf = [], ""
    for c in text:
        if ord(c) < 128 and not c.isspace():
            buf += c
        else:
            if buf:
                toks.append(buf)
                buf = ""
            toks.append(" " if c.isspace() else c)
    if buf:
        toks.append(buf)
    lines, cur = [], ""
    nbb = "，。、；：？！）」』】》%,.;:?!)]}"
    for t in toks:
        if t == " " and not cur:
            continue
        if tw(cur + t, size) <= maxw or (t and t[0] in nbb and cur):
            cur += t
        else:
            if cur.strip():
                lines.append(cur.rstrip())
            cur = "" if t == " " else t
    if cur.strip():
        lines.append(cur.rstrip())
    return lines or [""]


DEFS = f'''<defs>
  <radialGradient id="b1" cx="0.15" cy="0.05" r="0.6">
    <stop offset="0" stop-color="{MINT}" stop-opacity="0.42"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="b2" cx="0.9" cy="0.25" r="0.55">
    <stop offset="0" stop-color="{IRIS}" stop-opacity="0.46"/><stop offset="1" stop-color="{IRIS}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="b3" cx="0.6" cy="1" r="0.6">
    <stop offset="0" stop-color="{PINK}" stop-opacity="0.30"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.075"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.025"/>
  </linearGradient>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{MINT}"/><stop offset="1" stop-color="{IRIS}"/>
  </linearGradient>
  <filter id="orb" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="90"/>
  </filter>
  <filter id="blur" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="60"/>
  </filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="16" stdDeviation="26" flood-color="#000000" flood-opacity="0.45"/>
  </filter>
  <style>
    text {{ font-family: {SANS}; }}
  </style>
</defs>'''


def card(x, y, w, h):
    return (f'<g filter="url(#shadow)">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="url(#glass)" '
            f'stroke="#ffffff" stroke-opacity="0.13"/></g>'
            f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="1.5" rx="1" fill="#ffffff" opacity="0.16"/>')


def label(x, y, text, color=DIM):
    return (f'<circle cx="{x+3.5}" cy="{y-4}" r="3" fill="{MINT}" opacity="0.9"/>'
            f'<text x="{x+16}" y="{y}" font-size="11.5" letter-spacing="3.4" fill="{color}">{esc(text)}</text>')


def build(c, V):
    W, P, G = V["w"], V["pad"], V["gap"]
    inner = W - 2 * P
    parts = []

    # ── 头部 ──
    y = 72 if V["two"] else 52
    parts.append(f'<text x="{P}" y="{y}" font-size="11.5" letter-spacing="5" fill="{DIM}">'
                 f'{esc(c["latin"])}　·　2026</text>')
    ny = y + (92 if V["two"] else 66)
    parts.append(f'<text x="{P-3}" y="{ny}" font-size="{V["name"]}" font-weight="700" '
                 f'letter-spacing="4" fill="{INK}">{esc(c["name"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+34}" font-size="{V["sub"]}" fill="{SUB}">'
                 f'{esc(c["role"])}　·　{esc(c["handle"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+72}" font-size="{V["sub"]}" fill="{DIM}">'
                 f'{esc(c["poem"])}</text>')

    y = ny + (124 if V["two"] else 104)

    if V["two"]:
        c1 = int(inner * 0.545)
        c2 = inner - c1 - G
        x1, x2 = P, P + c1 + G

        a_parts, a_h = card_about(c, x1, y, c1, V)
        b_parts, b_h = card_now(c, x2, y, c2, V)
        rh = max(a_h, b_h)
        parts.append(card(x1, y, c1, rh))
        parts.append(card(x2, y, c2, rh))
        parts.extend(a_parts)
        parts.extend(b_parts)

        y2 = y + rh + G
        w_parts, w_h = card_work(c, x1, y2, c1, V)
        k_parts, k_h = card_contact(c, x2, y2, c2, V)
        rh2 = max(w_h, k_h)
        parts.append(card(x1, y2, c1, rh2))
        parts.append(card(x2, y2, c2, rh2))
        parts.extend(w_parts)
        parts.extend(k_parts)
        H = y2 + rh2 + (86 if V["two"] else 70)
    else:
        yy = y
        for fn in (card_about, card_now, card_work, card_contact):
            p, h = fn(c, P, yy, inner, V)
            parts.append(card(P, yy, inner, h))
            parts.extend(p)
            yy += h + G
        H = yy + 56

    bg = (f'<rect width="{W}" height="{H}" fill="{BASE}"/>'
          f'<circle cx="{W*0.10}" cy="{H*0.02}" r="{W*0.30}" fill="{MINT}" opacity="0.22" filter="url(#orb)"/>'
          f'<circle cx="{W*0.96}" cy="{H*0.18}" r="{W*0.27}" fill="{IRIS}" opacity="0.24" filter="url(#orb)"/>'
          f'<circle cx="{W*0.62}" cy="{H*1.04}" r="{W*0.32}" fill="{PINK}" opacity="0.16" filter="url(#orb)"/>'
          f'<rect x="{W*0.5-1}" y="0" width="2" height="{H}" fill="none"/>')

    tail = (f'<text x="{P}" y="{H-34}" font-size="11" letter-spacing="4" fill="{DIM}" opacity="0.85">'
            f'{esc(c["latin"])}　/　{esc(c["handle"])}　/　2026</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}{bg}{"".join(parts)}{tail}</svg>')


def card_about(c, x, y, w, V):
    pad = V["cardpad"]
    parts = [label(x + pad, y + pad + 10, "关于 / ABOUT")]
    yy = y + pad + 44
    for para in c["about"]:
        for ln in wrap(para, w - pad * 2, V["body"]):
            parts.append(f'<text x="{x+pad}" y="{yy}" font-size="{V["body"]}" fill="{INK}" '
                         f'opacity="0.92">{esc(ln)}</text>')
            yy += V["lh"]
        yy += 12
    return parts, (yy - y) + pad - 6


def card_now(c, x, y, w, V):
    pad = V["cardpad"]
    parts = [label(x + pad, y + pad + 10, "在做 / NOW")]
    yy = y + pad + 46
    for i, item in enumerate(c["doing"]):
        parts.append(f'<text x="{x+pad}" y="{yy}" font-size="{V["h"]}" font-weight="600" '
                     f'fill="{INK}">{esc(item["k"])}</text>')
        yy += 24
        for ln in wrap(item["v"], w - pad * 2, V["small"]):
            parts.append(f'<text x="{x+pad}" y="{yy}" font-size="{V["small"]}" fill="{SUB}">{esc(ln)}</text>')
            yy += V["smalllh"]
        yy += 20
    return parts, (yy - y) - 4


def card_work(c, x, y, w, V):
    pad = V["cardpad"]
    parts = [label(x + pad, y + pad + 10, "项目 / WORK")]
    yy = y + pad + 48
    parts.append(f'<text x="{x+pad}" y="{yy}" font-size="{V["h"]+6}" font-weight="700" '
                 f'fill="{INK}">{esc(c["work"]["name"])}</text>')
    yy += 30
    for ln in wrap(c["work"]["desc"], w - pad * 2, V["small"] + 1):
        parts.append(f'<text x="{x+pad}" y="{yy}" font-size="{V["small"]+1}" fill="{SUB}">{esc(ln)}</text>')
        yy += V["smalllh"] + 2
    yy += 18
    tx = x + pad
    for t in c["work"]["tags"]:
        ww = tw(t.upper(), 10) * 1.35 + 26
        parts.append(f'<rect x="{tx}" y="{yy-16}" width="{ww}" height="26" rx="13" fill="#ffffff" '
                     f'fill-opacity="0.05" stroke="#ffffff" stroke-opacity="0.16"/>')
        parts.append(f'<text x="{tx+ww/2}" y="{yy+1}" text-anchor="middle" font-size="10.5" '
                     f'letter-spacing="1.4" fill="{MINT}">{esc(t.upper())}</text>')
        tx += ww + 8
    yy += 30
    return parts, (yy - y)


def card_contact(c, x, y, w, V):
    pad = V["cardpad"]
    parts = [label(x + pad, y + pad + 10, "联系 / CONTACT")]
    yy = y + pad + 46
    for item in c["contact"]:
        parts.append(f'<text x="{x+pad}" y="{yy}" font-size="10" letter-spacing="3.4" '
                     f'fill="{DIM}">{esc(item["k"])}</text>')
        yy += 24
        parts.append(f'<text x="{x+pad}" y="{yy}" font-size="{V["small"]+3}" fill="{INK}" '
                     f'font-family="Consolas, monospace">{esc(item["v"])}</text>')
        yy += 30
    return parts, (yy - y) - 4


def main():
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    ASSETS.mkdir(exist_ok=True)

    for V, suffix in ((DESK, ""), (MOB, "-mobile")):
        (ASSETS / f"glass{suffix}.svg").write_text(build(c, V), encoding="utf-8")

    src = (ROOT / "content.json").read_bytes() + (ROOT / "scripts" / "build.py").read_bytes()
    ver = hashlib.sha1(src + (ROOT / "BUILD").read_bytes()).hexdigest()[:6]

    img = (f'<div align="center">\n<picture>\n'
           f'  <source media="(max-width: 640px)" srcset="assets/glass-mobile.svg?v={ver}" />\n'
           f'  <img width="100%" alt="{esc(c["name"])} · {esc(c["role"])} · {esc(c["handle"])}" '
           f'src="assets/glass.svg?v={ver}" />\n</picture>\n</div>\n')
    note = "<!-- 由 scripts/build.py 生成，请勿直接编辑。改内容请修改 content.json 后提交。 -->\n\n"
    (ROOT / "README.md").write_text(note + img, encoding="utf-8")
    print(f"built glass {ver}")


if __name__ == "__main__":
    main()
