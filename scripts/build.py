def flow(W, H, m=24):
    """沿边框跑的一小段光，给整页一点流动感。"""
    return (f'<rect x="{m+1}" y="{m+1}" width="{W-2*m-2}" height="{H-2*m-2}" fill="none" '
            f'stroke="url(#accent)" stroke-opacity="0.32" stroke-width="1.2" stroke-dasharray="10 130">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="-624" dur="14s" repeatCount="indefinite"/>'
            f'</rect>')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content.json 渲染成一套「工程图纸」风格的 SVG + README。

改文案只动 content.json，然后：
    py -3 scripts/build.py
"""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BG = "#04090F"
PANEL = "#08121D"
FRAME = "#254A62"
GRID_S = "#0D1E2C"
GRID_L = "#12293C"
INK = "#DCE7F0"
MUTED = "#93A9BB"
DIM = "#5B7A90"
ACCENT = "#5EEAD4"
BLUE = "#7DD3FC"

DESKTOP = dict(w=1200, pad=72, body=29, lh=46, small=21, smalllh=32,
               h1=40, h2=30, lh2=44, name=86, latin=19, handle=18, role=20,
               radius=14, hero_h=460, stack=False, gap=18)
MOBILE = dict(w=680, pad=36, body=26, lh=42, small=18, smalllh=28,
              h1=32, h2=26, lh2=38, name=64, latin=13, handle=14, role=15,
              radius=14, hero_h=400, stack=True, gap=16)


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
        if tw(cur + t, size) <= maxw or (t and t[0] in "，。、；：？！）」』】》%,.;:?!)]}" and cur):
            cur += t
        else:
            if cur.strip():
                lines.append(cur.rstrip())
            cur = "" if t == " " else t
    if cur.strip():
        lines.append(cur.rstrip())
    return lines or [""]


GRID = f'''<defs>
  <radialGradient id="lg" cx="0.12" cy="0.04" r="0.95">
    <stop offset="0" stop-color="#5EEAD4" stop-opacity="0.065"/>
    <stop offset="0.55" stop-color="#38BDF8" stop-opacity="0.02"/>
    <stop offset="1" stop-color="#38BDF8" stop-opacity="0"/>
  </radialGradient>
  <pattern id="g1" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="{GRID_S}" stroke-width="1"/>
  </pattern>
  <pattern id="g2" width="96" height="96" patternUnits="userSpaceOnUse">
    <path d="M96 0H0V96" fill="none" stroke="{GRID_L}" stroke-width="1"/>
  </pattern>
</defs>'''

STYLE = f'''<style>
  text {{ font-family: Inter, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif; }}
  .mono {{ font-family: Consolas, "JetBrains Mono", monospace; font-size: 13px; letter-spacing: 2.4px; fill: {DIM}; }}
  .mono2 {{ font-family: Consolas, "JetBrains Mono", monospace; fill: {MUTED}; }}
</style>'''


def frame(W, H, m=24):
    x0, y0, x1, y1 = m, m, W - m, H - m
    t = 12
    marks = ""
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        marks += f'<path d="M{x} {y + dy*t} V{y} H{x + dx*t}" fill="none" stroke="#2E5A78" stroke-width="1.5"/>'
    return (f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="{FRAME}"/>' + marks)


def header(num, zh, en, P, W, size=27):
    return (f'<rect x="{P}" y="38" width="32" height="32" fill="none" stroke="{FRAME}"/>'
            f'<text x="{P+16}" y="60" text-anchor="middle" font-size="14" fill="{ACCENT}" '
            f'font-family="Consolas,monospace">{num}</text>'
            f'<text x="{P+48}" y="66" font-size="{size}" font-weight="700" fill="{INK}">{esc(zh)}</text>'
            f'<text x="{P+48+tw(zh,size)+16}" y="64" class="mono">{esc(en)}</text>'
            f'<line x1="{P}" y1="96" x2="{W-P}" y2="96" stroke="{FRAME}"/>'
            f'<line x1="{P}" y1="92" x2="{P}" y2="100" stroke="{FRAME}"/>'
            f'<line x1="{W-P}" y1="92" x2="{W-P}" y2="100" stroke="{FRAME}"/>' f'<rect x="{P}" y="95.5" width="118" height="2" fill="url(#accent)"/>')


def shell(W, H, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{GRID}{STYLE}'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>'
            f'<rect width="{W}" height="{H}" fill="url(#g1)" opacity="0.5"/>'
            f'<rect width="{W}" height="{H}" fill="url(#g2)" opacity="0.45"/><rect width="{W}" height="{H}" fill="url(#lg)"/>'
            f'{frame(W, H)}{flow(W, H)}{inner}</svg>')


def dim(x1, x2, y, label):
    """水平尺寸线：两端短竖线 + 中间小字。"""
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#2E5A78"/>'
            f'<line x1="{x1}" y1="{y-5}" x2="{x1}" y2="{y+5}" stroke="#2E5A78"/>'
            f'<line x1="{x2}" y1="{y-5}" x2="{x2}" y2="{y+5}" stroke="#2E5A78"/>'
            f'<text x="{(x1+x2)/2}" y="{y-8}" text-anchor="middle" class="mono">{label}</text>')


def module(x, y, w, h, code):
    t = 9
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0A1622" stroke="{FRAME}"/>'
            f'<path d="M{x} {y+t} V{y} H{x+t}" fill="none" stroke="{ACCENT}" stroke-width="1.4" opacity="0.85"/>'
            f'<path d="M{x+w} {y+h-t} V{y+h} H{x+w-t}" fill="none" stroke="{ACCENT}" stroke-width="1.4" opacity="0.85"/>'
            f'<text x="{x+16}" y="{y+22}" class="mono" fill="{ACCENT}" style="fill:{ACCENT}">{code}</text>')


def chip(cx, cy, s):
    out = [f'<rect x="{cx-s}" y="{cy-s}" width="{2*s}" height="{2*s}" rx="8" fill="#0A1A28" stroke="{FRAME}"/>',
           f'<rect x="{cx-s*0.56}" y="{cy-s*0.56}" width="{s*1.12}" height="{s*1.12}" rx="3" fill="none" stroke="#2A4A66"/>']
    n, gap = 5, 2 * s / 6
    for i in range(1, 6):
        off = -s + gap * i
        out.append(f'<line x1="{cx+off}" y1="{cy-s}" x2="{cx+off}" y2="{cy-s-15}" stroke="#2A4A66"/>')
        out.append(f'<line x1="{cx+off}" y1="{cy+s}" x2="{cx+off}" y2="{cy+s+15}" stroke="#2A4A66"/>')
        out.append(f'<line x1="{cx-s}" y1="{cy+off}" x2="{cx-s-15}" y2="{cy+off}" stroke="#2A4A66"/>')
        out.append(f'<line x1="{cx+s}" y1="{cy+off}" x2="{cx+s+15}" y2="{cy+off}" stroke="#2A4A66"/>')
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        x2 = cx + dx * (s + 15)
        y2 = cy + dy * (s + 15)
        out.append(f'<line x1="{x2}" y1="{y2}" x2="{x2 + dx*34}" y2="{y2 + dy*34}" stroke="#22475F" stroke-dasharray="3 4"/>')
        out.append(f'<circle cx="{x2 + dx*34}" cy="{y2 + dy*34}" r="2" fill="{BLUE}" opacity="0.9"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="13" fill="none" stroke="{ACCENT}" opacity="0.7"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="{ACCENT}">'
               f'<animate attributeName="r" values="4.5;9;4.5" dur="3.6s" repeatCount="indefinite"/></circle>')
    return "".join(out)


def build_hero(c, V):
    W, P = V["w"], V["pad"]
    H = V["hero_h"]
    small = V["w"] < 800
    name_w = tw(c["name"], V["name"]) + 7 * (len(c["name"]) - 1)
    ny = 196 if not small else 200

    body = [f'<text x="{P}" y="62" class="mono">{esc(c["eyebrow"])}</text>',
            f'<text x="{W-P}" y="62" class="mono" text-anchor="end">SHEET 01 / 05</text>',
            f'<text x="{P-4}" y="{ny}" font-size="{V["name"]}" font-weight="700" '
            f'letter-spacing="7" fill="{INK}">{esc(c["name"])}</text>',
            dim(P, P + name_w, ny + 36, "1:1"),
            f'<text x="{P}" y="{ny+82}" class="mono2" font-size="{V["latin"]}" '
            f'letter-spacing="{5 if small else 7}">{esc(c["latin"])}</text>',
            f'<line x1="{P}" y1="{ny+108}" x2="{P+340 if not small else P+250}" y2="{ny+108}" stroke="{FRAME}"/>',
            f'<text x="{P}" y="{ny+148}" font-family="Consolas,monospace" font-size="{V["handle"]}" '
            f'fill="{ACCENT}">{esc(c["handle"])}</text>',
            f'<text x="{P}" y="{ny+190}" font-size="{V["role"]}" fill="{MUTED}">{esc(c["tagline"])}</text>',
            f'<text x="{P}" y="{ny+218}" font-size="{15 if not small else 13}" fill="#546B80">'
            f'{esc(c["tagline_en"])}</text>']

    if not small:
        body.append(chip(W - 252, 192, 74)); body.append(f'<polyline points="{W-324},152 {W-392},106 {W-470},106" fill="none" stroke="#2E5A78"/>'); body.append(f'<circle cx="{W-324}" cy="152" r="2.6" fill="{ACCENT}"/>'); body.append(f'<text x="{W-470}" y="98" text-anchor="end" class="mono">FIG.1 / SYSTEM CORE</text>');
        tb_x, tb_y, tb_w, tb_h = W - 348, H - 124, 276, 96
        body.append(f'<rect x="{tb_x}" y="{tb_y}" width="{tb_w}" height="{tb_h}" fill="none" stroke="{FRAME}"/>')
        body.append(f'<line x1="{tb_x}" y1="{tb_y+32}" x2="{tb_x+tb_w}" y2="{tb_y+32}" stroke="{FRAME}"/>')
        body.append(f'<line x1="{tb_x}" y1="{tb_y+64}" x2="{tb_x+tb_w}" y2="{tb_y+64}" stroke="{FRAME}"/>')
        body.append(f'<line x1="{tb_x+70}" y1="{tb_y}" x2="{tb_x+70}" y2="{tb_y+tb_h}" stroke="{FRAME}"/>')
        for i, (k, v) in enumerate((("DRAWN", c["name"]), ("DATE", "2026.10"), ("SCALE", "1:1"))):
            body.append(f'<text x="{tb_x+12}" y="{tb_y+21+i*32}" class="mono">{k}</text>')
            body.append(f'<text x="{tb_x+84}" y="{tb_y+21+i*32}" font-size="14" fill="{INK}">{esc(v)}</text>')

    body.append(f'<rect x="0" y="0" width="{W}" height="2" fill="{ACCENT}" opacity="0.25">'
                f'<animate attributeName="y" values="0;{H}" dur="9s" repeatCount="indefinite"/></rect>')

    return shell(W, H, "".join(body))


def build_about(c, V):
    W, P = V["w"], V["pad"]
    inner = W - 2 * P
    y0 = 132

    if V["stack"]:
        out, y = [], y0 + 24
        out.append(f'<text x="{P}" y="{y}" class="mono">个人简介 / PROFILE</text>')
        out.append(f'<line x1="{P}" y1="{y+10}" x2="{W-P}" y2="{y+10}" stroke="{FRAME}" opacity="0.6"/>')
        y += 44
        for para in c["about_cn"]:
            for ln in wrap(para, inner, V["body"]):
                out.append(f'<text x="{P}" y="{y}" font-size="{V["body"]}" fill="{INK}">{esc(ln)}</text>')
                y += V["lh"]
            y += V["gap"]
        y += 10
        out.append(f'<text x="{P}" y="{y}" class="mono">EN</text>')
        y += 28
        for ln in wrap(c["about_en"], inner, V["small"]):
            out.append(f'<text x="{P}" y="{y}" font-size="{V["small"]}" fill="{MUTED}">{esc(ln)}</text>')
            y += V["smalllh"]
        H = y + 34
        return shell(W, H, header("01", "关于我", "ABOUT ME", P, W) + "".join(out))

    left_w = int(inner * 0.5)
    div_x = P + int(inner * 0.525)
    right_x = div_x + 34
    right_w = W - P - right_x

    out = [f'<text x="{P}" y="{y0}" class="mono">个人简介 / PROFILE</text>',
           f'<line x1="{P}" y1="{y0+10}" x2="{P+left_w-20}" y2="{y0+10}" stroke="{FRAME}" opacity="0.6"/>',
           f'<text x="{right_x}" y="{y0}" class="mono">EN</text>',
           f'<line x1="{right_x}" y1="{y0+10}" x2="{W-P}" y2="{y0+10}" stroke="{FRAME}" opacity="0.6"/>']

    yl = y0 + 44
    for para in c["about_cn"]:
        for ln in wrap(para, left_w - 10, V["body"]):
            out.append(f'<text x="{P}" y="{yl}" font-size="{V["body"]}" fill="{INK}">{esc(ln)}</text>')
            yl += V["lh"]
        yl += V["gap"]

    yr = y0 + 44
    for ln in wrap(c["about_en"], right_w, V["small"]):
        out.append(f'<text x="{right_x}" y="{yr}" font-size="{V["small"]}" fill="{MUTED}">{esc(ln)}</text>')
        yr += V["smalllh"]

    y_end = max(yl, yr)
    out.append(f'<line x1="{div_x}" y1="{y0-8}" x2="{div_x}" y2="{y_end-14}" stroke="{FRAME}"/>')
    out.append(f'<line x1="{div_x-5}" y1="{y0-8}" x2="{div_x+5}" y2="{y0-8}" stroke="{FRAME}"/>')
    out.append(f'<line x1="{div_x-5}" y1="{y_end-14}" x2="{div_x+5}" y2="{y_end-14}" stroke="{FRAME}"/>')

    H = y_end + 30
    return shell(W, H, header("01", "关于我", "ABOUT ME", P, W) + "".join(out))


def build_path(c, V):
    W, P = V["w"], V["pad"]
    rail_x = P + 24
    text_x = P + (78 if V["stack"] else 104)
    maxw = W - P - text_x
    y = 152
    out, nodes = [], []

    for item in c["path"]:
        lines = wrap(item["desc"], maxw, V["small"])
        out.append(f'<text x="{text_x}" y="{y+10}" class="mono">{esc(item["when"])}</text>')
        out.append(f'<text x="{text_x}" y="{y+52}" font-size="{V["h2"]}" font-weight="700" '
                   f'fill="{INK}">{esc(item["title"])}</text>')
        yy = y + 84
        for ln in lines:
            out.append(f'<text x="{text_x}" y="{yy}" font-size="{V["small"]}" fill="{MUTED}">{esc(ln)}</text>')
            yy += V["smalllh"]
        nodes.append(y + 8)
        y = yy + 36

    rail_top, rail_bot = 118, (nodes[-1] + 44 if nodes else y)
    out.insert(0, f'<line x1="{rail_x}" y1="{rail_top}" x2="{rail_x}" y2="{rail_bot}" '
                  f'stroke="#2A5570" stroke-width="2.6"/>')
    out.insert(1, f'<line x1="{rail_x}" y1="{rail_top}" x2="{rail_x}" y2="{rail_bot}" '
                  f'stroke="url(#fadeDown)" stroke-width="2.4" stroke-dasharray="46 170">'
                  f'<animate attributeName="stroke-dashoffset" from="0" to="-226" dur="3.4s" repeatCount="indefinite"/>'
                  f'</line>')

    ty = rail_top
    while ty < rail_bot:
        out.append(f'<line x1="{rail_x-7}" y1="{ty}" x2="{rail_x+7}" y2="{ty}" stroke="#3A6A88" opacity="0.45"/>')
        ty += 36

    for ny in nodes:
        out.append(f'<circle cx="{rail_x}" cy="{ny}" r="10" fill="{BG}" stroke="#2E5A78"/>')
        out.append(f'<circle cx="{rail_x}" cy="{ny}" r="3.6" fill="{ACCENT}"/>')
        out.append(f'<circle cx="{rail_x}" cy="{ny}" r="3.6" fill="{ACCENT}" opacity="0.4">'
                   f'<animate attributeName="r" values="3.6;15;3.6" dur="3.2s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0.4;0;0.4" dur="3.2s" repeatCount="indefinite"/></circle>')

    out.append(f'<circle cx="{rail_x}" cy="{rail_top}" r="3" fill="#A5F3FC">'
               f'<animate attributeName="cy" values="{rail_top};{rail_bot}" dur="6.5s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values="0;1;1;0" dur="6.5s" repeatCount="indefinite"/></circle>')

    H = y + 4
    return shell(W, H, header("02", "路径", "PATH", P, W) + "".join(out))

def build_work(c, V):
    W, P = V["w"], V["pad"]
    inner = W - 2 * P
    pad_in, top = 26, 122

    lines = wrap(c["work"]["desc"], inner - pad_in * 2 - 70, 18)
    h = 56 + 44 + len(lines) * 30 + 62
    out = [module(P, top, inner, h, "U2")]

    out.append(f'<text x="{P+pad_in}" y="{top+56}" font-size="{V["h1"]}" font-weight="700" '
               f'fill="{INK}">{esc(c["work"]["name"])}</text>')
    yy = top + 92
    for ln in lines:
        out.append(f'<text x="{P+pad_in}" y="{yy}" font-size="18" fill="{MUTED}">{esc(ln)}</text>')
        yy += 30

    yy += 12
    x = P + pad_in
    for t in c["work"]["tags"]:
        w = tw(t.upper(), 10) * 1.4 + 26
        out.append(f'<rect x="{x}" y="{yy}" width="{w}" height="24" fill="none" stroke="#2A4A66"/>')
        out.append(f'<text x="{x+w/2}" y="{yy+16}" text-anchor="middle" class="mono" '
                   f'style="fill:{BLUE}">{esc(t.upper())}</text>')
        x += w + 10

    out.append(f'<g transform="translate({W-P-56},{top+26})">'
               f'<rect x="0" y="0" width="30" height="30" fill="none" stroke="{FRAME}"/>'
               f'<path d="M9 21 L21 9 M12 9 H21 V18" fill="none" stroke="{ACCENT}" stroke-width="1.6"/></g>')

    H = top + h + 30
    return shell(W, H, header("03", "项目", "WORK", P, W) + "".join(out))


def build_contact(c, V):
    W, P = V["w"], V["pad"]
    col = [P, P + 90, P + 300] if not V["stack"] else [P, P + 60, P + 200]
    y = 140

    out = [f'<text x="{col[0]}" y="{y}" class="mono">PIN</text>',
           f'<text x="{col[1]}" y="{y}" class="mono">SIGNAL</text>',
           f'<text x="{col[2]}" y="{y}" class="mono">VALUE</text>',
           f'<line x1="{P}" y1="{y+12}" x2="{W-P}" y2="{y+12}" stroke="{FRAME}"/>']
    y += 44
    for i, item in enumerate(c["contact"]):
        out.append(f'<text x="{col[0]}" y="{y}" font-family="Consolas,monospace" font-size="13" fill="{ACCENT}">'
                   f'{i+1:02d}</text>')
        out.append(f'<text x="{col[1]}" y="{y}" class="mono2" font-size="13" letter-spacing="2">{esc(item["k"])}</text>')
        out.append(f'<text x="{col[2]}" y="{y}" font-family="Consolas,monospace" font-size="19" fill="{INK}">{esc(item["v"])}</text>')
        y += 54
        out.append(f'<line x1="{P}" y1="{y-24}" x2="{W-P}" y2="{y-24}" stroke="{FRAME}" opacity="0.55"/>')

    H = y + 24
    return shell(W, H, header("04", "联系", "CONTACT", P, W) + "".join(out))


def main():
    c = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    ASSETS.mkdir(exist_ok=True)

    writers = {"hero": build_hero, "about": build_about, "path": build_path,
               "work": build_work, "contact": build_contact}
    for name, fn in writers.items():
        for variant, suffix in ((DESKTOP, ""), (MOBILE, "-mobile")):
            (ASSETS / f"{name}{suffix}.svg").write_text(fn(c, variant), encoding="utf-8")

    ver = hashlib.sha1((ROOT / "content.json").read_bytes() + (ROOT / "scripts" / "build.py").read_bytes()).hexdigest()[:6]
    alts = {"hero": f'{c["name"]} · {c["handle"]}', "about": "关于我 ABOUT ME",
            "path": "路径 PATH", "work": f'项目 {c["work"]["name"]}',
            "contact": "联系方式 CONTACT"}
    parts = []
    for name in writers:
        parts.append(f'<div align="center">\n<picture>\n'
                     f'  <source media="(max-width: 640px)" srcset="assets/{name}-mobile.svg?v={ver}" />\n'
                     f'  <img width="100%" alt="{alts[name]}" src="assets/{name}.svg?v={ver}" />\n'
                     f'</picture>\n</div>\n')

    note = "<!-- 此文件由 scripts/build.py 生成，请勿直接编辑。改文案请修改 content.json 后运行构建。 -->\n\n"
    (ROOT / "README.md").write_text(note + "\n".join(parts), encoding="utf-8")
    print(f"built 10 svgs, version {ver}")


if __name__ == "__main__":
    main()
