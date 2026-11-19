"""Builds the animated SVG cards for the GitHub profile README.

Same art direction as anekkumar.in: ink + paper, one orange accent,
Bricolage Grotesque for display, Geist Mono for facts, Caveat for
hand-written notes. Fonts are subset and embedded so the cards look
identical everywhere. All numbers are real (Search Console, Meta Ads
Manager, Semrush; Nov 2026).

Run:  python tools/build_svgs.py   (needs fonttools, brotli, Pillow)
Fonts: Bricolage Grotesque, Caveat, Geist Mono (SIL Open Font License).
"""
import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
OUT = ROOT / "assets"

INK, PAPER, ORANGE, ORANGE_LT, MUTED, DIM, LINE, GREEN = "#0d0d0c", "#f1f0ec", "#e2571f", "#ff8a5c", "#a9a69d", "#7f7c74", "#2b2a27", "#4be37a"
SANS_FALLBACK = '"Segoe UI", -apple-system, Helvetica, Arial, sans-serif'


class Font:
    def __init__(self, file, family):
        self.path = FONTS / file
        self.family = family
        self.tt = TTFont(self.path)
        self.cmap = self.tt.getBestCmap()
        self.hmtx = self.tt["hmtx"]
        self.upm = self.tt["head"].unitsPerEm
        self.chars = set()

    def use(self, text):
        self.chars.update(text)
        return text

    def width(self, text, size, ls=0.0):
        w = 0
        for ch in text:
            g = self.cmap.get(ord(ch))
            w += self.hmtx[g][0] if g else self.upm * 0.55
        return w * size / self.upm + ls * max(0, len(text) - 1)

    def face(self):
        """@font-face with a woff2 subset holding only the characters used."""
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        tt = TTFont(self.path)
        s = subset.Subsetter(opts)
        s.populate(text="".join(sorted(self.chars | set(" "))))
        s.subset(tt)
        buf = io.BytesIO()
        tt.flavor = "woff2"
        tt.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"@font-face{{font-family:'{self.family}';src:url(data:font/woff2;base64,{b64}) format('woff2');}}"

    def ttf_path(self):
        p = ROOT / "tools" / f".{self.family}.ttf"
        if not p.exists():
            tt = TTFont(self.path)
            tt.flavor = None
            tt.save(p)
        return p


