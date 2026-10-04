"""Build yaqzan's network map.

Everything on the map lives in this file: stations, lines, what each card says.
Edit it and run `python build.py`. It writes index.html (the map is baked in
as SVG, app.js only animates it) and the teaser for the profile README in
../yaqzans/assets/map.svg.

The map is a hub: every line starts at aiub and runs out to one part of my
work, so it reads at a glance without clicking anything.
"""
import hashlib
import json
import math
import os


# --------------------------------------------------------------------------
# stations. tag = the line printed under the name on the map.
# side = where the name goes: r, l, t, b (or hub)
# --------------------------------------------------------------------------
def st(name, tag, x, y, side, text, links=(), related=()):
    return dict(name=name, tag=tag, x=x, y=y, side=side, text=text, links=list(links), related=list(related))


S = {
    "aiub": st("aiub", "bsc cse, class of 2027", 800, 470, "hub",
               "american international university-bangladesh. bsc in computer science and engineering, major in "
               "computational theory, minor in data science. cgpa 3.96, dean's list twice, on an academic "
               "scholarship. every line on this map starts here."),

    # projects, out to the east
    "pm25": st("pm2.5 monitor", "air quality alerts, esp32", 960, 310, "t",
               "pocket air quality monitor plus a react native app. it only alerts on real spikes, not on dhaka's "
               "normal bad air. two weeks of field testing: about 4 alerts a day instead of dozens, and people "
               "actually read them."),
    "hand": st("robotic hand", "copies your hand, no gloves", 1130, 310, "b",
               "a camera watches your hand and a 7-servo robotic hand copies it. no gloves, no sensors. 88 ms end "
               "to end at 24.6 fps, built for about 2,800 taka. it became the qpain paper on the papers line.",
               [("read the paper", "https://doi.org/10.1109/QPAIN69676.2026.11545528")], ["qpain"]),
    "oshud": st("oshudbot", "bangla medicine bot", 1400, 210, "t",
                "21,714 medicine brands, ask in bangla, english or banglish. answers in about 15 ms on a cpu. it "
                "used to carry 1.1 gb of models, swapped them for transliteration and fuzzy matching and lost "
                "nothing.",
                [("repo", "https://github.com/yaqzans/oshudbot"), ("try it", "https://oshudbot.streamlit.app/")]),
    "medease": st("medease bd", "offline medicine llm", 1570, 210, "t",
                  "the heavier sibling of oshudbot. rag over 21,000+ medicines plus a gemma 3 4b fine-tuned on "
                  "36,000+ medicine q&a pairs, running fully offline.", [], ["oshud"]),
    "vehicle": st("vehicle recognition", "yolo + convnext", 1300, 310, "b",
                  "bangladeshi road vehicles on rsud20k. yolo26n finds them, convnext-tiny names every crop. code, "
                  "results and the paper.",
                  [("repo", "https://github.com/yaqzans/cvpr-two-stage-vehicle-recognition")]),

    # papers, out to the west
    "qpain": st("gesture robotic hand", "ieee qpain 2026", 640, 310, "t",
                "Gesture Controlled Robotic Hand Designed for Enhancing Industrial Automation and Innovation. "
                "ieee qpain 2026. second and corresponding author.",
                [("read the paper", "https://doi.org/10.1109/QPAIN69676.2026.11545528")], ["hand"]),
    "blood": st("blood-like solution", "analytical chemistry letters", 470, 310, "b",
                "Development of a Simulated Blood-Like Solution for Medical Experiments. analytical chemistry "
                "letters, 2025. first shown at the international conference on physics 2024. fifth author.",
                [("read the paper", "https://doi.org/10.1080/22297928.2025.2533331")]),
    "agile": st("agile + waterfall", "ieom bangladesh 2025", 280, 310, "b",
                "Evaluating the Performance of Agile-Waterfall Integrated Approaches in Large Scale Engineering "
                "Projects in Bangladesh. ieom bangladesh 2025. fifth author.",
                [("read the paper", "https://doi.org/10.46254/BA08.20250467")]),
    "hybrid": st("human-ai animation", "icctass 2025", 180, 210, "r",
                 "A Hybrid Human-AI Model for Sustainable Innovation in Media and Animation. presented at icctass "
                 "2025. third author."),

    # out & about, south-west
    "undp": st("undp roundtable", "youth and the sdgs", 640, 630, "b",
               "picked to represent aiub at let's talk with the undp resident representative, a roundtable on "
               "youth and the sdgs."),
    "embassy": st("u.s. embassy", "ai workshop", 470, 630, "t",
                  "ai workshop at the american center, dhaka. the faculty of science and technology sent me to "
                  "represent aiub."),
    "english": st("english club", "organiser, 10+ events", 370, 730, "r",
                  "organiser and content writer at the aiub english club. 10+ events and workshops, 50+ members."),

    # side projects, south-east
    "md": st("markdown converter", "anything to markdown", 960, 630, "b",
             "pdf, word, powerpoint or excel in, clean markdown out. one windows exe, nothing to install.",
             [("repo", "https://github.com/yaqzans/markdown-converter-app")]),
    "who": st("who should count more", "voting sim, playable", 1130, 630, "t",
              "should educated votes count more? set it up, run the election, see who wins.",
              [("play", "https://yaqzans.github.io/who-should-count-more/"),
               ("repo", "https://github.com/yaqzans/who-should-count-more")]),
    "ttt": st("tictactoe ∞", "4 pieces, then move them", 1230, 730, "l",
              "tic-tac-toe where you only get 4 pieces, then you have to move them. has a bot with a "
              "difficulty slider.",
              [("play", "https://yaqzans.github.io/TicTacToeInfinity/"),
               ("repo", "https://github.com/yaqzans/TicTacToeInfinity")]),
}

