#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content.json 渲染成一页暖色的长图（黎明 / 星尘）。

    py -3 scripts/build.py
"""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

CREAM = "#F5EBDF"
MUTED = "#B8A4AE"
DIM = "#6E5C74"
GLOW = "#F0A868"
ROSE = "#D98876"

SERIF = '"Songti SC", "Noto Serif SC", "Source Han Serif SC", "SimSun", serif'
SANS = '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif'

DESK = dict(w=1200, pad=120, name=96, latin=16, body=28, lh=47,
            small=18, smalllh=30, poem=27, poemlh=45, label=12,
            doing_k=28, doing_v=20, gap=72)
MOB = dict(w=680, pad=44, name=62, latin=12, body=21, lh=36,
           small=15, smalllh=26, poem=20, poemlh=34, label=10.5,
           doing_k=22, doing_v=17, gap=48)


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


def stars(W, H, n=80, seed=20261022):
    out = []
    for _ in range(n):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = 10 + seed % (W - 20)
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        y = 20 + seed % int(H * 0.72)
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        r = 0.5 + (seed % 90) / 100.0
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        dur = 3.5 + (seed % 60) / 10.0
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        op = 0.12 + (seed % 55) / 100.0
        hi = min(op + 0.45, 0.95)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{CREAM}" opacity="{op:.2f}">'
                   f'<animate attributeName="opacity" values="{op:.2f};{hi:.2f};{op:.2f}" '
                   f'dur="{dur:.1f}s" repeatCount="indefinite"/></circle>')
    return "".join(out)


def motes(W, H, n=7, seed=777):
    out = []
    for i in range(n):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = 40 + seed % (W - 80)
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        y = int(H * 0.35) + seed % int(H * 0.5)
        r = 1.2 + (seed % 3) * 0.7
        dur = 14 + (seed % 10)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{GLOW}" opacity="0">'
                   f'<animate attributeName="cy" values="{y};{y-90};{y-180}" dur="{dur}s" '
                   f'repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0.5;0" dur="{dur}s" '
                   f'repeatCount="indefinite"/></circle>')
    return "".join(out)


def label(parts, x, y, zh, en):
    parts.append(f'<text x="{x}" y="{y}" class="sans" font-size="12" letter-spacing="5" '
                 f'fill="{DIM}">{esc(zh)}　{esc(en)}</text>')
    parts.append(f'<line x1="{x}" y1="{y+16}" x2="{x+44}" y2="{y+16}" stroke="{GLOW}" '
                 f'stroke-opacity="0.55"/>')
    return y + 52


STYLE = '''  <style>
    .serif { font-family: "Songti SC", "Noto Serif SC", "Source Han Serif SC", "SimSun", serif; }
    .sans  { font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif; }
    .mono  { font-family: Consolas, monospace; }
  </style>'''


def build(c, V):
    W, P = V["w"], V["pad"]
    parts = []
    y = 96 if V is DESK else 74

    # ── 头部 ──
    parts.append(f'<text x="{P}" y="{y}" class="sans" font-size="11.5" letter-spacing="6" '
                 f'fill="{DIM}">{esc(c["latin"])}　·　2026</text>')
    ny = y + (150 if V is DESK else 106)
    parts.append(f'<text x="{P-6}" y="{ny}" class="serif" font-size="{V["name"]}" '
                 f'font-weight="600" letter-spacing="8" fill="{CREAM}">{esc(c["name"])}</text>')
    parts.append(f'<text x="{P}" y="{ny+40}" class="sans" font-size="{V["latin"]}" '
                 f'letter-spacing="8" fill="{MUTED}">{esc(c["latin"])}</text>')

    dy = ny + 76
    parts.append(f'<line x1="{P}" y1="{dy}" x2="{P+240}" y2="{dy}" stroke="{ROSE}" stroke-opacity="0.45"/>')
    parts.append(f'<rect x="{P+246}" y="{dy-3}" width="6" height="6" transform="rotate(45 {P+249} {dy})" '
                 f'fill="{ROSE}" opacity="0.8"/>')

    py = dy + 62
    for ln in wrap(c["poem"], W - 2 * P - 40, V["poem"]):
        parts.append(f'<text x="{P}" y="{py}" class="serif" font-size="{V["poem"]}" '
                     f'fill="{CREAM}" opacity="0.95">{esc(ln)}</text>')
        py += V["poemlh"]
    parts.append(f'<text x="{P}" y="{py+10}" class="sans" font-size="{V["small"]}" '
                 f'fill="{MUTED}" opacity="0.75">{esc(c["poem_en"])}</text>')
    py += 56
    parts.append(f'<text x="{P}" y="{py}" class="mono" font-size="15" '
                 f'letter-spacing="1" fill="{GLOW}">{esc(c["handle"])}</text>')

    # ── 关于 ──
    y = py + 96
    y = label(parts, P, y, "关于", "ABOUT")
    maxw = min(W - 2 * P, 880 if V is DESK else W - 2 * P)
    for para in c["about"]:
        for ln in wrap(para, maxw, V["body"]):
            parts.append(f'<text x="{P}" y="{y}" class="serif" font-size="{V["body"]}" '
                         f'fill="{CREAM}" opacity="0.9">{esc(ln)}</text>')
            y += V["lh"]
        y += 20
    y += 34

    # ── 在做 ──
    y = label(parts, P, y, "在做", "NOW")
    for item in c["doing"]:
        parts.append(f'<circle cx="{P+5}" cy="{y-6}" r="3" fill="{GLOW}" opacity="0.9"/>')
        parts.append(f'<text x="{P+26}" y="{y}" class="serif" font-size="{V["doing_k"]}" '
                     f'fill="{CREAM}">{esc(item["k"])}</text>')
        yy = y + V["doing_k"] + 12
        for ln in wrap(item["v"], maxw - 26, V["doing_v"]):
            parts.append(f'<text x="{P+26}" y="{yy}" class="serif" font-size="{V["doing_v"]}" '
                         f'fill="{MUTED}">{esc(ln)}</text>')
            yy += V["smalllh"] + 2
        y = yy + 34
    y += 20

    # ── 联系 ──
    y = label(parts, P, y, "找到我", "CONTACT")
    for item in c["contact"]:
        parts.append(f'<text x="{P}" y="{y}" class="sans" font-size="10.5" letter-spacing="4" '
                     f'fill="{DIM}">{esc(item["k"])}</text>')
        parts.append(f'<text x="{P}" y="{y+28}" class="mono" font-size="16" '
                     f'fill="{CREAM}">{esc(item["v"])}</text>')
        y += 74

    H = y + (200 if V is DESK else 170)

    # ── 背景 + 地平线 ──
    horizon = H - (150 if V is DESK else 120)
    bg = f'''<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#05060C"/>
    <stop offset="0.38" stop-color="#0B0D19"/>
    <stop offset="0.62" stop-color="#1A1526"/>
    <stop offset="0.82" stop-color="#33202A"/>
    <stop offset="1" stop-color="#53302F"/>
  </linearGradient>
  <radialGradient id="sun" cx="0.5" cy="1" r="0.75">
    <stop offset="0" stop-color="{GLOW}" stop-opacity="0.55"/>
    <stop offset="0.35" stop-color="{ROSE}" stop-opacity="0.22"/>
    <stop offset="1" stop-color="{ROSE}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="hline" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{ROSE}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{ROSE}" stop-opacity="0.55"/>
    <stop offset="1" stop-color="{ROSE}" stop-opacity="0"/>
  </linearGradient>
{STYLE}
</defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(W, H)}
{motes(W, H)}
<ellipse cx="{W/2}" cy="{horizon+30}" rx="{W*0.62}" ry="230" fill="url(#sun)">
  <animate attributeName="opacity" values="0.75;1;0.75" dur="11s" repeatCount="indefinite"/>
</ellipse>
<ellipse cx="{W/2}" cy="{horizon}" rx="{W*0.5}" ry="60" fill="{GLOW}" opacity="0.06"/>
<line x1="0" y1="{horizon}" x2="{W}" y2="{horizon}" stroke="url(#hline)"/>'''

    tail = (f'<text x="{W/2}" y="{H-56}" text-anchor="middle" class="sans" '
            f'font-size="11" letter-spacing="5" fill="{MUTED}" opacity="0.85">李天成　·　{XICHEN}　·　2026</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{bg}{"".join(parts)}{tail}</svg>')


XICHEN = "@Xichen-01"


def main():
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    ASSETS.mkdir(exist_ok=True)

    for V, suffix in ((DESK, ""), (MOB, "-mobile")):
        (ASSETS / f"sky{suffix}.svg").write_text(build(c, V), encoding="utf-8")

    src = (ROOT / "content.json").read_bytes() + (ROOT / "scripts" / "build.py").read_bytes()
    ver = hashlib.sha1(src + (ROOT / "BUILD").read_bytes()).hexdigest()[:6]

    img = (f'<div align="center">\n<picture>\n'
           f'  <source media="(max-width: 640px)" srcset="assets/sky-mobile.svg?v={ver}" />\n'
           f'  <img width="100%" alt="{esc(c["name"])} · {esc(c["role"])} · {esc(c["handle"])}" '
           f'src="assets/sky.svg?v={ver}" />\n</picture>\n</div>\n')
    note = "<!-- 由 scripts/build.py 生成，请勿直接编辑。改内容请修改 content.json 后提交。 -->\n\n"
    (ROOT / "README.md").write_text(note + img, encoding="utf-8")
    print(f"built sky {ver}")


if __name__ == "__main__":
    main()