B = Font("bricolage.woff2", "Bric")
C = Font("caveat.woff2", "Hand")
M = Font("geistmono.woff2", "Mono")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body, css, title, desc, fonts):
    faces = "".join(f.face() for f in fonts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>
<defs><filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter></defs>
<style>{faces}
.b{{font-family:'Bric',{SANS_FALLBACK};font-weight:800}}
.m{{font-family:'Mono',Consolas,Menlo,monospace;font-weight:500}}
.h{{font-family:'Hand','Segoe Print','Comic Sans MS',cursive;font-weight:700}}
{css}</style>
{body}
</svg>'''


def card(w, h):
    return (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" fill="{INK}"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" fill="#fff" filter="url(#grain)" opacity=".05"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" fill="none" stroke="{LINE}"/>')


ARROW = '<path d="M8 12c26-6 58 2 76 22s20 34 18 48"/><path d="M88 70l14 14 10-17"/>'
CIRCLE = "M150 14C112 2 46 6 20 32 0 54 14 86 64 98c48 11 112 4 128-26 14-26-16-52-74-58-30-3-56 2-80 12"


# ------------------------------------------------------------------ hero
def hero():
    W, H, X = 1000, 540, 48
    lines = ["I build websites,", "then I bring them", "customers."]
    ls = -3.2
    size = 92
    while max(B.width(l, size, ls) for l in lines) > 610:
        size -= 2
    lh = size * 0.98
    y0 = 128 + size * 0.8
    strip = ["ANEK KUMAR", "FULL STACK DEVELOPER & DIGITAL MARKETER", "NOIDA, IN"]
    for s in strip:
        M.use(s)
    body = [card(W, H)]
    # top fact strip with hairlines
    body.append(f'<line x1="{X}" y1="34" x2="{W - X}" y2="34" stroke="{LINE}"/><line x1="{X}" y1="78" x2="{W - X}" y2="78" stroke="{LINE}"/>')
    x = X
    for i, s in enumerate(strip):
        anchor = "end" if i == 2 else "start"
        tx = W - X if i == 2 else x
        body.append(f'<text class="m strip" x="{tx}" y="61" text-anchor="{anchor}">{esc(s)}</text>')
        if i < 2:
            x += M.width(s, 13, 1.3) + 22
            body.append(f'<line x1="{x - 11}" y1="48" x2="{x - 11}" y2="64" stroke="{LINE}"/>')
    # headline, word by word
    for li, line in enumerate(lines):
        y = y0 + li * lh
        if li == 2:
            wv = B.width(line, size, ls)
            body.append(f'<rect class="marker" x="{X - 6}" y="{y - size * 0.34:.1f}" width="{wv + 14:.1f}" height="{size * 0.36:.1f}" rx="5" fill="{ORANGE}"/>')
        body.append(f'<text class="b head w{li}" x="{X}" y="{y:.1f}" style="font-size:{size}px;letter-spacing:{ls}px">{esc(B.use(line))}</text>')
    # hand note + arrow on the right
    nx = 700
    body.append(f'<g class="note" transform="rotate(-5 {nx + 80} 210)"><text class="h" x="{nx}" y="196" font-size="31" fill="{ORANGE_LT}">{esc(C.use("every number here is"))}</text>'
                f'<text class="h" x="{nx + 6}" y="230" font-size="31" fill="{ORANGE_LT}">{esc(C.use("real. scroll down."))}</text></g>')
    body.append(f'<g class="arrow" transform="translate({nx + 150} 246) scale(1.15) rotate(18)" fill="none" stroke="{ORANGE_LT}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{ARROW}</g>')
    # bottom fact row
    facts = [("now", "Shubharambh Infra Advisors"), ("since", "2023 · 3+ years, 4 companies"), ("open to", "freelance projects")]
    yb = H - 46
    body.append(f'<line x1="{X}" y1="{yb - 36}" x2="{W - X}" y2="{yb - 36}" stroke="{LINE}"/>')
    x = X
    for i, (k, v) in enumerate(facts):
        body.append(f'<text class="m" x="{x}" y="{yb}" font-size="13" fill="{DIM}">{esc(M.use(k))}</text>')
        kx = x + M.width(k, 13) + 10
        body.append(f'<text class="b" x="{kx}" y="{yb + 1}" font-size="18" fill="{PAPER}" letter-spacing="-.3">{esc(B.use(v))}</text>')
        x = kx + B.width(v, 18, -0.3) + 34
    body.append(f'<circle class="pulse" cx="{W - X - 6}" cy="{yb - 6}" r="5" fill="{GREEN}"/>')
    css = f'''
.strip{{font-size:13px;letter-spacing:1.3px;fill:{DIM}}}
.head{{fill:{PAPER};opacity:0;animation:rise .9s cubic-bezier(.2,.8,.2,1) forwards}}
.w1{{animation-delay:.15s}} .w2{{animation-delay:.3s}}
.marker{{transform-box:fill-box;transform-origin:0 50%;transform:rotate(-1.2deg) scaleX(0);animation:mark .7s cubic-bezier(.6,0,.2,1) 1s forwards}}
.note{{opacity:0;animation:fade .6s ease 1.7s forwards}}
.arrow path{{stroke-dasharray:240;stroke-dashoffset:240;animation:draw 1s cubic-bezier(.6,0,.2,1) 2s forwards}}
.arrow path+path{{animation-delay:2.9s;animation-duration:.35s}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 1.8s ease-in-out infinite}}
@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
@keyframes mark{{to{{transform:rotate(-1.2deg) scaleX(1)}}}}
@keyframes fade{{to{{opacity:1}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.35;transform:scale(.7)}}}}'''
    return svg(W, H, "\n".join(body), css, "Anek Kumar: I build websites, then I bring them customers.",
               "Full Stack Developer and Digital Marketer in Noida, India. Now at Shubharambh Infra Advisors, open to freelance projects.", [B, C, M])


# ------------------------------------------------------------------ results
def dots(text, w, h, n):
    f = ImageFont.truetype(str(B.ttf_path()), 10)
    size = 10
    while True:
        f = ImageFont.truetype(str(B.ttf_path()), size + 4)
        bb = f.getbbox(text)
        if bb[2] - bb[0] > w * 0.98 or bb[3] - bb[1] > h * 0.98:
            break
        size += 4
    f = ImageFont.truetype(str(B.ttf_path()), size)
    bb = f.getbbox(text)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=255)
    px = im.load()
    step = 2.0
    while True:
        pts = [(x, y) for y in range(0, h, max(1, round(step))) for x in range(0, w, max(1, round(step))) if px[x, y] > 128]
        if len(pts) <= n * 1.25:
            break
        step += 0.5
    return [pts[int(i * len(pts) / n)] for i in range(n)], step


def results():
    W, H = 1000, 500
    body = [card(W, H)]
    head = "PROOF · SHUBHARAMBH INFRA ADVISORS · 2026"
    body.append(f'<circle class="pulse" cx="44" cy="44" r="5" fill="{GREEN}"/><text class="m" x="58" y="49" font-size="13" letter-spacing="1.3" fill="{DIM}">{esc(M.use(head))}</text>')
    src = "search console · meta ads manager · semrush"
    body.append(f'<text class="m" x="{W - 44}" y="49" font-size="12.5" fill="{DIM}" text-anchor="end">{esc(M.use(src))}</text>')
    # left: 1,149 drawn with 1,149 dots
    bx, by, bw, bh = 40, 92, 440, 270
    pts, step = dots("1,149", bw, bh, 1149)
    r = max(1.25, min(2.4, step * 0.42))
    groups = {}
    for (x, y) in pts:
        groups.setdefault(int(x / bw * 14), []).append((x, y))
    body.append('<g fill="%s">' % ORANGE)
    for gi in sorted(groups):
        circles = "".join(f'<circle cx="{bx + x:.1f}" cy="{by + y:.1f}" r="{r:.2f}"/>' for x, y in groups[gi])
        body.append(f'<g class="fall" style="animation-delay:{gi * 0.07:.2f}s">{circles}</g>')
    body.append("</g>")
    cap1 = "each dot is one real lead from Meta Ads"
    body.append(f'<text class="m" x="{bx + 4}" y="{by + bh + 34}" font-size="13" fill="{MUTED}">{esc(M.use(cap1))}</text>')
    body.append(f'<text class="h note" x="{bx + 6}" y="{by + bh + 74}" font-size="28" fill="{ORANGE_LT}" transform="rotate(-3 {bx + 120} {by + bh + 70})">{esc(C.use("1,149 of them, at ₹288 each"))}</text>')
    # right: ledger
    rx, rw = 528, W - 528 - 44
    rows = [("#1", "on Google for 17 keywords", '"best property advisor in noida"', True),
            ("1.22M", "Google impressions in 6 months", "up from 3.43k · 355×", False),
            ("3.8K", "keywords ranking on Google", "from zero in five months", False),
            ("1 in 10", "leads became a site meeting", "≈ 115 meetings from 1,149 leads", False)]
    y = 98
    rh = 92
    body.append(f'<line x1="{rx}" y1="{y - 8}" x2="{rx + rw}" y2="{y - 8}" stroke="{PAPER}" stroke-opacity=".5"/>')
    for i, (big, lab, sub, circ) in enumerate(rows):
        cy = y + i * rh
        bigw = B.width(big, 46, -1.6)
        body.append(f'<g class="row" style="animation-delay:{0.35 + i * 0.15:.2f}s">')
        body.append(f'<text class="b" x="{rx}" y="{cy + 50}" font-size="46" letter-spacing="-1.6" fill="{ORANGE if circ else PAPER}">{esc(B.use(big))}</text>')
        tx = rx + max(bigw, 128) + 22
        body.append(f'<text class="b" x="{tx}" y="{cy + 34}" font-size="18" letter-spacing="-.3" fill="{PAPER}">{esc(B.use(lab))}</text>')
        body.append(f'<text class="m" x="{tx}" y="{cy + 58}" font-size="12.5" fill="{DIM}">{esc(M.use(sub))}</text>')
        body.append("</g>")
        if circ:
            sx, sy = (bigw + 34) / 200, 66 / 110
            body.append(f'<path class="circ" d="{CIRCLE}" transform="translate({rx - 17} {cy + 4}) scale({sx:.3f} {sy:.3f})" fill="none" stroke="{ORANGE_LT}" stroke-width="{3.4 / ((sx + sy) / 2):.2f}" stroke-linecap="round"/>')
        body.append(f'<line x1="{rx}" y1="{cy + rh - 8}" x2="{rx + rw}" y2="{cy + rh - 8}" stroke="{LINE}"/>')
    css = f'''
