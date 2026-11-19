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
import json
from datetime import datetime, timedelta, timezone
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


# ------------------------------------------------------------------ editor
# The hero: a code editor. The profile is typed out as a TypeScript object,
# then the terminal below shows a real health check of the six live sites
# (data/status.json, refreshed daily by GitHub Actions) next to each one's
# real result. Typing uses SMIL clip widths, so it runs inside an <img>.
KW, STR, NUM, KEY, PUN, FN, COM = ORANGE_LT, "#e3c98f", GREEN, "#ece9e1", "#8d8a82", "#ffb08a", "#6f6c65"
CODE = [
    [("c", "// Anek Kumar, Noida, India")],
    [("k", "export const "), ("f", "anek"), ("p", " = {")],
    [("y", "  role"), ("p", ": ["), ("s", '"Full Stack Developer"'), ("p", ", "), ("s", '"Digital Marketer"'), ("p", "],")],
    [("y", "  now"), ("p", ": "), ("s", '"Shubharambh Infra Advisors"'), ("p", ",")],
    [("y", "  code"), ("p", ": ["), ("s", '"Python"'), ("p", ", "), ("s", '"Django"'), ("p", ", "), ("s", '"PHP"'), ("p", ", "), ("s", '"MySQL"'), ("p", ", "), ("s", '"React"'), ("p", "],")],
    [("y", "  growth"), ("p", ": ["), ("s", '"SEO"'), ("p", ", "), ("s", '"Meta Ads"'), ("p", ", "), ("s", '"Google Ads"'), ("p", ", "), ("s", '"GA4"'), ("p", "],")],
    [("y", "  since"), ("p", ": "), ("n", "2023"), ("p", ",")],
    [("y", "  openTo"), ("p", ": "), ("s", '"freelance"'), ("p", ",")],
    [("p", "};")],
    [],
    [("k", "await "), ("f", "anek"), ("p", "."), ("f", "healthcheck"), ("p", "();  "), ("c", "// live, runs daily ↓")],
]
DEPLOYS = [  # domain, what I did, real result
    ("shubharambhinfraadvisors.com", "site + seo", "#1 on Google for 55 keywords"),
    ("matrixacres.in", "crm + ads", "300+ module CRM"),
    ("visionwavetechnology.com", "website", "29 free tools"),
    ("lmcstore.in", "e-commerce", "ayurvedic e-commerce"),
    ("harisabziwala.com", "site + app", "grocery site + rider app"),
    ("ezzycommerce.store", "e-commerce", "streetwear e-commerce"),
]
TOK = {"c": COM, "k": KW, "f": FN, "p": PUN, "y": KEY, "s": STR, "n": NUM}


RED = "#ff6b5b"


