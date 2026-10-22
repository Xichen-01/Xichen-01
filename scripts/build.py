#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""空间站 + 粒子星座，英文优先。

    py -3 scripts/build.py
"""
import json
import math
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BASE = "#05080F"
INK = "#F4F8FF"
SUB = "#A6B7D4"
DIM = "#6B7F9E"
MINT = "#5EEAD4"
CYAN = "#38BDF8"
VIOLET = "#8B9CF6"

SANS = '"PingFang SC", "Microsoft YaHei", "Inter", "Noto Sans SC", sans-serif'

DESK = dict(w=1200, name=64, sub=18)
MOB = dict(w=680, name=40, sub=14)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


DEFS = f'''<defs>
  <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{MINT}"/><stop offset="1" stop-color="{CYAN}"/>
  </linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0.35"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{MINT}" stop-opacity="0.35"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glow2" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.30"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <style>
    text {{ font-family: {SANS}; }}
    .mono {{ font-family: Consolas, "JetBrains Mono", monospace; }}
  </style>
</defs>'''


def rnd(seed):
    return (seed * 1103515245 + 12345) & 0x7FFFFFFF


def constellation(W, H, n=54, seed=913, avoid=None):
    """粒子 + 连线，缓慢漂移。"""
    pts = []
    s = seed
    x0, x1 = (W * 0.42, W - 20) if W > 800 else (W * 0.30, W - 12)
    y0, y1 = 24, H - 24
    for _ in range(n):
        s = rnd(s); x = x0 + (s % int(x1 - x0))
        s = rnd(s); y = y0 + (s % int(y1 - y0))
        if avoid and math.hypot(x - avoid[0], y - avoid[1]) < avoid[2]:
            s = rnd(s)
            continue
        s = rnd(s); r = 0.6 + (s % 90) / 100.0
        s = rnd(s); op = 0.22 + (s % 45) / 100.0
        s = rnd(s); dur = 3.0 + (s % 40) / 10.0
        s = rnd(s); dly = (s % 30) / 10.0
        pts.append((x, y, r, op, dur, dly))

    lines = []
    m = len(pts)
    for i in range(m):
        for j in range(i + 1, m):
            d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if d < 158:
                lines.append((pts[i], pts[j], 1 - d / 158))

    out = ['<g opacity="0.85">']
    for a, b, w in lines:
        if w < 0.35:
            continue
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{CYAN}" stroke-opacity="{0.16 * w:.2f}" stroke-width="0.8"/>')
    for x, y, r, op, dur, dly in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{MINT}" opacity="{op:.2f}">'
                   f'<animate attributeName="opacity" values="{op:.2f};{min(op+0.45,0.95):.2f};{op:.2f}" '
                   f'dur="{dur:.1f}s" begin="{dly:.1f}s" repeatCount="indefinite"/></circle>')
    out.append('</g>')
    out.append(f'<g><animateTransform attributeName="transform" type="translate" '
               f'values="0,0; 9,-7; 0,0" dur="22s" repeatCount="indefinite"/>{"".join(out)}</g>')
    return "".join(out)


def station(cx, cy, s=1.0):
    g = [f'<g transform="translate({cx},{cy}) scale({s})" stroke="{MINT}" stroke-opacity="0.6" fill="none">']
    g.append(f'<circle r="240" fill="url(#glow)" stroke="none"/>')

    g.append(f'<line x1="-146" y1="0" x2="146" y2="0" stroke-width="1.2"/>')
    g.append(f'<line x1="-146" y1="-9" x2="146" y2="-9" stroke-opacity="0.22"/>')

    for ox in (-232, 158):
        g.append(f'<rect x="{ox}" y="-32" width="72" height="64" stroke-width="1" stroke-opacity="0.5"/>')
        for i in range(1, 6):
            g.append(f'<line x1="{ox + i*12}" y1="-32" x2="{ox + i*12}" y2="32" stroke-opacity="0.20"/>')
        g.append(f'<line x1="{ox if ox < 0 else ox+72}" y1="0" x2="{-146 if ox < 0 else 146}" y2="0" stroke-opacity="0.38"/>')

    g.append(f'<rect x="-46" y="-30" width="92" height="60" rx="12" stroke-width="1.4" stroke="{INK}" stroke-opacity="0.9"/>')
    g.append(f'<rect x="-34" y="-18" width="26" height="36" rx="4" stroke-opacity="0.3"/>')
    g.append(f'<circle cx="18" cy="0" r="10" stroke-opacity="0.4"/>')

    for x1, y1, x2, y2, mx, my in ((-46, -12, -104, -62, -132, -78), (46, -12, 104, -62, 132, -78)):
        g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-width="1.1" stroke-opacity="0.42"/>')
        g.append(f'<rect x="{mx}" y="{my}" width="52" height="30" rx="7" stroke-width="1.1" stroke-opacity="0.72"/>')
        g.append(f'<circle cx="{mx+14}" cy="{my+15}" r="2" fill="{MINT}" fill-opacity="0.85" stroke="none"/>')

    g.append(f'<line x1="0" y1="-30" x2="0" y2="-72" stroke-width="1.1"/>')
    g.append(f'<rect x="-26" y="-102" width="52" height="30" rx="7" stroke-width="1.1" stroke-opacity="0.72"/>')
    g.append(f'<line x1="0" y1="30" x2="0" y2="64" stroke-width="1.1"/>')
    g.append(f'<rect x="-30" y="64" width="60" height="28" rx="7" stroke-width="1.1" stroke-opacity="0.72"/>')

    g.append(f'<line x1="0" y1="-102" x2="0" y2="-146" stroke-width="1" stroke-opacity="0.45"/>')
    g.append(f'<circle cx="0" cy="-150" r="3" fill="{MINT}" stroke="none">'
             f'<animate attributeName="opacity" values="0.15;1;0.15" dur="2.8s" repeatCount="indefinite"/></circle>')

    for bx, by, col, d in ((-96, -78, CYAN, "3.4s"), (122, -78, VIOLET, "4.1s"), (0, 78, CYAN, "3.8s")):
        g.append(f'<circle cx="{bx}" cy="{by}" r="2.4" fill="{col}" stroke="none">'
                 f'<animate attributeName="opacity" values="0.1;1;0.1" dur="{d}" repeatCount="indefinite"/></circle>')

    g.append('</g>')
    return "".join(g)


def build_hero(c, V):
    W = V["w"]
    small = W <= 800
    H = 440 if not small else 360
    P = 56 if not small else 24

    parts = [f'<rect width="{W}" height="{H}" fill="{BASE}"/>',
             constellation(W, H),
             f'<circle cx="{W*0.14}" cy="{H*0.18}" r="{W*0.22}" fill="url(#glow2)"/>']

    if not small:
        parts.append(station(W - 300, 218, 0.92))
    else:
        parts.append(station(W - 168, H - 96, 0.55))

    parts.append(f'<text x="{P}" y="{68 if not small else 46}" class="mono" font-size="11" '
                 f'letter-spacing="6" fill="{DIM}">{esc(c["latin"])}　·　ORBITAL STATION</text>')

    ny = 196 if not small else 150
    parts.append(f'<text x="{P-2}" y="{ny}" font-size="{V["name"]}" font-weight="700" '
                 f'letter-spacing="3" fill="{INK}">{esc(c["latin"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+38}" font-size="{V["sub"]}" fill="{SUB}">'
                 f'{esc(c["name"])}　·　{esc(c["role"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+68}" class="mono" font-size="{V["sub"]-4}" '
                 f'letter-spacing="1.5" fill="{MINT}" opacity="0.9">{esc(c["handle"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+104}" font-size="{V["sub"]-1}" fill="{DIM}" '
                 f'letter-spacing="0.3">{esc(c["tagline"])}</text>')

    idx = "　".join(f'{m["id"]} {m["en"]}' for m in c["modules"])
    parts.append(f'<text x="{P}" y="{H-34}" class="mono" font-size="10.5" letter-spacing="3.6" '
                 f'fill="{DIM}" opacity="0.85">{esc(idx)}</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}{"".join(parts)}</svg>')


def build_module(m, W):
    small = W <= 800
    H = 92 if not small else 80
    P = 56 if not small else 24
    name_sz = 26 if not small else 21
    en_sz = 12.5 if not small else 11
    cy = H / 2

    parts = [
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="{BASE}"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="#ffffff" stroke-opacity="0.09"/>',
        f'<rect x="0" y="14" width="2" height="{H-28}" rx="1" fill="url(#bar)"/>',
        f'<text x="{P}" y="{cy+4}" class="mono" font-size="10.5" letter-spacing="1.6" '
        f'fill="{MINT}" opacity="0.85">{esc(m["id"])}</text>',
    ]

    gx = P + 62
    parts.append(f'<rect x="{gx}" y="{cy-12}" width="24" height="24" rx="6" fill="none" '
                 f'stroke="{MINT}" stroke-opacity="0.5"/>')
    parts.append(f'<circle cx="{gx+12}" cy="{cy}" r="2.6" fill="{MINT}" opacity="0.85"/>')

    tx = gx + 40
    parts.append(f'<text x="{tx}" y="{cy+9}" font-size="{name_sz}" font-weight="700" '
                 f'letter-spacing="2" fill="{INK}">{esc(m["en"])}</text>')

    zh_x = tx + (215 if not small else 150)
    parts.append(f'<text x="{zh_x}" y="{cy+6}" font-size="{en_sz}" letter-spacing="3" '
                 f'fill="{DIM}">{esc(m["zh"])}</text>')

    parts.append(f'<line x1="{zh_x + (60 if not small else 46)}" y1="{cy+22}" x2="{W-P-58}" y2="{cy+22}" '
                 f'stroke="{CYAN}" stroke-opacity="0.24" stroke-dasharray="1 6"/>')

    cx = W - P - 18
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="none" stroke="{MINT}" stroke-opacity="0.35"/>')
    parts.append(f'<path d="M{cx-5} {cy} H{cx+5} M{cx} {cy-5} V{cy+5}" stroke="{MINT}" '
                 f'stroke-width="1.3" stroke-linecap="round" opacity="0.9"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}{"".join(parts)}</svg>')


def main():
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    ASSETS.mkdir(exist_ok=True)

    (ASSETS / "hero.svg").write_text(build_hero(c, DESK), encoding="utf-8")
    (ASSETS / "hero-mobile.svg").write_text(build_hero(c, MOB), encoding="utf-8")
    for i, m in enumerate(c["modules"]):
        (ASSETS / f"mod-{i+1}.svg").write_text(build_module(m, DESK["w"]), encoding="utf-8")
        (ASSETS / f"mod-{i+1}-mobile.svg").write_text(build_module(m, MOB["w"]), encoding="utf-8")

    src = (ROOT / "content.json").read_bytes() + (ROOT / "scripts" / "build.py").read_bytes()
    ver = hashlib.sha1(src + (ROOT / "BUILD").read_bytes()).hexdigest()[:6]

    out = ["<!-- 由 scripts/build.py 生成，请勿直接编辑。改内容请修改 content.json 后提交。 -->\n",
           '<div align="center">',
           '<picture>',
           f'  <source media="(max-width: 640px)" srcset="assets/hero-mobile.svg?v={ver}" />',
           f'  <img width="100%" alt="{esc(c["name"])} · {esc(c["role"])} · {esc(c["handle"])}" '
           f'src="assets/hero.svg?v={ver}" />',
           '</picture>',
           '</div>\n']

    for i, m in enumerate(c["modules"]):
        n = i + 1
        open_attr = " open" if m.get("open") else ""
        out.append(f'<details{open_attr}>')
        out.append(f'<summary><picture>'
                   f'<source media="(max-width: 640px)" srcset="assets/mod-{n}-mobile.svg?v={ver}" />'
                   f'<img width="100%" alt="{esc(m["id"])} {esc(m["en"])} {esc(m["zh"])}" '
                   f'src="assets/mod-{n}.svg?v={ver}" /></picture></summary>')
        out.append("")
        for para in m["body_en"]:
            out.append(para)
            out.append("")
        out.append(f'<sub>{" ".join(m["body_zh"])}</sub>')
        out.append("")
        out.append("</details>")
        out.append("")

    (ROOT / "README.md").write_text("\n".join(out), encoding="utf-8")
    print(f"built station {ver}")


if __name__ == "__main__":
    main()