.fall{{opacity:0;animation:fall 1.1s cubic-bezier(.2,.8,.2,1) forwards}}
.row{{opacity:0;animation:rise .8s cubic-bezier(.2,.8,.2,1) forwards}}
.note{{opacity:0;animation:fade .6s ease 1.9s forwards}}
.circ{{stroke-dasharray:540;stroke-dashoffset:540;animation:draw 1.2s cubic-bezier(.6,0,.2,1) 1.2s forwards}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 1.8s ease-in-out infinite}}
@keyframes fall{{from{{opacity:0;transform:translateY(-70px)}}to{{opacity:1;transform:none}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@keyframes fade{{to{{opacity:1}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.35;transform:scale(.7)}}}}'''
    return svg(W, H, "\n".join(body), css, "Proof: real results by Anek Kumar",
               "1,149 Meta Ads leads drawn as 1,149 dots. Number 1 on Google for 17 keywords, 1.22 million impressions in 6 months, 3,800 keywords ranking, 1 in 10 leads became a site meeting.", [B, C, M])


# ------------------------------------------------------------------ proof (real Search Console chart)
def proof():
    W = 1000
    img = Image.open(ROOT / "assets" / "gsc-chart.webp").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=82)
    b64 = base64.b64encode(buf.getvalue()).decode()
    iw = 860
    ih = round(img.height * iw / img.width)
    ix, iy = 70, 120
    H = iy + ih + 64
    body = [card(W, H)]
    head = "GOOGLE SEARCH CONSOLE · SHUBHARAMBHINFRAADVISORS.COM · 6 MONTHS"
    body.append(f'<text class="m" x="44" y="52" font-size="13" letter-spacing="1.3" fill="{DIM}">{esc(M.use(head))}</text>')
    body.append(f'<text class="b" x="44" y="94" font-size="30" letter-spacing="-1" fill="{PAPER}">{esc(B.use("3.43k"))}<tspan fill="{DIM}">{esc(B.use("  →  "))}</tspan><tspan fill="{GREEN}">{esc(B.use("1.22M impressions"))}</tspan></text>')
    body.append(f'<rect x="{ix - 10}" y="{iy - 10}" width="{iw + 20}" height="{ih + 20}" rx="12" fill="#fff"/>')
    body.append(f'<g class="wipe"><image x="{ix}" y="{iy}" width="{iw}" height="{ih}" href="data:image/webp;base64,{b64}"/></g>')
    body.append(f'<rect class="cover" x="{ix - 10}" y="{iy - 10}" width="{iw + 20}" height="{ih + 20}" rx="12" fill="{INK}"/>')
    body.append(f'<g class="note" transform="rotate(-4 760 70)"><text class="h" x="640" y="70" font-size="29" fill="{ORANGE_LT}">{esc(C.use("not edited. straight from"))}</text>'
                f'<text class="h" x="652" y="100" font-size="29" fill="{ORANGE_LT}">{esc(C.use("Google Search Console"))}</text></g>')
    body.append(f'<g class="arrow" transform="translate(902 92) scale(.8) rotate(40)" fill="none" stroke="{ORANGE_LT}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">{ARROW}</g>')
    cap = "real screenshot · 15 nov 2026"
    body.append(f'<text class="m" x="{W - 44}" y="{H - 26}" font-size="12.5" fill="{DIM}" text-anchor="end">{esc(M.use(cap))}</text>')
    css = '''
.cover{transform-box:fill-box;transform-origin:100% 50%;animation:uncover 1.4s cubic-bezier(.65,0,.35,1) .3s forwards}
.note{opacity:0;animation:fade .6s ease 1.6s forwards}
.arrow path{stroke-dasharray:240;stroke-dashoffset:240;animation:draw .9s cubic-bezier(.6,0,.2,1) 1.9s forwards}
.arrow path+path{animation-delay:2.7s;animation-duration:.35s}
@keyframes uncover{to{transform:scaleX(0)}}
@keyframes fade{to{opacity:1}}
@keyframes draw{to{stroke-dashoffset:0}}'''
    return svg(W, H, "\n".join(body), css, "Real Google Search Console chart",
               "Search Console impressions for shubharambhinfraadvisors.com rising from 3.43k to 1.22 million in six months.", [B, C, M])


# ------------------------------------------------------------------ terminal
def terminal():
    W, H = 1000, 362
    fs = 15
    cw = M.width("x", fs)
    body = [card(W, H)]
    body.append(f'<text class="m" x="24" y="30" font-size="12.5" fill="{DIM}">{esc(M.use("anek@portfolio: ~"))}</text><line x1="0" y1="46" x2="{W}" y2="46" stroke="{LINE}"/>')
    script = [
        ("whoami", [[("o", "Anek Kumar · Full Stack Developer & Digital Marketer · Noida, India")]]),
        ("cat stack.txt", [[("hl", "code    "), ("o", "Python · Django · PHP · MySQL · JavaScript · React · Node.js")],
                           [("hl", "growth  "), ("o", "SEO · Meta Ads · Google Ads · Pixel + CAPI · GA4 · WhatsApp API")]]),
        ("./results --live", [[("ok", "✔ #1 on Google · 17 keywords   ✔ 1.22M impressions   ✔ 1,149 leads")]]),
        ("hire anek", [[("hl", "→ "), ("o", "wa.me/919518848804 · anekkumar9518@gmail.com · anekkumar.in")]]),
    ]
    defs, y, t = [], 84, 0.4
    for i, (cmd, outs) in enumerate(script):
        n = len(cmd)
        dur = 0.07 * n
        vals = ";".join(f"{cw * k:.1f}" for k in range(n + 1))
        defs.append(f'<clipPath id="c{i}"><rect x="58" y="{y - 18}" height="26" width="0"><animate attributeName="width" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze" calcMode="discrete" values="{vals}"/></rect></clipPath>')
        body.append(f'<text class="m out" x="30" y="{y}" font-size="{fs}" fill="{ORANGE_LT}" style="animation-delay:{max(0, t - 0.3):.2f}s">❯</text>')
        body.append(f'<text class="m" x="58" y="{y}" font-size="{fs}" fill="{PAPER}" clip-path="url(#c{i})">{esc(M.use(cmd))}</text>')
        t += dur + 0.35
        for line in outs:
            y += 24
            spans = "".join(f'<tspan class="{c}">{esc(M.use(txt))}</tspan>' for c, txt in line)
            body.append(f'<text class="m out" x="58" y="{y}" font-size="{fs}" style="animation-delay:{t:.2f}s">{spans}</text>')
            t += 0.12
        y += 38
        t += 0.45
    body.insert(1, "<defs>" + "".join(defs) + "</defs>")
    body.append(f'<rect class="cur" x="58" y="{y - 32}" width="9" height="18" fill="{ORANGE_LT}" style="animation-delay:{t:.2f}s"/>')
    css = f'''
.m{{white-space:pre}} .o{{fill:#c9c6bd}} .hl{{fill:#ffb08a}} .ok{{fill:{GREEN}}}
.out{{opacity:0;animation:fade .01s forwards}}
.cur{{opacity:0;animation:blink 1s steps(1) infinite}}
@keyframes fade{{to{{opacity:1}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}'''
    M.use("❯✔→")
    return svg(W, H, "\n".join(body), css, "anek@portfolio terminal", "whoami, cat stack.txt, ./results --live, hire anek", [M])


# ------------------------------------------------------------------ footer
def footer():
    W, H = 1000, 280
    body = [card(W, H)]
    word, tld = "anekkumar", ".in"
    size = 150
    while B.width(word + tld, size, -7) > W - 96:
        size -= 2
    body.append(f'<text class="b big" x="48" y="{H - 104}" font-size="{size}" letter-spacing="-7" fill="{PAPER}">{esc(B.use(word))}<tspan fill="{ORANGE}">{esc(B.use(tld))}</tspan></text>')
    body.append(f'<line x1="48" y1="{H - 72}" x2="{W - 48}" y2="{H - 72}" stroke="{LINE}"/>')
    left = "whatsapp +91 95188 48804 · anekkumar9518@gmail.com"
    body.append(f'<text class="m" x="48" y="{H - 40}" font-size="13" fill="{MUTED}">{esc(M.use(left))}</text>')
    body.append(f'<text class="h note" x="{W - 48}" y="{H - 36}" font-size="30" fill="{ORANGE_LT}" text-anchor="end">{esc(C.use("let\'s build something that sells."))}</text>')
    css = '''
.big{opacity:0;animation:rise 1s cubic-bezier(.2,.8,.2,1) .1s forwards}
.note{opacity:0;animation:fade .6s ease 1s forwards}
@keyframes rise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
@keyframes fade{to{opacity:1}}'''
    return svg(W, H, "\n".join(body), css, "anekkumar.in", "WhatsApp +91 95188 48804, anekkumar9518@gmail.com", [B, C, M])


if __name__ == "__main__":
    # build every card first so each font collects all characters, then write (faces are subset per file)
    for name, fn in [("hero", hero), ("results", results), ("proof", proof), ("terminal", terminal), ("footer", footer)]:
        B.chars.clear(); C.chars.clear(); M.chars.clear()
        out = fn()
        (OUT / f"{name}.svg").write_text(out, encoding="utf-8", newline="\n")
        print(f"{name}.svg  {len(out) // 1024} KB")