# lines: id -> (name, color, stations from the hub outwards)
L = {
    "red":    ("projects", "#dc241f", ["aiub", "pm25", "hand", "vehicle", "oshud", "medease"]),
    "blue":   ("papers", "#0019a8", ["aiub", "qpain", "blood", "agile", "hybrid"]),
    "yellow": ("out & about", "#e8a200", ["aiub", "undp", "embassy", "english"]),
    "cyan":   ("side projects", "#0098d4", ["aiub", "md", "who", "ttt"]),
}

W, H = 1600, 900
INK, PAPER, SOFT, ZONE = "#1d1d1f", "#ffffff", "#6e6e73", "#ebebee"
FONT = "Inter,'Helvetica Neue',Arial,sans-serif"
LW = 7  # line width, thin like a real network map


# --------------------------------------------------------------------------
# geometry: lines run at 0, 45 and 90 degrees with rounded bends
# --------------------------------------------------------------------------
def leg(a, b):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    d = min(abs(dx), abs(dy))
    sx, sy = (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)
    if d == 0 or abs(dx) == abs(dy):
        return [b]
    return [(x1 + sx * d, y1 + sy * d), b]  # diagonal first, then straight


def route(stops):
    pts = [(S[stops[0]]["x"], S[stops[0]]["y"])]
    for sid in stops[1:]:
        pts += leg(pts[-1], (S[sid]["x"], S[sid]["y"]))
    return pts


