#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content.json 渲染成 assets/*.svg 和 README.md。

改文案只需要动 content.json，然后跑一次：
    python scripts/build.py
"""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ── 配色 ────────────────────────────────────────────────
PANEL_TOP = "#0A1725"
PANEL_BOT = "#08121D"
STROKE = "#14304A"
TEXT = "#DCE7F0"
MUTED = "#7E96AA"
DIM = "#4F6B82"
SOFT = "#C7D6E3"

# ── 两套尺寸 ────────────────────────────────────────────
DESKTOP = dict(w=1200, pad=72, label=13, body=29, lh=48, small=19, smalllh=31,
               h1=40, h2=26, lh2=39, name=86, latin=20, handle=17, role=20,
               radius=16, hero_h=380, gap=18, suffix="")
MOBILE = dict(w=680, pad=36, label=12, body=31, lh=50, small=20, smalllh=32,
              h1=34, h2=28, lh2=41, name=66, latin=14, handle=15, role=16,
              radius=16, hero_h=360, gap=16, suffix="-mobile")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chw(c, size):
    if ord(c) < 128:
        if c in "ilj|.,:;'!()[]":  return size * 0.32
        if c in "mwMW@":            return size * 0.86
        if c.isupper():             return size * 0.66
        return size * 0.55
    return size * 1.0


def tw(s, size):
    return sum(chw(c, size) for c in s)


def wrap(text, maxw, size):
    """按中英混排粗略断行。"""
    tokens, buf = [], ""
    for c in text:
        if ord(c) < 128 and not c.isspace():
            buf += c
        else:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(" " if c.isspace() else c)
    if buf:
        tokens.append(buf)

    lines, cur = [], ""
    for t in tokens:
        if t == " " and not cur:
            continue
        if tw(cur + t, size) <= maxw:
            cur += t
        else:
            if cur.strip():
                lines.append(cur.rstrip())
            cur = "" if t == " " else t
    if cur.strip():
        lines.append(cur.rstrip())
    return lines or [""]


DEFS = f'''<defs>
    <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{PANEL_TOP}"/>
      <stop offset="1" stop-color="{PANEL_BOT}"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#5EEAD4"/>
      <stop offset="0.55" stop-color="#38BDF8"/>
      <stop offset="1" stop-color="#A78BFA"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5EEAD4"/>
      <stop offset="1" stop-color="#A78BFA"/>
    </linearGradient>
    <linearGradient id="pkt" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#38BDF8" stop-opacity="0"/>
      <stop offset="0.7" stop-color="#38BDF8" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#A5F3FC" stop-opacity="0.95"/>
    </linearGradient>
    <style>
      text {{ font-family: Inter, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif; }}
      .label {{ font-size: {DESKTOP['label']}px; font-weight: 600; letter-spacing: 3px; fill: {DIM}; }}
      .body  {{ fill: {TEXT}; }}
      .small {{ fill: {MUTED}; }}
      .k     {{ font-size: 15px; font-weight: 600; letter-spacing: 2.4px; fill: {DIM}; }}
      .v     {{ fill: {SOFT}; }}
      .h1    {{ font-weight: 700; fill: #F1F7FB; }}
      .tag   {{ font-size: 11px; font-weight: 600; letter-spacing: 1.4px; fill: #7DD3FC; }}
    </style>
  </defs>'''


def label(num, zh, en, P, size=None):
    return (f'<text x="{P}" y="76" class="label">{esc(num)} — {esc(zh)} / {esc(en)}</text>'
            f'<rect x="{P}" y="96" width="36" height="2" fill="url(#accent)"/>')


def decor(W, H):
    """右上角脉冲点 + 底部流光，给每张卡一点动静。"""
    return f'''
  <circle cx="{W-72}" cy="70" r="3" fill="#5EEAD4">
    <animate attributeName="opacity" values="0.2;0.95;0.2" dur="3.4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{W-72}" cy="70" r="7" fill="#5EEAD4" opacity="0.18">
    <animate attributeName="r" values="7;12;7" dur="3.4s" repeatCount="indefinite"/>
  </circle>
  <line x1="0" y1="{H-1}" x2="{W}" y2="{H-1}" stroke="#12283C" stroke-width="1"/>
  <rect x="0" y="{H-2}" width="110" height="2" fill="url(#pkt)" opacity="0.55">
    <animate attributeName="x" values="-120;{W}" dur="9s" repeatCount="indefinite"/>
  </rect>'''


def shell(W, H, inner, R=16):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{DEFS}'
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="{R}" fill="url(#panel)" stroke="{STROKE}"/>'
            f'{inner}{decor(W, H)}</svg>')


# ── 卡片 ────────────────────────────────────────────────
def build_about(c, V):
    W, P = V["w"], V["pad"]
    maxw = W - 2 * P
    y = 150
    out = []
    for para in c["about"]:
        for ln in wrap(para, maxw, V["body"]):
            out.append(f'<text x="{P}" y="{y}" class="body" font-size="{V["body"]}">{esc(ln)}</text>')
            y += V["lh"]
        y += V["gap"]

    en_lines = wrap(c.get("about_en", ""), maxw, V["small"])
    if en_lines:
        y += 6
        out.append(f'<line x1="{P}" y1="{y-24}" x2="{W-P}" y2="{y-24}" stroke="{STROKE}"/>')
        y += 10
        for ln in en_lines:
            out.append(f'<text x="{P}" y="{y}" class="small" font-size="{V["small"]}">{esc(ln)}</text>')
            y += V["smalllh"]

    H = y + 56
    return shell(W, H, label("01", "关于", "ABOUT", P) + "".join(out), V["radius"])


def build_now(c, V):
    W, P = V["w"], V["pad"]
    maxw = W - 2 * P
    y = 158
    out = []
    rows = c["now"]
    for i, item in enumerate(rows):
        out.append(f'<text x="{P}" y="{y}" class="k">{esc(item["k"])}</text>')
        yy = y + 34
        for ln in wrap(item["v"], maxw, V["h2"]):
            out.append(f'<text x="{P}" y="{yy}" class="v" font-size="{V["h2"]}">{esc(ln)}</text>')
            yy += V["lh2"]
        y = yy + 26
        if i < len(rows) - 1:
            out.append(f'<line x1="{P}" y1="{y-14}" x2="{W-P}" y2="{y-14}" stroke="{STROKE}"/>')
            y += 10

    H = y + 40
    return shell(W, H, label("02", "现在", "NOW", P) + "".join(out), V["radius"])


def build_work(c, V):
    W, P = V["w"], V["pad"]
    inner_w = W - 2 * P
    pad_in = 36
    text_w = inner_w - pad_in * 2
    y = 150
    out = []
    out.append(f'<rect x="{P}" y="{y}" width="{inner_w}" height="1" fill="none"/>')

    # 内卡
    card_y = y
    yy = card_y + 58
    out.append(f'<text x="{P+pad_in}" y="{yy}" class="h1" font-size="{V["h1"]}">{esc(c["work"]["name"])}</text>')
    yy += 40
    for ln in wrap(c["work"]["desc"], text_w, 22):
        out.append(f'<text x="{P+pad_in}" y="{yy}" class="small" font-size="22">{esc(ln)}</text>')
        yy += 34
    yy += 14
    x = P + pad_in
    for t in c["work"]["tags"]:
        w = tw(t.upper(), 11) * 1.2 + 30
        out.append(f'<rect x="{x}" y="{yy}" width="{w}" height="26" rx="13" fill="#0C2436" stroke="#1B4B6B"/>')
        out.append(f'<text x="{x+w/2}" y="{yy+17}" class="tag" text-anchor="middle">{esc(t.upper())}</text>')
        x += w + 10
    card_h = (yy + 26 + 40) - card_y

    out.insert(1, f'<rect x="{P}" y="{card_y}" width="{inner_w}" height="{card_h}" rx="12" fill="#0B1926" stroke="#16324B"/>')
    out.insert(2, f'<rect x="{P}" y="{card_y}" width="3.5" height="{card_h}" rx="1.75" fill="url(#edge)"/>')

    H = card_y + card_h + 56
    return shell(W, H, label("03", "项目", "WORK", P) + "".join(out), V["radius"])


def build_contact(c, V):
    W, P = V["w"], V["pad"]
    y = 158
    out = []
    rows = c["contact"]
    for i, item in enumerate(rows):
        out.append(f'<text x="{P}" y="{y}" class="k">{esc(item["k"])}</text>')
        out.append(f'<text x="{P}" y="{y+36}" class="v" font-size="24" style="font-family:Consolas,monospace">{esc(item["v"])}</text>')
        y += 96
        if i < len(rows) - 1:
            out.append(f'<line x1="{P}" y1="{y-26}" x2="{W-P}" y2="{y-26}" stroke="{STROKE}"/>')
    H = y + 34
    return shell(W, H, label("04", "联系", "CONTACT", P) + "".join(out), V["radius"])


def build_hero(c, V):
    W, P = V["w"], V["pad"]
    H = V["hero_h"]
    small = V["w"] < 800
    orbit = "" if small else f'''
  <g transform="translate({W-256},208)">
    <circle r="132" fill="none" stroke="#17334C" stroke-dasharray="2 7" opacity="0.8"/>
    <circle r="94" fill="none" stroke="#17334C" opacity="0.55"/>
    <circle r="56" fill="none" stroke="#1B3E5B" stroke-dasharray="3 5" opacity="0.7"/>
    <path d="M0 -132 A132 132 0 0 1 93 -93" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
    <circle r="3.4" fill="#5EEAD4"/>
    <g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="48s" repeatCount="indefinite"/>
      <circle cx="132" cy="0" r="2.6" fill="#7DD3FC"/></g>
    <g><animateTransform attributeName="transform" type="rotate" from="120" to="480" dur="34s" repeatCount="indefinite"/>
      <circle cx="94" cy="0" r="2" fill="#A78BFA"/></g>
    <g><animateTransform attributeName="transform" type="rotate" from="250" to="610" dur="26s" repeatCount="indefinite"/>
      <circle cx="56" cy="0" r="1.6" fill="#5EEAD4"/></g>
  </g>'''

    ny = 196 if not small else 190
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#050A11"/><stop offset="0.58" stop-color="#07131F"/>
      <stop offset="1" stop-color="#0A1A2A"/>
    </linearGradient>
    <radialGradient id="ga" cx="0.12" cy="0.14" r="0.55">
      <stop offset="0" stop-color="#22D3EE" stop-opacity="0.18"/><stop offset="1" stop-color="#22D3EE" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="gb" cx="0.86" cy="0.8" r="0.6">
      <stop offset="0" stop-color="#8B5CF6" stop-opacity="0.16"/><stop offset="1" stop-color="#8B5CF6" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#5EEAD4"/><stop offset="0.55" stop-color="#38BDF8"/><stop offset="1" stop-color="#A78BFA"/>
    </linearGradient>
    <linearGradient id="pkt" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#38BDF8" stop-opacity="0"/><stop offset="1" stop-color="#A5F3FC" stop-opacity="0.95"/>
    </linearGradient>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="1" fill="#15304A" fill-opacity="0.55"/>
    </pattern>
    <style>
      text {{ font-family: Inter, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif; }}
      .lbl {{ font-size: 12px; font-weight: 600; letter-spacing: 3px; fill: #4F6B82; }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity="0.45"/>
  <rect width="{W}" height="{H}" fill="url(#ga)"/>
  <rect width="{W}" height="{H}" fill="url(#gb)"/>
  <rect x="0" width="{W}" height="2" fill="url(#pkt)" opacity="0.35">
    <animate attributeName="y" values="-2;{H}" dur="7s" repeatCount="indefinite"/>
  </rect>
  <text x="{P}" y="64" class="lbl">PROFILE / 2026</text>
  <text x="{W-P}" y="64" class="lbl" text-anchor="end">AI × SOFTWARE</text>
  <text x="{P-2}" y="{ny}" font-size="{V['name']}" font-weight="700" letter-spacing="{6 if small else 8}" fill="#F2F7FB">{esc(c["name"])}</text>
  <text x="{P}" y="{ny+44}" font-size="{V['latin']}" font-weight="500" letter-spacing="{5 if small else 8}" fill="{MUTED}">{esc(c["latin"])}</text>
  <rect x="{P}" y="{ny+74}" width="{240 if small else 380}" height="1" fill="#17334C"/>
  <text x="{P}" y="{ny+112}" font-size="{V['handle']}" fill="#5EEAD4" font-family="Consolas,monospace">{esc(c["handle"])}</text>
  <text x="{P}" y="{ny+148}" font-size="{V['role']}" fill="{MUTED}" letter-spacing="1.5">{esc(c["role"])}</text>
  {orbit}
  <line x1="0" y1="{H-1}" x2="{W}" y2="{H-1}" stroke="#12283C"/>
  <rect x="0" y="{H-3}" width="90" height="2" fill="url(#pkt)" opacity="0.8">
    <animate attributeName="x" values="-120;{W}" dur="6s" repeatCount="indefinite"/>
  </rect>
</svg>'''


def main():
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    ASSETS.mkdir(exist_ok=True)

    writers = {
        "hero": build_hero,
        "about": build_about,
        "now": build_now,
        "work": build_work,
        "contact": build_contact,
    }
    for name, fn in writers.items():
        for variant, suffix in ((DESKTOP, ""), (MOBILE, "-mobile")):
            (ASSETS / f"{name}{suffix}.svg").write_text(fn(c, variant), encoding="utf-8")

    ver = hashlib.sha1((ROOT / "content.json").read_bytes()).hexdigest()[:6]
    alts = {
        "hero": f'{c["name"]} · {c["handle"]}',
        "about": "关于我 ABOUT",
        "now": "现在 NOW",
        "work": f'项目 {c["work"]["name"]}',
        "contact": "联系方式 CONTACT",
    }
    parts = []
    for name in writers:
        parts.append(
            f'<div align="center">\n<picture>\n'
            f'  <source media="(max-width: 640px)" srcset="assets/{name}-mobile.svg?v={ver}" />\n'
            f'  <img width="100%" alt="{alts[name]}" src="assets/{name}.svg?v={ver}" />\n'
            f'</picture>\n</div>\n')
        header = "<!-- 此文件由 scripts/build.py 生成，请勿直接编辑。改文案请修改 content.json 后运行构建。 -->\n\n"
    (ROOT / "README.md").write_text(header + "\n".join(parts), encoding="utf-8")
    print(f"built 10 svgs, version {ver}")


if __name__ == "__main__":
    main()
