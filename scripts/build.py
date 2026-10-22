#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content.json 渲染成一页「器件数据手册」风格的 SVG。

    py -3 scripts/build.py
"""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BG = "#04090F"
PANEL = "#071019"
FRAME = "#254A62"
GRID_S = "#0D1E2C"
GRID_L = "#12293C"
INK = "#E4EDF5"
MUTED = "#93A9BB"
DIM = "#5B7A90"
ACCENT = "#5EEAD4"
BLUE = "#7DD3FC"

DESK = dict(w=1200, pad=72, body=28, lh=42, small=21, smalllh=30,
            h1=74, h2=34, name=88, latin=20, mono=13,
            stack=False, dia="row")
MOB = dict(w=680, pad=36, body=24, lh=36, small=18, smalllh=27,
           h1=46, h2=24, name=62, latin=13, mono=11,
           stack=True, dia="col")

MONO = 'font-family="Consolas, monospace"'


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
  <radialGradient id="lg" cx="0.10" cy="0.02" r="0.95">
    <stop offset="0" stop-color="#5EEAD4" stop-opacity="0.06"/>
    <stop offset="0.5" stop-color="#38BDF8" stop-opacity="0.015"/>
    <stop offset="1" stop-color="#38BDF8" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#5EEAD4"/><stop offset="1" stop-color="#A78BFA"/>
  </linearGradient>
  <marker id="arw" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
    <path d="M0 0 L10 5 L0 10 Z" fill="#2E5A78"/>
  </marker>
  <style>
    text {{ font-family: Inter, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif; }}
    .mono {{ font-family: Consolas, "JetBrains Mono", monospace; letter-spacing: 2px; fill: {DIM}; }}
  </style>
</defs>'''


def frame(W, H, m=22):
    x0, y0, x1, y1 = m, m, W - m, H - m
    t = 12
    marks = ""
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        marks += f'<path d="M{x} {y+dy*t} V{y} H{x+dx*t}" fill="none" stroke="#2E5A78" stroke-width="1.5"/>'
    flow = (f'<rect x="{x0+1}" y="{y0+1}" width="{x1-x0-2}" height="{y1-y0-2}" fill="none" '
            f'stroke="url(#accent)" stroke-opacity="0.25" stroke-dasharray="8 170">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="-720" dur="16s" repeatCount="indefinite"/>'
            f'</rect>')
    return (f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="{FRAME}"/>'
            f'{marks}{flow}')


def sheet(W, H, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>'
            f'<rect width="{W}" height="{H}" fill="url(#lg)"/>'
            f'<g opacity="0.5">'
            f'<path d="M0 24H{W}M0 48H{W}M0 72H{W}" stroke="none"/>'
            f'</g>'
            f'{grid(W, H)}{frame(W, H)}{inner}</svg>')


def grid(W, H, step=24):
    """细网格 + 每 96 一条粗线。"""
    out = [f'<g stroke="{GRID_S}" stroke-width="1" opacity="0.55">']
    x = 0
    while x <= W:
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
        x += step
    y = 0
    while y <= H:
        out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
        y += step
    out.append('</g>')
    out.append(f'<g stroke="{GRID_L}" stroke-width="1" opacity="0.5">')
    x = 0
    while x <= W:
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
        x += step * 4
    y = 0
    while y <= H:
        out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
        y += step * 4
    out.append('</g>')
    return "".join(out)


def stitle(parts, y, zh, en, W, P, size=16):
    parts.append(f'<text x="{P}" y="{y}" font-size="{size}" font-weight="700" '
                 f'letter-spacing="3" fill="{INK}">{esc(zh)}</text>')
    parts.append(f'<text x="{P+tw(zh,size)+16}" y="{y-1}" class="mono" font-size="12">{esc(en)}</text>')
    parts.append(f'<line x1="{P}" y1="{y+14}" x2="{W-P}" y2="{y+14}" stroke="{FRAME}"/>')
    parts.append(f'<rect x="{P}" y="{y+13}" width="64" height="2" fill="url(#accent)"/>')
    return y + 46


def header(c, V, parts):
    W, P = V["w"], V["pad"]
    small = V["stack"]
    parts.append(f'<text x="{P}" y="70" class="mono" font-size="12">DATASHEET / {esc(c["part"])}</text>')
    parts.append(f'<text x="{W-P}" y="70" class="mono" font-size="12" text-anchor="end">'
                 f'REV {esc(c["rev"])} · SHEET 1 OF 1</text>')

    parts.append(f'<text x="{P-3}" y="188" font-size="{V["name"]}" font-weight="700" '
                 f'letter-spacing="6" fill="{INK}">{esc(c["name"])}</text>')
    parts.append(f'<text x="{P}" y="226" class="mono" font-size="{V["latin"]}" letter-spacing="7" '
                 f'fill="{MUTED}">{esc(c["latin"])}</text>')

    parts.append(f'<line x1="{P}" y1="252" x2="{W-P}" y2="252" stroke="{FRAME}"/>')

    parts.append(f'<text x="{P}" y="288" class="mono" font-size="13" fill="{ACCENT}">{esc(c["handle"])}</text>')
    parts.append(f'<text x="{P}" y="316" font-size="17" fill="{MUTED}">{esc(c["role"])}</text>')

    if not small:
        bx = W - P - 330
        for i, (k, v) in enumerate((("PART NO", c["part"]), ("REV", c["rev"]), ("STATUS", "ACTIVE"))):
            yy = 288 + i * 30
            parts.append(f'<text x="{bx}" y="{yy}" class="mono" font-size="11.5">{k}</text>')
            parts.append(f'<text x="{bx+120}" y="{yy}" font-size="13" fill="{INK}">{esc(v)}</text>')
            parts.append(f'<line x1="{bx}" y1="{yy+10}" x2="{W-P}" y2="{yy+10}" stroke="{FRAME}" opacity="0.6"/>')

    return 360


def section_features(c, V, y, parts):
    W, P = V["w"], V["pad"]
    y = stitle(parts, y, "特性", "FEATURES", W, P)
    maxw = W - P * 2 - 34
    for f in c["features"]:
        parts.append(f'<path d="M{P+6} {y-7} l5 5 l-5 5 l-5 -5 Z" fill="{ACCENT}" opacity="0.85"/>')
        for ln in wrap(f, maxw, V["body"]):
            parts.append(f'<text x="{P+30}" y="{y}" font-size="{V["body"]}" fill="{INK}">{esc(ln)}</text>')
            y += V["lh"]
        y += 12
    return y + 18


def section_revisions(c, V, y, parts):
    W, P = V["w"], V["pad"]
    y = stitle(parts, y, "修订记录", "REVISION HISTORY", W, P)
    cx = [P, P + 90, P + 220] if not V["stack"] else [P, P + 46, P + 120]
    parts.append(f'<text x="{cx[0]}" y="{y}" class="mono" font-size="11.5">REV</text>')
    parts.append(f'<text x="{cx[1]}" y="{y}" class="mono" font-size="11.5">DATE</text>')
    parts.append(f'<text x="{cx[2]}" y="{y}" class="mono" font-size="11.5">DESCRIPTION</text>')
    parts.append(f'<line x1="{P}" y1="{y+12}" x2="{W-P}" y2="{y+12}" stroke="{FRAME}"/>')
    y += 42
    for r in c["revisions"]:
        parts.append(f'<text x="{cx[0]}" y="{y}" font-size="13" fill="{ACCENT}" {MONO}>{esc(r["rev"])}</text>')
        parts.append(f'<text x="{cx[1]}" y="{y}" font-size="13" fill="{DIM}" {MONO}>{esc(r["date"])}</text>')
        parts.append(f'<text x="{cx[2]}" y="{y}" font-size="{V["small"]}" fill="{MUTED}">{esc(r["desc"])}</text>')
        y += 44
        parts.append(f'<line x1="{P}" y1="{y-16}" x2="{W-P}" y2="{y-16}" stroke="{FRAME}" opacity="0.55"/>')
    return y + 16


def block(parts, x, y, w, h, ident, name, desc, io=None):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{PANEL}" stroke="#2E5A78"/>')
    parts.append(f'<path d="M{x} {y+10} V{y} H{x+10}" fill="none" stroke="{ACCENT}" stroke-width="1.4"/>')
    parts.append(f'<text x="{x+12}" y="{y+18}" class="mono" font-size="10.5" style="fill:{ACCENT}">{ident}</text>')
    parts.append(f'<text x="{x+14}" y="{y+46}" font-size="17" font-weight="700" fill="{INK}">{esc(name)}</text>')
    parts.append(f'<text x="{x+14}" y="{y+68}" font-size="13" fill="{MUTED}">{esc(desc)}</text>')


def section_diagram(c, V, y, parts):
    W, P = V["w"], V["pad"]
    y = stitle(parts, y, "功能框图", "FUNCTIONAL DIAGRAM", W, P)
    if not V["stack"]:
        me_w, me_h = 230, 116
        me_x, me_y = P + 20, y + 24
        block(parts, me_x, me_y, me_w, me_h, "U0", c["name"], c["role"])
        bx = W - P - 330
        bus_x = me_x + me_w + 56
        ys = []
        for i, b in enumerate(c["blocks"]):
            by = y + 24 + i * 104
            block(parts, bx, by, 330, 84, b["id"], b["name"], f'{b["desc"]}　·　{b["io"]}')
            ys.append(by + 42)

        parts.append(f'<line x1="{me_x+me_w}" y1="{me_y+me_h/2}" x2="{bus_x}" y2="{me_y+me_h/2}" stroke="#2E5A78"/>')
        parts.append(f'<line x1="{bus_x}" y1="{ys[0]}" x2="{bus_x}" y2="{ys[-1]}" stroke="#2E5A78"/>')
        for (b, by) in zip(c["blocks"], ys):
            parts.append(f'<line x1="{bus_x}" y1="{by}" x2="{bx-2}" y2="{by}" stroke="#2E5A78" marker-end="url(#arw)"/>')
            parts.append(f'<text x="{bus_x+10}" y="{by-8}" class="mono" font-size="10">{esc(b["io"])}</text>')
        parts.append(f'<circle cx="{bus_x}" cy="{ys[0]}" r="2.4" fill="{BLUE}">'
                     f'<animate attributeName="cy" values="{ys[0]};{ys[-1]}" dur="4.5s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="0;1;1;0" dur="4.5s" repeatCount="indefinite"/></circle>')
        return y + 24 + 3 * 104 + 6

    # 竖排
    me_w = W - 2 * P
    block(parts, P, y + 10, me_w, 92, "U0", c["name"], c["role"])
    yy = y + 102
    for b in c["blocks"]:
        parts.append(f'<line x1="{W/2}" y1="{yy}" x2="{W/2}" y2="{yy+26}" stroke="#2E5A78" marker-end="url(#arw)"/>')
        block(parts, P, yy + 26, me_w, 86, b["id"], b["name"], f'{b["desc"]}　·　{b["io"]}')
        yy += 112
    return yy + 6


def section_contact(c, V, y, parts):
    W, P = V["w"], V["pad"]
    y = stitle(parts, y, "联系方式", "CONTACT", W, P)
    cx = [P, P + 90, P + 230] if not V["stack"] else [P, P + 46, P + 130]
    parts.append(f'<text x="{cx[0]}" y="{y}" class="mono" font-size="11.5">PIN</text>')
    parts.append(f'<text x="{cx[1]}" y="{y}" class="mono" font-size="11.5">SIGNAL</text>')
    parts.append(f'<text x="{cx[2]}" y="{y}" class="mono" font-size="11.5">VALUE</text>')
    parts.append(f'<line x1="{P}" y1="{y+12}" x2="{W-P}" y2="{y+12}" stroke="{FRAME}"/>')
    y += 42
    for i, item in enumerate(c["contact"]):
        parts.append(f'<text x="{cx[0]}" y="{y}" font-size="13" fill="{ACCENT}" {MONO}>{i+1:02d}</text>')
        parts.append(f'<text x="{cx[1]}" y="{y}" font-size="13" fill="{DIM}" {MONO}>{esc(item["k"])}</text>')
        parts.append(f'<text x="{cx[2]}" y="{y}" font-size="18" fill="{INK}" {MONO}>{esc(item["v"])}</text>')
        y += 50
        parts.append(f'<line x1="{P}" y1="{y-18}" x2="{W-P}" y2="{y-18}" stroke="{FRAME}" opacity="0.55"/>')
    return y + 20


def title_block(c, V, y, parts):
    W, P = V["w"], V["pad"]
    h = 64
    cells = [("DRAWN", c["name"]), ("DATE", "2026.10"), ("SCALE", "1:1"), ("SHEET", "1 / 1")]
    cw = (W - 2 * P) / len(cells)
    parts.append(f'<rect x="{P}" y="{y}" width="{W-2*P}" height="{h}" fill="none" stroke="{FRAME}"/>')
    for i, (k, v) in enumerate(cells):
        x = P + i * cw
        if i:
            parts.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{FRAME}"/>')
        parts.append(f'<text x="{x+12}" y="{y+26}" class="mono" font-size="10.5">{k}</text>')
        parts.append(f'<text x="{x+12}" y="{y+50}" font-size="14" fill="{INK}">{esc(v)}</text>')
    return y + h + 46


def build(c, V):
    parts = []
    y = header(c, V, parts)
    y = section_features(c, V, y, parts)
    y = section_revisions(c, V, y, parts)
    y = section_diagram(c, V, y, parts)
    y = section_contact(c, V, y, parts)
    y = title_block(c, V, y + 6, parts)
    return sheet(V["w"], y, "".join(parts))


def main():
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    ASSETS.mkdir(exist_ok=True)

    for V, suffix in ((DESK, ""), (MOB, "-mobile")):
        (ASSETS / f"sheet{suffix}.svg").write_text(build(c, V), encoding="utf-8")

    src = (ROOT / "content.json").read_bytes() + (ROOT / "scripts" / "build.py").read_bytes()
    ver = hashlib.sha1(src + (ROOT / "BUILD").read_bytes()).hexdigest()[:6]

    img = (f'<div align="center">\n<picture>\n'
           f'  <source media="(max-width: 640px)" srcset="assets/sheet-mobile.svg?v={ver}" />\n'
           f'  <img width="100%" alt="{esc(c["name"])} · {esc(c["role"])} · {esc(c["handle"])}" '
           f'src="assets/sheet.svg?v={ver}" />\n</picture>\n</div>\n')
    note = "<!-- 由 scripts/build.py 生成，请勿直接编辑。改内容请修改 content.json 后提交。 -->\n\n"
    (ROOT / "README.md").write_text(note + img, encoding="utf-8")
    print(f"built sheet {ver}")


if __name__ == "__main__":
    main()