def load_status():
    """Real health check from data/status.json: ({host: site}, 'DD Mon YYYY, HH:MM IST')."""
    data = json.loads((ROOT / "data" / "status.json").read_text(encoding="utf-8"))
    when = datetime.strptime(data["checked"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    ist = when.astimezone(timezone(timedelta(hours=5, minutes=30)))
    return {x["host"]: x for x in data["sites"]}, ist.strftime("%d %b %Y, %H:%M IST").lstrip("0")


def cross(x, y):
    return f'<path d="M{x + 1} {y - 10}l8 8M{x + 9} {y - 10}l-8 8" fill="none" stroke="{RED}" stroke-width="2" stroke-linecap="round"/>'


def check(x, y):
    return f'<path d="M{x} {y - 5}l3.6 3.8L{x + 10} {y - 11}" fill="none" stroke="{GREEN}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'


def editor():
    W = 1000
    fs, lh = 15, 24
    cw = M.width("x", fs)
    tfs, tlh = 14, 23
    tcw = M.width("x", tfs)
    defs, body = [], []
    t = 0.5  # running clock (seconds)

    def typed(i, x, y, n, per, size_h):
        """clip that reveals n characters starting at x, one per `per` seconds, from time t."""
        nonlocal t
        c = cw if size_h == fs else tcw
        vals = ";".join(f"{c * k:.1f}" for k in range(n + 1))
        defs.append(f'<clipPath id="t{i}"><rect x="{x}" y="{y - size_h - 2}" height="{size_h + 10}" width="0">'
                    f'<animate attributeName="width" begin="{t:.2f}s" dur="{per * n:.2f}s" fill="freeze" calcMode="discrete" values="{vals}"/></rect></clipPath>')
        t += per * n

    # window chrome
    TB = 42
    body.append(f'<line x1="0" y1="{TB}" x2="{W}" y2="{TB}" stroke="{LINE}"/>')
    for k in range(3):
        body.append(f'<circle cx="{24 + k * 18}" cy="{TB / 2}" r="5" fill="#2e2d2a"/>')
    tabs = [("anek.ts", True), ("results.json", False), ("README.md", False)]
    x = 92
    for name, active in tabs:
        tw = M.width(name, 12.5) + 36
        if active:
            body.append(f'<rect x="{x}" y="1" width="{tw:.1f}" height="{TB - 1}" fill="#151513"/>'
                        f'<rect x="{x}" y="1" width="{tw:.1f}" height="2" fill="{ORANGE}"/>')
        body.append(f'<text class="m" x="{x + 18}" y="{TB / 2 + 4.5}" font-size="12.5" fill="{PAPER if active else DIM}">{esc(M.use(name))}</text>')
        x += tw
    body.append(f'<text class="m" x="{W - 24}" y="{TB / 2 + 4.5}" font-size="12" fill="{DIM}" text-anchor="end">{esc(M.use("~/anekkumar9518"))}</text>')

    # code
    GX, CX = 30, 78
    y = TB + 34
    for i, line in enumerate(CODE):
        body.append(f'<text class="m" x="{GX + 22}" y="{y}" font-size="13" fill="#4a4843" text-anchor="end">{i + 1}</text>')
        text = "".join(s for _, s in line)
        if text:
            spans = "".join(f'<tspan fill="{TOK[c]}"{" font-style=\"italic\"" if c == "c" else ""}>{esc(M.use(s))}</tspan>' for c, s in line)
            typed(i, CX, y, len(text), 0.011, fs)
            body.append(f'<text class="m" x="{CX}" y="{y}" font-size="{fs}" clip-path="url(#t{i})">{spans}</text>')
            t += 0.04
        y += lh
    yCodeEnd = y - lh
    t += 0.3
    # minimap
    my = TB + 22
    for line in CODE:
        mx = W - 92
        for c, s in line:
            if s.strip():
                lead = len(s) - len(s.lstrip())
                body.append(f'<rect x="{mx + lead * 0.9:.1f}" y="{my}" width="{len(s.strip()) * 0.9:.1f}" height="2.2" fill="{TOK[c]}" opacity=".45"/>')
            mx += len(s) * 0.9
        my += 4.4

    # panel
    PY = yCodeEnd + 30
    body.append(f'<line x1="0" y1="{PY}" x2="{W}" y2="{PY}" stroke="{LINE}"/>')
    px = 30
    for name, active in [("PROBLEMS", False), ("OUTPUT", False), ("TERMINAL", True)]:
        body.append(f'<text class="m" x="{px}" y="{PY + 26}" font-size="11" letter-spacing="1.4" fill="{PAPER if active else DIM}">{esc(M.use(name))}</text>')
        w = M.width(name, 11, 1.4)
        if active:
            body.append(f'<rect x="{px}" y="{PY + 34}" width="{w:.1f}" height="1.5" fill="{ORANGE}"/>')
        px += w + 28

    # terminal
    TX = 30
    y = PY + 66
    prompt = "anek@noida ~/work $ "
    cmd = "npm run healthcheck"
    status, checked = load_status()
    body.append(f'<text class="m out" x="{TX}" y="{y}" font-size="{tfs}" style="animation-delay:{t:.2f}s"><tspan fill="{ORANGE_LT}">{esc(M.use(prompt))}</tspan></text>')
    cx = TX + tcw * len(prompt)
    t += 0.3
    typed("cmd", cx, y, len(cmd), 0.045, tfs)
    body.append(f'<text class="m" x="{cx:.1f}" y="{y}" font-size="{tfs}" fill="{PAPER}" clip-path="url(#tcmd)">{esc(M.use(cmd))}</text>')
    t += 0.5
    y += tlh + 6
    up = 0
    for dom, what, res in DEPLOYS:
        st = status.get(dom, {"up": False, "code": None, "ms": 0})
        up += st["up"]
        code = f'{st["code"]} OK' if st["up"] else (f'{st["code"]}' if st["code"] else "no reply")
        ms = f'{st["ms"]}ms' if st["up"] else ""
        g = [check(TX + 1, y) if st["up"] else cross(TX + 1, y), f'<text class="m" x="{TX + 22}" y="{y}" font-size="{tfs}">'
             f'<tspan fill="{PAPER}">{esc(M.use(dom.ljust(30)))}</tspan><tspan fill="{GREEN if st["up"] else RED}">{esc(M.use(code.ljust(8)))}</tspan>'
             f'<tspan fill="{DIM}">{esc(M.use(ms.rjust(7)))}   </tspan>'
             f'<tspan fill="{ORANGE_LT if any(ch.isdigit() for ch in res) else MUTED}">{esc(M.use(res))}</tspan></text>']
        body.append(f'<g class="out" style="animation-delay:{t:.2f}s">{"".join(g)}</g>')
        t += 0.28
        y += tlh
    y += 6
    down = len(DEPLOYS) - up
    summ = [(f"{up} up, {down} down.", PAPER), (f"  checked {checked} · runs daily on GitHub Actions", DIM)]
    spans = "".join(f'<tspan fill="{c}">{esc(M.use(s))}</tspan>' for s, c in summ)
    body.append(f'<text class="m out" x="{TX}" y="{y}" font-size="{tfs}" style="animation-delay:{t:.2f}s">{spans}</text>')
    t += 0.4
    y += tlh
    summ = [("next site could be yours: ", DIM), ("wa.me/919518848804", ORANGE_LT)]
    spans = "".join(f'<tspan fill="{c}">{esc(M.use(s))}</tspan>' for s, c in summ)
    body.append(f'<text class="m out" x="{TX}" y="{y}" font-size="{tfs}" style="animation-delay:{t:.2f}s">{spans}</text>')
    t += 0.5
    y += tlh + 6
    body.append(f'<text class="m out" x="{TX}" y="{y}" font-size="{tfs}" fill="{ORANGE_LT}" style="animation-delay:{t:.2f}s">{esc(M.use(prompt))}</text>')
    body.append(f'<rect class="cur" x="{TX + tcw * len(prompt):.1f}" y="{y - 13}" width="8.5" height="17" fill="{ORANGE_LT}" style="animation-delay:{t:.2f}s"/>')

    # status bar
    SB = y + 26
    H = SB + 28
    body.append(f'<path d="M0 {SB}H{W}V{H - 14}a14 14 0 0 1-14 14H14a14 14 0 0 1-14-14Z" fill="{ORANGE}"/>')
    sy = SB + 18.5
    branch = (f'<g transform="translate(22 {SB + 7})" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round">'
              '<circle cx="3" cy="2.5" r="2"/><circle cx="3" cy="11.5" r="2"/><circle cx="11" cy="4.5" r="2"/><path d="M3 4.5v5M11 6.5c0 3-8 2-8 3"/></g>')
    body.append(branch)
    left = f"main    0 errors    {up}/{len(DEPLOYS)} sites up"
    right = f"Ln {len(CODE)}, Col {len(''.join(s for _, s in CODE[-1])) + 1}    UTF-8    TypeScript    • available for freelance"
    body.append(f'<text class="m" x="42" y="{sy}" font-size="12" fill="{INK}" font-weight="600">{esc(M.use(left))}</text>')
    body.append(f'<text class="m" x="{W - 20}" y="{sy}" font-size="12" fill="{INK}" font-weight="600" text-anchor="end">{esc(M.use(right))}</text>')

    frame = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{INK}"/>'
             f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="#fff" filter="url(#grain)" opacity=".04"/>')
    border = f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{LINE}"/>'
    css = '''
.m{white-space:pre}
.out{opacity:0;animation:fade .01s forwards}
.cur{opacity:0;animation:blink 1s steps(1) infinite}
@keyframes fade{to{opacity:1}}
@keyframes blink{0%{opacity:1}50%{opacity:0}}'''
    route = "; ".join(f"{d}: {'up' if status.get(d, {}).get('up') else 'down'}, {r}" for d, w, r in DEPLOYS)
    return svg(W, H, frame + f"<defs>{''.join(defs)}</defs>" + "\n".join(body) + border, css,
               "anek.ts: Anek Kumar, Full Stack Developer and Digital Marketer",
               "A code editor typing out Anek's profile (Python, Django, PHP, MySQL, React; SEO, Meta Ads, Google Ads, GA4; since 2023; open to freelance), "
               f"then a terminal with a live health check of six sites ({up} up, checked {checked}): {route}. Next site could be yours: wa.me/919518848804.", [M])


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
    rows = [("#1", "on Google for 55 keywords", '"best property advisor in noida"', True),
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
               "1,149 Meta Ads leads drawn as 1,149 dots. Number 1 on Google for 55 keywords, 1.22 million impressions in 6 months, 3,800 keywords ranking, 1 in 10 leads became a site meeting.", [B, C, M])


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
    for name, fn in [("editor", editor), ("results", results), ("proof", proof), ("footer", footer)]:
        B.chars.clear(); C.chars.clear(); M.chars.clear()
        out = fn()
        (OUT / f"{name}.svg").write_text(out, encoding="utf-8", newline="\n")
        print(f"{name}.svg  {len(out) // 1024} KB")
