#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""空间站 + 粒子 / 流星，模块可展开，英文优先。

    py -3 scripts/build.py
"""
import json
import math
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BASE = "#05080F"
CARD = "#070C16"
INK = "#F4F8FF"
EN_TXT = "#CBD8EA"
ZH_TXT = "#8FA3BC"
SUB = "#A6B7D4"
DIM = "#6B7F9E"
MINT = "#5EEAD4"
CYAN = "#38BDF8"
VIOLET = "#8B9CF6"

SANS = '"PingFang SC", "Microsoft YaHei", "Inter", "Noto Sans SC", sans-serif'

DESK = dict(w=1200, name=64, sub=18, en=21, enlh=36, zh=16, zhlh=29, pad=64)
MOB = dict(w=680, name=40, sub=14, en=17, enlh=29, zh=14, zhlh=25, pad=32)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def plain(s):
    return str(s).replace("**", "")


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
  <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{MINT}"/><stop offset="1" stop-color="{CYAN}"/>
  </linearGradient>
  <linearGradient id="meteor" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="0.75" stop-color="{CYAN}" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#FFFFFF" stop-opacity="1"/>
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


def constellation(W, H, n=52, seed=913):
    pts, s = [], seed
    x0, x1 = (W * 0.40, W - 16) if W > 800 else (W * 0.26, W - 10)
    y0, y1 = 18, H - 18
    for _ in range(n):
        s = rnd(s); x = x0 + (s % int(x1 - x0))
        s = rnd(s); y = y0 + (s % int(y1 - y0))
        s = rnd(s); r = 0.7 + (s % 100) / 100.0
        s = rnd(s); op = 0.25 + (s % 50) / 100.0
        s = rnd(s); dur = 3.0 + (s % 40) / 10.0
        s = rnd(s); dly = (s % 40) / 10.0
        pts.append((x, y, r, op, dur, dly))

    lines = []
    m = len(pts)
    for i in range(m):
        for j in range(i + 1, m):
            d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if d < 150:
                lines.append((pts[i], pts[j], 1 - d / 150))

    out = []
    for a, b, w in lines:
        if w < 0.3:
            continue
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{CYAN}" stroke-opacity="{0.22 * w:.2f}" stroke-width="0.8"/>')
    for x, y, r, op, dur, dly in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{MINT}" opacity="{op:.2f}">'
                   f'<animate attributeName="opacity" values="{op:.2f};{min(op+0.5,1):.2f};{op:.2f}" '
                   f'dur="{dur:.1f}s" begin="{dly:.1f}s" repeatCount="indefinite"/></circle>')
    return (f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="0,0; 10,-8; 0,0" dur="24s" repeatCount="indefinite"/>{"".join(out)}</g>')


def meteors(W, H):
    shots = [(W * 0.46, 18, 320, 136, "1.2s", "8.5s"),
             (W * 0.28, 96, 360, 158, "3.6s", "9.5s"),
             (W * 0.64, -8, 280, 128, "6.4s", "8s")]
    out = []
    for x, y, dx, dy, delay, dur in shots:
        out.append(f'<g opacity="0">'
                   f'<animate attributeName="opacity" values="0;0;1;0.9;0" keyTimes="0;0.42;0.58;0.86;1" '
                   f'dur="{dur}" begin="{delay}" repeatCount="indefinite"/>'
                   f'<animateTransform attributeName="transform" type="translate" '
                   f'values="0,0;{dx},{dy}" dur="{dur}" begin="{delay}" repeatCount="indefinite"/>'
                   f'<line x1="{x}" y1="{y}" x2="{x+96}" y2="{y+42}" stroke="url(#meteor)" '
                   f'stroke-width="1.6" stroke-linecap="round"/>'
                   f'<circle cx="{x+96}" cy="{y+42}" r="1.8" fill="#FFFFFF"/>'
                   f'<circle cx="{x+76}" cy="{y+33}" r="1.1" fill="{CYAN}" opacity="0.7"/>'
                   f'<circle cx="{x+56}" cy="{y+25}" r="0.9" fill="{CYAN}" opacity="0.45"/>'
                   f'</g>')
    return "".join(out)


def station(cx, cy, s=1.0):
    g = [f'<g transform="translate({cx},{cy}) scale({s})" stroke="{MINT}" stroke-opacity="0.6" fill="none">',
         f'<circle r="240" fill="url(#glow)" stroke="none"/>',
         f'<line x1="-146" y1="0" x2="146" y2="0" stroke-width="1.2"/>',
         f'<line x1="-146" y1="-9" x2="146" y2="-9" stroke-opacity="0.22"/>']
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
    H = 330 if not small else 260
    P = 56 if not small else 24

    parts = [f'<rect width="{W}" height="{H}" fill="{BASE}"/>',
             f'<circle cx="{W*0.14}" cy="{H*0.18}" r="{W*0.22}" fill="url(#glow2)"/>',
             constellation(W, H),
             meteors(W, H)]

    parts.append(f'<text x="{P}" y="{68 if not small else 46}" class="mono" font-size="11" '
                 f'letter-spacing="6" fill="{DIM}">{esc(c["latin"])}　·　ORBITAL STATION</text>')
    ny = 176 if not small else 140
    parts.append(f'<text x="{P-2}" y="{ny}" font-size="{V["name"]}" font-weight="700" '
                 f'letter-spacing="3" fill="{INK}">{esc(c["latin"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+38}" font-size="{V["sub"]}" fill="{SUB}">'
                 f'{esc(c["name"])}　·　{esc(c["role"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+68}" class="mono" font-size="{V["sub"]-4}" '
                 f'letter-spacing="1.5" fill="{MINT}" opacity="0.9">{esc(c["handle"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+102}" font-size="{V["sub"]-1}" fill="{DIM}" '
                 f'letter-spacing="0.3">{esc(c["tagline"])}</text>')
    parts.append(f'<text x="{P}" y="{H-26}" class="mono" font-size="10.5" letter-spacing="3.6" '
                 f'fill="{DIM}" opacity="0.85">DOCKING MODULES BELOW　▼</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}{"".join(parts)}</svg>')


def build_module(m, V, idx):
    W = V["w"]
    small = W <= 800
    H = 150 if not small else 132
    sp = 560 if not small else 316
    num = m["id"].split("-")[-1]
    cy = H / 2
    name_sz = 25 if not small else 21
    en_sz = 12 if not small else 11

    p_x = 64 if not small else 24
    pod_x = sp + 200 if not small else sp + 132
    pod_w = W - pod_x - (64 if not small else 24)
    pod_h = 84 if not small else 74

    parts = [f'<rect width="{W}" height="{H}" fill="{BASE}"/>']

    # 左侧编号
    parts.append(f'<text x="{p_x}" y="{cy+22}" font-size="{72 if not small else 52}" font-weight="700" '
                 f'fill="none" stroke="{CYAN}" stroke-opacity="0.35" stroke-width="1.2">'
                 f'{num}</text>')
    parts.append(f'<text x="{p_x+4}" y="{cy+52 if not small else cy+46}" font-size="{en_sz}" '
                 f'letter-spacing="3" fill="{DIM}">{esc(m["zh"])}</text>')

    # 主梁
    parts.append(f'<line x1="{sp-6}" y1="0" x2="{sp-6}" y2="{H}" stroke="{MINT}" stroke-opacity="0.35"/>')
    parts.append(f'<line x1="{sp+6}" y1="0" x2="{sp+6}" y2="{H}" stroke="{MINT}" stroke-opacity="0.35"/>')
    y = 0
    while y < H:
        parts.append(f'<line x1="{sp-6}" y1="{y}" x2="{sp+6}" y2="{y+18}" stroke="{MINT}" stroke-opacity="0.18"/>')
        parts.append(f'<line x1="{sp+6}" y1="{y}" x2="{sp-6}" y2="{y+18}" stroke="{MINT}" stroke-opacity="0.18"/>')
        y += 18

    # 旋转陀螺环
    parts.append(f'<g transform="translate({sp},{cy})">'
                 f'<ellipse rx="{66 if not small else 48}" ry="{20 if not small else 15}" fill="none" '
                 f'stroke="{CYAN}" stroke-opacity="0.55" stroke-dasharray="16 10" '
                 f'stroke-width="1.3">'
                 f'<animate attributeName="stroke-dashoffset" from="0" to="-52" dur="3.2s" repeatCount="indefinite"/>'
                 f'</ellipse>'
                 f'<ellipse rx="{66 if not small else 48}" ry="{20 if not small else 15}" fill="none" '
                 f'stroke="{MINT}" stroke-opacity="0.3" stroke-dasharray="26 14" '
                 f'transform="rotate(62)" stroke-width="1">'
                 f'<animate attributeName="stroke-dashoffset" from="0" to="-80" dur="5.5s" repeatCount="indefinite"/>'
                 f'</ellipse>'
                 f'<circle r="2.6" fill="{MINT}">'
                 f'<animateMotion dur="6s" repeatCount="indefinite" '
                 f'path="M {-66 if not small else -48},0 A {66 if not small else 48},{20 if not small else 15} 0 1,1 '
                 f'{66 if not small else 48},0 A {66 if not small else 48},{20 if not small else 15} 0 1,1 '
                 f'{-66 if not small else -48},0"/></circle>'
                 f'</g>')

    # 连接臂
    parts.append(f'<line x1="{sp+6}" y1="{cy}" x2="{pod_x}" y2="{cy}" stroke="{MINT}" stroke-opacity="0.45"/>')
    parts.append(f'<circle cx="{pod_x}" cy="{cy}" r="3" fill="{MINT}" opacity="0.9"/>')

    # 舱体
    parts.append(f'<rect x="{pod_x}" y="{cy-pod_h/2}" width="{pod_w}" height="{pod_h}" rx="10" '
                 f'fill="{CARD}" stroke="#1E4159"/>')
    parts.append(f'<rect x="{pod_x}" y="{cy-pod_h/2}" width="3" height="{pod_h}" rx="1.5" fill="url(#bar)"/>')
    tx = pod_x + 26
    parts.append(f'<text x="{tx}" y="{cy+9}" font-size="{name_sz}" font-weight="700" letter-spacing="2.5" '
                 f'fill="{INK}">{esc(m["en"])}</text>')
    parts.append(f'<text x="{tx + (176 if not small else 132)}" y="{cy+7}" font-size="{en_sz}" '
                 f'letter-spacing="2.4" fill="{DIM}">{esc(m["zh"])}</text>')
    parts.append(f'<line x1="{tx}" y1="{cy+24}" x2="{pod_x+pod_w-60}" y2="{cy+24}" '
                 f'stroke="{CYAN}" stroke-opacity="0.18" stroke-dasharray="1 6"/>')

    bx = pod_x + pod_w - 30
    parts.append(f'<circle cx="{bx}" cy="{cy}" r="12" fill="none" stroke="{MINT}" stroke-opacity="0.4"/>')
    parts.append(f'<path d="M{bx-4.5} {cy} H{bx+4.5} M{bx} {cy-4.5} V{cy+4.5}" stroke="{MINT}" '
                 f'stroke-width="1.2" stroke-linecap="round" opacity="0.9"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}'
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BASE}"/>'
            f'{"".join(parts)}</svg>')

def build_body(m, V):
    W, P = V["w"], V["pad"]
    small = W <= 800
    maxw = W - 2 * P
    num = m["id"].split("-")[-1]
    en_sz = 19 if small else 20
    en_lh = 31 if small else 34
    zh_sz = 14 if small else 16
    zh_lh = 25 if small else 28

    parts = [
        f'<rect x="{P}" y="28" width="30" height="30" fill="none" stroke="#2E5A78"/>',
        f'<text x="{P+15}" y="{48.5}" text-anchor="middle" class="mono" font-size="12" '
        f'fill="{MINT}">{num}</text>',
        f'<text x="{P+44}" y="{52}" font-size="22" font-weight="700" letter-spacing="2.5" '
        f'fill="{INK}">{esc(m["en"])}</text>',
        f'<text x="{P+44+len(m["en"])*22*0.74+18}" y="{50}" font-size="12" letter-spacing="2.4" '
        f'fill="{DIM}">{esc(m["zh"])}</text>',
        f'<line x1="{P}" y1="76" x2="{W-P}" y2="76" stroke="#1E4159"/>',
        f'<rect x="{P}" y="75" width="72" height="2" fill="url(#bar)"/>',
    ]

    y = 122
    for para in m["body_en"]:
        for ln in wrap(plain(para), maxw, en_sz):
            parts.append(f'<text x="{P}" y="{y}" font-size="{en_sz}" fill="{EN_TXT}" '
                         f'letter-spacing="0.2">{esc(ln)}</text>')
            y += en_lh
        y += 14

    y += 4
    parts.append(f'<line x1="{P}" y1="{y-12}" x2="{W-P}" y2="{y-12}" stroke="#17324A"/>')
    y += 30
    for para in m["body_zh"]:
        for ln in wrap(plain(para), maxw, zh_sz):
            parts.append(f'<text x="{P}" y="{y}" font-size="{zh_sz}" fill="{ZH_TXT}" '
                         f'letter-spacing="0.6">{esc(ln)}</text>')
            y += zh_lh
        y += 8

    H = y + 14
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}'
            f'<rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="{CARD}"/>'
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" '
            f'stroke="#1E4159" stroke-opacity="0.9"/>'
            f'<path d="M1 {H-14} V{H-1} H14" fill="none" stroke="{MINT}" stroke-opacity="0.5"/>'
            f'{"".join(parts)}</svg>')

def main():
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    ASSETS.mkdir(exist_ok=True)

    (ASSETS / "hero.svg").write_text(build_hero(c, DESK), encoding="utf-8")
    (ASSETS / "hero-mobile.svg").write_text(build_hero(c, MOB), encoding="utf-8")

    for i, m in enumerate(c["modules"]):
        n = i + 1
        (ASSETS / f"mod-{n}.svg").write_text(build_module(m, DESK, i + 1), encoding="utf-8")
        (ASSETS / f"mod-{n}-mobile.svg").write_text(build_module(m, MOB, i + 1), encoding="utf-8")
        (ASSETS / f"body-{n}.svg").write_text(build_body(m, DESK), encoding="utf-8")
        (ASSETS / f"body-{n}-mobile.svg").write_text(build_body(m, MOB), encoding="utf-8")

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
                   f'src="assets/mod-{n}.svg?v={ver}" /></picture></summary>\n')
        out.append(f'<div align="center"><picture>'
                   f'<source media="(max-width: 640px)" srcset="assets/body-{n}-mobile.svg?v={ver}" />'
                   f'<img width="100%" alt="{esc(" ".join(plain(p) for p in m["body_en"]))}" '
                   f'src="assets/body-{n}.svg?v={ver}" /></picture></div>')
        out.append("\n</details>\n")

    (ROOT / "README.md").write_text("\n".join(out), encoding="utf-8")
    print(f"built station {ver}")


if __name__ == "__main__":
    main()