def rounded(pts, r=40):
    d = f"M{pts[0][0]},{pts[0][1]}"
    for i in range(1, len(pts) - 1):
        (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[i + 1]
        if (bx - ax) * (cy - by) == (by - ay) * (cx - bx):
            continue
        l1, l2 = math.dist((ax, ay), (bx, by)), math.dist((bx, by), (cx, cy))
        k = min(r, l1 / 2, l2 / 2)
        p1 = (bx - (bx - ax) / l1 * k, by - (by - ay) / l1 * k)
        p2 = (bx + (cx - bx) / l2 * k, by + (cy - by) / l2 * k)
        d += f" L{p1[0]:.1f},{p1[1]:.1f} Q{bx},{by} {p2[0]:.1f},{p2[1]:.1f}"
    return d + f" L{pts[-1][0]},{pts[-1][1]}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def lines_at(sid):
    return [lid for lid, (_, _, stops) in L.items() if sid in stops]


def marker(x, y, hub=False):
    if hub:
        return f'<circle class="sh" cx="{x}" cy="{y}" r="15" fill="#fff" stroke="{INK}" stroke-width="3.2"/>'
    return f'<circle class="sh" cx="{x}" cy="{y}" r="8" fill="#fff" stroke="{INK}" stroke-width="2.8"/>'


def label(sid):
    s = S[sid]
    x, y, side = s["x"], s["y"], s["side"]
    if side == "hub":
        return (f'<text x="{x}" y="{y + 70}" text-anchor="middle" class="lbl hubname">{esc(s["name"].upper())}</text>'
                f'<text x="{x}" y="{y + 90}" text-anchor="middle" class="tag">{esc(s["tag"])}</text>')
    nx, ny, anchor = {"r": (x + 16, y + 1, "start"), "l": (x - 16, y + 1, "end"),
                      "t": (x, y - 36, "middle"), "b": (x, y + 30, "middle")}[side]
    return (f'<text x="{nx}" y="{ny}" text-anchor="{anchor}" class="lbl">{esc(s["name"])}</text>'
            f'<text x="{nx}" y="{ny + 19}" text-anchor="{anchor}" class="tag">{esc(s["tag"])}</text>')


def arrow(a, b, color):
    """The line runs on past its last stop into an arrowhead: more to come."""
    (x1, y1), (x2, y2) = a, b
    n = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / n, (y2 - y1) / n
    sx, sy = x2 + ux * 34, y2 + uy * 34
    tx, ty = sx + ux * 20, sy + uy * 20
    px, py = -uy * 13, ux * 13
    return (f'<path d="M{x2},{y2} L{sx:.1f},{sy:.1f}" stroke="{color}" stroke-width="{LW}" fill="none"/>'
            f'<path d="M{tx:.1f},{ty:.1f} L{sx + px:.1f},{sy + py:.1f} L{sx - px:.1f},{sy - py:.1f}Z" fill="{color}"/>')


def badge_box(lid):
    """Where the line's name goes: past the arrow, along the last leg."""
    name, color, stops = L[lid]
    pts = route(stops)
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    n = math.dist((ax, ay), (bx, by))
    ux, uy = (bx - ax) / n, (by - ay) / n
    w = len(name) * 9.2 + 20
    tip = (bx + ux * 54, by + uy * 54)
    if abs(ux) > .9:      # horizontal end: badge carries on sideways
        cx, cy = tip[0] + ux * (12 + w / 2), tip[1]
    elif abs(uy) > .9:    # vertical end
        cx, cy = tip[0], tip[1] + uy * 24
    else:                 # diagonal end: badge sits just past the tip
        cx, cy = tip[0] + ux * (10 + w / 2), tip[1] + uy * 22
    return name, color, cx, cy, w


def line_badge(lid):
    """The line's name, printed past its arrow."""
    name, color, cx, cy, w = badge_box(lid)
    return (f'<g class="badge" data-line="{lid}"><rect x="{cx - w / 2:.0f}" y="{cy - 13:.0f}" width="{w:.0f}" height="26" rx="2" fill="{color}"/>'
            f'<text x="{cx:.0f}" y="{cy + 5:.0f}" text-anchor="middle" fill="#fff" font-family="{FONT}" font-size="14" '
            f'font-weight="700" letter-spacing=".6">{esc(name.upper())}</text></g>')


def view():
    """Bounding box of everything drawn, with a margin: the part of the canvas the poster shows."""
    xs = [v["x"] for v in S.values()]
    ys = [v["y"] for v in S.values()]
    for lid in L:
        _, _, cx, cy, w = badge_box(lid)
        xs += [cx - w / 2, cx + w / 2]
        ys += [cy - 14, cy + 14]
    x0, x1 = min(xs) - 40, max(xs) + 40
    y0, y1 = min(ys) - 62, max(ys) + 96    # room for labels above and below
    return (round(x0), round(y0), round(x1 - x0), round(y1 - y0))


def map_svg(interactive=True):
    style = (f"<style>.lbl{{font:500 18.5px {FONT};fill:{INK}}}.hubname{{font-weight:700;font-size:20px;letter-spacing:1px}}"
             f".tag{{font:400 14.5px {FONT};fill:{SOFT}}}"
             f".lbl,.tag{{paint-order:stroke;stroke:{PAPER};stroke-width:5px;stroke-linejoin:round}}</style>")
    o = [style, f'<rect x="-200" y="-200" width="{W + 400}" height="{H + 400}" fill="{PAPER}"/>']
    o += [f'<rect x="{s["x"] - 76}" y="{s["y"] - 46}" width="152" height="150" rx="12" fill="{ZONE}"/>'
          for s in S.values() if s["side"] == "hub"]
    for lid, (name, color, stops) in L.items():
        pts = route(stops)
        o.append(f'<path id="L-{lid}" class="line" data-line="{lid}" d="{rounded(pts)}" fill="none" stroke="{color}" '
                 f'stroke-width="{LW}" stroke-linejoin="round"/>')
        o.append(f'<g class="cap" data-line="{lid}">{arrow(pts[-2], pts[-1], color)}</g>')
        o.append(line_badge(lid))
    o.append('<g id="trains"></g>')
    for sid, s in S.items():
        attrs = (f' class="stn" data-id="{sid}" tabindex="0" role="button" aria-label="{esc(s["name"])}: {esc(s["tag"])}"'
                 if interactive else "")
        o.append(f'<g{attrs}>{marker(s["x"], s["y"], s["side"] == "hub")}'
                 f'<circle cx="{s["x"]}" cy="{s["y"]}" r="26" fill="transparent"/>{label(sid)}</g>')
    return "\n".join(o)


# --------------------------------------------------------------------------
# the page: a framed map on a station wall, a departures board, a clock
# --------------------------------------------------------------------------
def data_json():
    ln = {lid: dict(name=n, color=c, stations=stops) for lid, (n, c, stops) in L.items()}
    st_ = {sid: dict(s, lines=lines_at(sid)) for sid, s in S.items()}
    # "</" would end the <script> block early
    return json.dumps(dict(stations=st_, lines=ln, view=view()), ensure_ascii=False).replace("</", "<\\/")


def clock_svg():
    ticks = "".join(f'<line x1="0" y1="-38" x2="0" y2="{-30 if i % 3 == 0 else -34}" stroke="#fff" '
                    f'stroke-width="{3 if i % 3 == 0 else 1.6}" transform="rotate({i * 30})"/>' for i in range(12))
    return (f'<svg class="sclock" viewBox="-50 -56 100 106" aria-hidden="true">'
            f'<rect x="-50" y="-56" width="100" height="106" rx="5" fill="#141414"/>'
            f'<text y="-45" text-anchor="middle" font-family="{FONT}" font-size="7.5" font-weight="700" fill="#fff" '
            f'letter-spacing="1.5">YAQZAN</text>'
            f'<circle r="42" fill="#0b0b0b" stroke="#262626" stroke-width="2"/>{ticks}'
            f'<line class="ch" y2="-21" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>'
            f'<line class="cm" y2="-32" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>'
            f'<line class="cs" y1="6" y2="-34" stroke="#dc241f" stroke-width="1.2"/>'
            f'<circle r="2.5" fill="#dc241f"/></svg>')


def board_html():
    return ('<div class="board" aria-live="polite"><div class="screen">'
            '<div class="led"><span class="led1">yaqzan\'s network</span></div>'
            '<div class="led row"><span class="led2">pick a stop</span><span class="led3"></span></div>'
            '</div></div>')


def roundel(size=44):
    return (f'<svg class="roundel" viewBox="-30 -30 60 60" width="{size}" height="{size}" aria-hidden="true">'
            f'<circle r="22" fill="none" stroke="#dc241f" stroke-width="9"/>'
            f'<rect x="-29" y="-6" width="58" height="12" fill="#0019a8"/></svg>')


def stamp(path):
    """Short content hash, so browsers fetch the new file after every deploy."""
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def page():
    legend = "".join(f'<button class="ldot" data-line="{lid}" style="--c:{c}"><i></i>{esc(n)}</button>'
                     for lid, (n, c, _) in L.items())
    m_tabs = "".join(f'<button class="m-tab" role="tab" data-line="{lid}" style="--c:{c}"><i></i><b>{esc(n)}</b>'
                     f'<span>{len(stops) - 1} stops</span></button>' for lid, (n, c, stops) in L.items())
    vx, vy, vw, vh = view()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>yaqzan's network map</title>
<meta name="description" content="my projects, papers and the rest, as a network map. pick a stop and a train takes you there.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Doto:wght@800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v={stamp('style.css')}">
</head>
<body>

<div class="d">
<div class="ceiling"><i></i><i></i></div>

<div class="wall">
  <aside class="side">
    <div class="hang">
      {clock_svg()}
      {board_html()}
    </div>

    <div class="plate">
      <b>yaqzan's</b>
      <span>projects, papers and the rest</span>
      <div class="bars">{"".join(f'<i style="background:{c}"></i>' for _, c, _ in L.values())}</div>
    </div>

    <div class="howto">
      <h2>how to read this map</h2>
      <p>every line starts at <b>aiub</b> and runs out to one part of what i do. each stop on a line is one thing: a project, a paper, an event.</p>
      <p>pick a stop and a train takes you there, with the details and the links.</p>
    </div>

    <nav class="exits" aria-label="links">
      <a href="https://github.com/yaqzans"><i>&uarr;</i>github</a>
      <a href="https://www.linkedin.com/in/shamvi-md-abdullah-b42a321a6/"><i>&uarr;</i>linkedin</a>
      <a href="https://scholar.google.com/citations?user=DwskOfEAAAAJ&hl=en"><i>&uarr;</i>google scholar</a>
      <a href="https://orcid.org/0009-0005-9717-9426"><i>&uarr;</i>orcid</a>
      <a href="mailto:shamvi.abdullah@gmail.com"><i>&uarr;</i>email</a>
      <a href="ShamviMdAbdullah.pdf"><i>&uarr;</i>cv</a>
    </nav>
  </aside>

  <main class="poster-wrap">
    <figure class="poster" style="--ar:{vw / vh:.3f}">
      <header class="poster-head">
        {roundel()}
        <div>
          <h1>yaqzan's network map</h1>
          <p>projects, papers and things i showed up for</p>
        </div>
      </header>
      <div id="scroller">
        <svg id="map" viewBox="{vx} {vy} {vw} {vh}" role="img" aria-label="a network map of yaqzan's projects, papers and activities">
{map_svg()}
        </svg>
      </div>
      <footer class="poster-foot">
        <div class="legend">{legend}</div>
        <span class="riders">pick any stop to ride there</span>
      </footer>
      <div class="glass"></div>
    </figure>
  </main>
</div>

<div class="platform"></div>

<aside class="card" id="card" hidden aria-live="polite">
  <button class="x" aria-label="close">&times;</button>
  <div class="card-lines"></div>
  <h2></h2>
  <p class="card-tag"></p>
  <p class="card-text"></p>
  <div class="card-links"></div>
</aside>
</div>

<!-- phone version: a line strip map, like the one above the doors in a train -->
<div class="m">
  <div class="m-ceiling"></div>
  <div class="m-hang">{clock_svg()}{board_html()}</div>
  <header class="m-plate">
    {roundel(34)}
    <div><b>yaqzan's</b><span>projects, papers and the rest</span></div>
  </header>
  <p class="m-intro">every line starts at <b>aiub</b>. pick a line, then tap a stop.</p>
  <nav class="m-tabs" role="tablist">{m_tabs}</nav>
  <section class="m-route" id="m-route" aria-live="polite"></section>
  <nav class="m-exits" aria-label="links">
    <a href="https://github.com/yaqzans"><i>&uarr;</i>github</a>
    <a href="https://www.linkedin.com/in/shamvi-md-abdullah-b42a321a6/"><i>&uarr;</i>linkedin</a>
    <a href="https://scholar.google.com/citations?user=DwskOfEAAAAJ&hl=en"><i>&uarr;</i>scholar</a>
    <a href="https://orcid.org/0009-0005-9717-9426"><i>&uarr;</i>orcid</a>
    <a href="mailto:shamvi.abdullah@gmail.com"><i>&uarr;</i>email</a>
    <a href="ShamviMdAbdullah.pdf"><i>&uarr;</i>cv</a>
  </nav>
  <div class="m-platform"></div>
</div>

<script id="data" type="application/json">{data_json()}</script>
<script src="app.js?v={stamp('app.js')}"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# teaser for the profile README: the same wall, poster and board, no js
# --------------------------------------------------------------------------
def teaser():
    """Profile README image: the board and name plate on the wall, the poster full width below."""
    vx, vy, vw, vh = view()
    TW = 1600
    px, py, pw = 40, 214, 1520
    mh = pw * vh / vw
    ph = 84 + mh + 50
    TH = round(py + ph + 70)
    trains = []
    for i, (lid, (_, color, stops)) in enumerate(L.items()):
        pts = route(stops)
        d = rounded(pts)
        length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        dur = max(5, length / 110)
        trains.append(f'<rect x="-15" y="-6.5" width="30" height="13" rx="2" fill="{color}" stroke="#fff" stroke-width="2">'
                      f'<animateMotion path="{d}" dur="{dur * 2:.1f}s" begin="-{i * 2.3:.1f}s" repeatCount="indefinite" '
                      f'rotate="auto" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear"/></rect>')
    body = map_svg(interactive=False).replace('<g id="trains"></g>', "".join(trains))
    body = body.replace(".lbl{font:500 18.5px", ".lbl{font:600 19.5px")
    led = "#ffb238"
    legend = "".join(f'<g transform="translate({28 + i * 200} {84 + mh + 31:.0f})"><rect width="30" height="7" y="-8" fill="{c}"/>'
                     f'<text x="40" y="0" font-family="{FONT}" font-size="18" fill="{INK}">{esc(n)}</text></g>'
                     for i, (n, c, _) in enumerate(L.values()))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}" width="{TW}" height="{TH}">
