#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""空间站风格：一张总览图 + 四个可展开的模块条。

    py -3 scripts/build.py
"""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BASE = "#05080F"
INK = "#F2F6FF"
SUB = "#9FB0CC"
DIM = "#6F82A0"
MINT = "#5EEAD4"
IRIS = "#818CF8"
PINK = "#F472B6"
AMBER = "#FBBF24"

SANS = '"PingFang SC", "Microsoft YaHei", "Inter", "Noto Sans SC", sans-serif'

DESK = dict(w=1200, name=84, sub=18)
MOB = dict(w=680, name=58, sub=14)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


DEFS = f'''<defs>
  <radialGradient id="g1" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{MINT}" stop-opacity="0.28"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.075"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.02"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#5EEAD4"/><stop offset="1" stop-color="#818CF8"/>
  </linearGradient>
  <filter id="orb" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="80"/>
  </filter>
  <style>
    text {{ font-family: {SANS}; }}
    .mono {{ font-family: Consolas, "JetBrains Mono", monospace; }}
  </style>
</defs>'''


def stars(W, H, n=90, seed=20261022):
    out = []
    for _ in range(n):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = seed % W
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        y = seed % H
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        r = 0.4 + (seed % 80) / 100.0
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        op = 0.10 + (seed % 50) / 100.0
        dur = 4 + (seed % 50) / 10.0
        out.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#DDE8F5" opacity="{op:.2f}">'
                   f'<animate attributeName="opacity" values="{op:.2f};{min(op+0.4,0.9):.2f};{op:.2f}" '
                   f'dur="{dur:.1f}s" repeatCount="indefinite"/></circle>')
    return "".join(out)


def station(cx, cy, s=1.0):
    """线稿空间站。s 为缩放。"""
    g = [f'<g transform="translate({cx},{cy}) scale({s})" stroke="{MINT}" stroke-opacity="0.55" fill="none">',
         f'<circle r="250" fill="url(#g1)" stroke="none"/>']

    # 主桁架
    g.append(f'<line x1="-150" y1="0" x2="150" y2="0" stroke-width="1.2"/>')
    g.append(f'<line x1="-150" y1="-8" x2="150" y2="-8" stroke-opacity="0.25"/>')

    # 太阳翼
    for ox in (-238, 164):
        g.append(f'<rect x="{ox}" y="-34" width="74" height="68" stroke-width="1" stroke-opacity="0.5"/>')
        for i in range(1, 6):
            g.append(f'<line x1="{ox + i*12}" y1="-34" x2="{ox + i*12}" y2="34" stroke-opacity="0.22"/>')
        g.append(f'<line x1="{ox if ox < 0 else ox+74}" y1="0" x2="{-150 if ox < 0 else 150}" y2="0" stroke-opacity="0.4"/>')

    # 核心舱
    g.append(f'<rect x="-46" y="-30" width="92" height="60" rx="12" stroke-width="1.4" stroke="{INK}" stroke-opacity="0.85"/>')
    g.append(f'<rect x="-34" y="-18" width="26" height="36" rx="4" stroke-opacity="0.3"/>')
    g.append(f'<circle cx="18" cy="0" r="10" stroke-opacity="0.4"/>')

    # 对接臂与模块
    arms = [(-46, -12, -104, -62, -132, -78), (46, -12, 104, -62, 132, -78)]
    for x1, y1, x2, y2, mx, my in arms:
        g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-width="1.1" stroke-opacity="0.45"/>')
        g.append(f'<rect x="{mx}" y="{my}" width="52" height="30" rx="7" stroke-width="1.1" stroke-opacity="0.75"/>')
        g.append(f'<circle cx="{mx+14}" cy="{my+15}" r="2" fill="{MINT}" fill-opacity="0.9" stroke="none"/>')

    # 上下模块
    g.append(f'<line x1="0" y1="-30" x2="0" y2="-74" stroke-width="1.1"/>')
    g.append(f'<rect x="-26" y="-104" width="52" height="30" rx="7" stroke-width="1.1" stroke-opacity="0.75"/>')
    g.append(f'<line x1="0" y1="30" x2="0" y2="66" stroke-width="1.1"/>')
    g.append(f'<rect x="-30" y="66" width="60" height="28" rx="7" stroke-width="1.1" stroke-opacity="0.75"/>')

    # 天线
    g.append(f'<line x1="0" y1="-104" x2="0" y2="-150" stroke-width="1" stroke-opacity="0.5"/>')
    g.append(f'<circle cx="0" cy="-154" r="3" fill="{MINT}" stroke="none">'
             f'<animate attributeName="opacity" values="0.2;1;0.2" dur="2.6s" repeatCount="indefinite"/></circle>')

    # 信标
    for bx, by, col in ((-96, -78, PINK), (122, -78, AMBER), (0, 66+14, IRIS)):
        g.append(f'<circle cx="{bx}" cy="{by}" r="2.4" fill="{col}" stroke="none">'
                 f'<animate attributeName="opacity" values="0.15;1;0.15" dur="3.2s" repeatCount="indefinite"/></circle>')

    g.append('</g>')
    return "".join(g)


def build_hero(c, V):
    W = V["w"]
    H = 440 if W > 800 else 360
    small = W <= 800
    P = 56 if not small else 24

    parts = [
        f'<rect width="{W}" height="{H}" fill="{BASE}"/>',
        stars(W, H),
        f'<circle cx="{W*0.72}" cy="{H*0.42}" r="{W*0.30}" fill="{MINT}" opacity="0.16" filter="url(#orb)"/>',
        f'<circle cx="{W*0.06}" cy="{H*0.1}" r="{W*0.22}" fill="{IRIS}" opacity="0.16" filter="url(#orb)"/>',
    ]

    if not small:
        parts.append(station(W - 330, H / 2, 1.0))
    else:
        parts.append(station(W - 190, H - 120, 0.62))

    parts.append(f'<text x="{P}" y="{72 if not small else 52}" font-size="11.5" letter-spacing="6" '
                 f'fill="{DIM}">{esc(c["latin"])}　·　ORBITAL STATION</text>')
    ny = 200 if not small else 156
    big = 64 if not small else 40
    parts.append(f'<text x="{P-2}" y="{ny}" font-size="{big}" font-weight="700" '
                 f'letter-spacing="5" fill="{INK}">{esc(c["latin"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+38}" font-size="{V["sub"]+2}" fill="{SUB}">'
                 f'{esc(c["name"])}　·　{esc(c["role"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+68}" font-size="{V["sub"]-2}" letter-spacing="1.5" '
                 f'fill="{MINT}" opacity="0.85">{esc(c["handle"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+102}" font-size="{V["sub"]}" fill="{DIM}">{esc(c["tagline"])}</text>')
    idx = "　".join(f'{m["id"]} {m["en"]}' for m in c["modules"])
    parts.append(f'<text x="{P}" y="{H-36}" font-size="11" letter-spacing="4" fill="{DIM}" opacity="0.8">'
                 f'{esc(idx)}</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}{"".join(parts)}</svg>')


def build_module(m, W, accent):
    small = W <= 800
    H = 96 if not small else 84
    P = 56 if not small else 24
    name_sz = 26 if not small else 22
    en_sz = 11.5 if not small else 10.5

    parts = [
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="{BASE}"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="url(#panel)" '
        f'stroke="#ffffff" stroke-opacity="0.12"/>',
        f'<rect x="0" y="0" width="3" height="{H}" rx="1.5" fill="{accent}"/>',
    ]

    # 模块编号
    parts.append(f'<text x="{P}" y="{H/2+4}" class="mono" font-size="11" letter-spacing="1.5" '
                 f'fill="{accent}">{esc(m["id"])}</text>')
    # 小图标
    gx = P + 66
    parts.append(f'<rect x="{gx}" y="{H/2-13}" width="26" height="26" rx="6" fill="none" '
                 f'stroke="{accent}" stroke-opacity="0.55"/>')
    parts.append(f'<circle cx="{gx+13}" cy="{H/2}" r="3" fill="{accent}" opacity="0.85"/>')

    # 标题
    tx = gx + 44
    parts.append(f'<text x="{tx}" y="{H/2+8}" font-size="{name_sz}" font-weight="700" '
                 f'letter-spacing="1.5" fill="{INK}">{esc(m["en"])}</text>')
    w_en = len(m["en"]) * name_sz * 0.64
    parts.append(f'<text x="{tx + w_en + 16}" y="{H/2+6}" font-size="{en_sz+2}" '
                 f'letter-spacing="2" fill="{DIM}">{esc(m["zh"])}</text>')

    # 分隔线 + 展开符
    parts.append(f'<line x1="{tx}" y1="{H/2+18}" x2="{W-P-56}" y2="{H/2+18}" stroke="{accent}" '
                 f'stroke-opacity="0.18"/>')
    cx = W - P - 22
    parts.append(f'<circle cx="{cx}" cy="{H/2}" r="15" fill="none" stroke="{accent}" stroke-opacity="0.45"/>')
    parts.append(f'<path d="M{cx-6} {H/2} H{cx+6} M{cx} {H/2-6} V{H/2+6}" stroke="{accent}" '
                 f'stroke-width="1.4" stroke-linecap="round" opacity="0.9"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}{"".join(parts)}</svg>')


def main():
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    ASSETS.mkdir(exist_ok=True)

    (ASSETS / "hero.svg").write_text(build_hero(c, DESK), encoding="utf-8")
    (ASSETS / "hero-mobile.svg").write_text(build_hero(c, MOB), encoding="utf-8")

    accents = [MINT, IRIS, PINK, AMBER]
    for i, m in enumerate(c["modules"]):
        acc = accents[i % 4]
        (ASSETS / f"mod-{i+1}.svg").write_text(build_module(m, DESK["w"], acc), encoding="utf-8")
        (ASSETS / f"mod-{i+1}-mobile.svg").write_text(build_module(m, MOB["w"], acc), encoding="utf-8")

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
                   f'<img width="100%" alt="{esc(m["id"])} {esc(m["zh"])} {esc(m["en"])}" '
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