<defs>
  <pattern id="tiles" width="72" height="36" patternUnits="userSpaceOnUse">
    <rect width="72" height="36" fill="#e9e7e2"/><path d="M0 .5 H72 M.5 0 V36" stroke="#d2cec6" stroke-width="1.6"/>
  </pattern>
  <pattern id="unlit" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1.3" fill="#2a1a07"/></pattern>
  <pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="2.05" fill="#fff"/></pattern>
  <mask id="ledmask"><rect width="{TW}" height="{TH}" fill="url(#dots)"/></mask>
  <filter id="glow" x="-10%" y="-60%" width="120%" height="220%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="alu" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#dcdde0"/><stop offset=".5" stop-color="#9ea1a6"/><stop offset="1" stop-color="#d2d4d7"/></linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset=".22" stop-color="#fff" stop-opacity="0"/><stop offset=".3" stop-color="#fff" stop-opacity=".16"/><stop offset=".38" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <clipPath id="round"><rect width="{TW}" height="{TH}" rx="22"/></clipPath>
  <style>@keyframes b{{50%{{opacity:.1}}}}.blink{{animation:b 1.2s steps(1) infinite}}</style>
</defs>
<g clip-path="url(#round)">
  <rect width="{TW}" height="{TH}" fill="url(#tiles)"/>
  <rect width="{TW}" height="44" fill="#2a2c30"/>
  <rect x="160" y="32" width="520" height="5" rx="2" fill="#fbf8ee"/><rect x="920" y="32" width="520" height="5" rx="2" fill="#fbf8ee"/>
  <rect y="{TH - 30}" width="{TW}" height="30" fill="#77756f"/><rect y="{TH - 30}" width="{TW}" height="10" fill="#f2b705"/>

  <g transform="translate(40 70)">
    <rect width="420" height="118" fill="#fff" stroke="#cfcbc2" stroke-width="2"/>
    <text x="22" y="64" font-family="{FONT}" font-size="54" font-weight="700" fill="{INK}" letter-spacing="-1">yaqzan's</text>
    <text x="24" y="92" font-family="{FONT}" font-size="17" fill="{SOFT}">projects, papers and the rest</text>
    {"".join(f'<rect x="{22 + i * 96}" y="102" width="90" height="7" fill="{c}"/>' for i, (_, c, _) in enumerate(L.values()))}
  </g>
  <g font-family="{FONT}" font-size="19">
    <text x="500" y="108" fill="{INK}" font-weight="600">every line starts at aiub.</text>
    <text x="500" y="136" fill="{SOFT}">each stop is one project, paper or event.</text>
    <text x="500" y="164" fill="{SOFT}">click the map to ride it.</text>
  </g>
  <g transform="translate(1000 64)">
    <line x1="140" y1="-20" x2="140" y2="0" stroke="#555" stroke-width="4"/><line x1="420" y1="-20" x2="420" y2="0" stroke="#555" stroke-width="4"/>
    <rect width="560" height="126" rx="4" fill="#0b0b0b" stroke="#333" stroke-width="3"/>
    <rect x="8" y="8" width="544" height="110" fill="url(#unlit)"/>
    <g filter="url(#glow)"><g mask="url(#ledmask)" font-family="ui-monospace,Consolas,monospace" font-weight="800" fill="{led}">
      <text x="22" y="52" font-size="34">yaqzan's network</text>
      <text x="22" y="102" font-size="34">all lines</text>
      <text x="538" y="102" font-size="34" text-anchor="end" class="blink">now</text>
    </g></g>
  </g>

  <g transform="translate({px} {py})">
    <rect x="-14" y="-14" width="{pw + 28}" height="{ph + 28:.0f}" rx="4" fill="url(#alu)"/>
    <rect width="{pw}" height="{ph:.0f}" fill="#fff"/>
    <svg x="24" y="18" width="48" height="48" viewBox="-30 -30 60 60"><circle r="22" fill="none" stroke="#dc241f" stroke-width="9"/><rect x="-29" y="-6" width="58" height="12" fill="#0019a8"/></svg>
    <text x="86" y="45" font-family="{FONT}" font-size="31" font-weight="700" fill="{INK}" letter-spacing="-.5">yaqzan's network map</text>
    <text x="87" y="69" font-family="{FONT}" font-size="16" fill="{SOFT}">projects, papers and things i showed up for</text>
    <line x1="0" y1="84" x2="{pw}" y2="84" stroke="#d7d7db" stroke-width="2"/>
    <svg x="0" y="84" width="{pw}" height="{mh:.0f}" viewBox="{vx} {vy} {vw} {vh}">{body}</svg>
    <line x1="0" y1="{84 + mh:.0f}" x2="{pw}" y2="{84 + mh:.0f}" stroke="#d7d7db" stroke-width="2"/>
    {legend}
    <text x="{pw - 24}" y="{84 + mh + 31:.0f}" text-anchor="end" font-family="{FONT}" font-size="17" fill="{SOFT}">click to ride →</text>
    <rect width="{pw}" height="{ph:.0f}" fill="url(#glass)"/>
  </g>
</g>
</svg>'''


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    for lid, (_, _, stops) in L.items():
        for sid in stops:
            assert sid in S, f"{lid}: unknown station {sid}"
    for sid, s in S.items():
        for r in s["related"]:
            assert r in S, f"{sid}: unknown related {r}"
    write("index.html", page())
    prof = os.path.join("..", "yaqzans", "assets")
    if os.path.isdir(os.path.dirname(prof)):
        os.makedirs(prof, exist_ok=True)
        for old in ("metro-light.svg", "metro-dark.svg"):
            if os.path.exists(os.path.join(prof, old)):
                os.remove(os.path.join(prof, old))
        write(os.path.join(prof, "map.svg"), teaser())
    print(f"{len(S)} stations, {len(L)} lines")
