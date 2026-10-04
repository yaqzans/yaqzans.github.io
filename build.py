"""Build yaqzan's metro.

Everything on the map lives in this file: stations, lines, what each card says.
Edit it and run `python build.py`. It writes index.html (the map is baked in
as SVG, app.js only animates it) and the animated teaser for the profile
README in ../yaqzans/.
"""
import json
import math
import os

W, H = 1600, 900

# --------------------------------------------------------------------------
# stations: id -> (name, shape, x, y, label side, card text, links, related)
# shapes: circle = project, square = paper, triangle = out & about,
#         pentagon = school, diamond = interest, star = aiub
# --------------------------------------------------------------------------
S = {
    # projects
    "medease": ("medease bd", "circle", 680, 120, "t",
                "medicine assistant that understands english, bangla and banglish. rag over 21,000+ medicines, "
                "and a gemma 3 4b fine-tuned on 36,000+ medicine q&a pairs. runs fully offline.", [], []),
    "oshud": ("oshudbot", "circle", 880, 170, "b",
              "the light one. 21,714 brands, answers in about 15 ms on a cpu. it used to carry 1.1 gb of models, "
              "swapped them for transliteration and fuzzy matching and lost nothing.",
              [("repo", "https://github.com/yaqzans/oshudbot"), ("try it", "https://oshudbot.streamlit.app/")], []),
    "hand": ("robotic hand", "cross", 480, 170, "b",
             "a camera watches your hand and a 7-servo robotic hand copies it. no gloves, no sensors. "
             "88 ms end to end at 24.6 fps, built for about 2,800 taka. it turned into a paper too: "
             "ieee qpain 2026, second and corresponding author.",
             [("read the paper", "https://doi.org/10.1109/QPAIN69676.2026.11545528")], []),
    "pm25": ("pm2.5 monitor", "circle", 300, 170, "t",
             "pocket air quality monitor plus a react native app. it only alerts on real spikes, not on dhaka's "
             "normal bad air. two weeks of field testing: about 4 alerts a day instead of dozens, and people "
             "actually read them.", [], []),
    "survey": ("needsurveyresponses", "circle", 140, 260, "b",
               "answer other people's surveys to earn credits, spend credits to post your own. php, mysql, "
               "separate user and admin sides.", [], []),

    # papers
    "blood": ("blood-like solution", "square", 640, 330, "r",
              "Development of a Simulated Blood-Like Solution for Medical Experiments. analytical chemistry "
              "letters, 2025. first shown at the international conference on physics 2024. fifth author.",
              [("read the paper", "https://doi.org/10.1080/22297928.2025.2533331")], []),
    "agile": ("agile + waterfall", "square", 300, 350, "r",
              "Evaluating the Performance of Agile-Waterfall Integrated Approaches in Large Scale Engineering "
              "Projects in Bangladesh. ieom bangladesh 2025. fifth author.",
              [("read the paper", "https://doi.org/10.46254/BA08.20250467")], []),
    "hybrid": ("human-ai animation", "square", 140, 430, "b",
               "A Hybrid Human-AI Model for Sustainable Innovation in Media and Animation. presented at icctass "
               "2025. third author.", [], []),

    # out & about
    "english": ("english club", "triangle", 800, 830, "r",
                "organiser and content writer at the aiub english club. 10+ events and workshops, 50+ members.",
                [], []),
    "undp": ("undp roundtable", "triangle", 920, 360, "r",
             "picked to represent aiub at let's talk with the undp resident representative, a roundtable on "
             "youth and the sdgs.", [], []),
    "embassy": ("u.s. embassy ai workshop", "triangle", 1060, 280, "t",
                "ai workshop at the american center, dhaka. the faculty of science and technology sent me to "
                "represent aiub.", [], []),
    "poster": ("poster competition", "triangle", 1280, 280, "t",
               "selected participant in the aiub poster presentation competition.", [], []),

    # school
    "aiub": ("aiub", "star", 800, 480, "t",
             "american international university-bangladesh. bsc in computer science and engineering, major in "
             "computational theory, minor in data science. cgpa 3.96.", [], []),
    "scholars": ("scholar's school & college", "pentagon", 520, 480, "b",
                 "ssc and hsc, science group. gpa 5.00 in both.", [], []),
    "deans": ("dean's list", "pentagon", 1060, 480, "b",
              "dean's list in spring 2023-24 and fall 2024-25, on an ongoing academic scholarship.", [], []),
    "grad": ("jan 2027", "pentagon", 1240, 420, "t",
             "end of the line. graduating in january 2027.", [], []),

    # coursework
    "wtp": ("wt project", "circle", 120, 780, "b",
            "web tech course project, php.", [("repo", "https://github.com/yaqzans/WT_Fall-25-26_Project")], []),
    "wt": ("wt fall 25", "circle", 280, 780, "b",
           "web tech coursework.", [("repo", "https://github.com/yaqzans/WT_Fall-25-26")], []),
    "pink": ("pink calculator", "circle", 420, 660, "l",
             "a class task to learn c# guis. it's a calculator. it's pink. it also talks to a database, "
             "for practice.", [("repo", "https://github.com/yaqzans/Pink-Calculator")], []),
    "prod": ("productivity manager", "circle", 580, 600, "b",
             "notes, reminders and a timer in one c# app, with logins and ms sql underneath. oop 2.",
             [("repo", "https://github.com/yaqzans/Productivity-Manager")], []),
    "bus": ("bus management", "circle", 980, 640, "r",
            "java oop final, built in 28 hours.", [("repo", "https://github.com/yaqzans/Bus-Management-System")], []),
    "sarc": ("sarcasm detection", "circle", 1100, 760, "b",
             "can a classifier tell when a tweet is being sarcastic? bag of words vs tf-idf across four "
             "classifiers, in r.", [("repo", "https://github.com/yaqzans/ids-sarcasm-detection")], []),
    "parking": ("2d parking", "circle", 1260, 760, "b",
                "park the car before the timer runs out. opengl and glut, computer graphics course.",
                [("repo", "https://github.com/yaqzans/2D-Parking-Game")], []),
    "vehicle": ("vehicle recognition", "circle", 1360, 660, "l",
                "bangladeshi road vehicles on rsud20k. yolo26n finds them, convnext-tiny names every crop. "
                "code, results and the paper.",
                [("repo", "https://github.com/yaqzans/cvpr-two-stage-vehicle-recognition")], []),

    # side quests
    "md": ("markdown converter", "circle", 1060, 120, "t",
           "pdf, word, powerpoint or excel in, clean markdown out. one windows exe, nothing to install.",
           [("repo", "https://github.com/yaqzans/markdown-converter-app")], []),
    "who": ("who should count more", "circle", 1260, 170, "b",
            "should educated votes count more? set it up, run the election, see who wins.",
            [("repo", "https://github.com/yaqzans/who-should-count-more"),
             ("play", "https://yaqzans.github.io/who-should-count-more/")], []),
    "ttt": ("tictactoe ∞", "circle", 1460, 110, "b",
            "tic-tac-toe where you only get 4 pieces, then you have to move them. has a bot with a "
            "difficulty slider.",
            [("repo", "https://github.com/yaqzans/TicTacToeInfinity"),
             ("play", "https://yaqzans.github.io/TicTacToeInfinity/")], []),

    # interests
    "graph": ("graph theory", "diamond", 1480, 300, "l",
              "my major is computational theory, so this is home turf.", [], ["aiub"]),
    "ml": ("machine learning", "diamond", 1480, 420, "l",
           "most of what's on this map, honestly.", [], ["medease", "oshud", "vehicle", "sarc"]),
    "medimg": ("medical imaging", "diamond", 1480, 540, "l",
               "where most of my current work is. not public yet.", [], []),
    "cv": ("computer vision", "diamond", 1500, 660, "b",
           "cameras that understand things.", [], ["vehicle", "hand"]),
    "nlp": ("bangla nlp", "diamond", 1480, 840, "l",
            "getting computers to deal with bangla, english and banglish all mixed together.",
            [], ["oshud", "medease"]),
}

# lines: id -> (name, color, stations). "|sd" on a stop = go straight first, then diagonal.
L = {
    "red":    ("projects", "#e03a2f", ["survey", "pm25", "hand", "medease", "oshud"]),
    "blue":   ("papers", "#1f3f96", ["hybrid", "agile", "hand", "blood|sd"]),
    "yellow": ("out & about", "#f4c21b", ["english", "aiub", "undp", "embassy", "poster"]),
    "green":  ("school", "#14913f", ["scholars", "aiub", "deans", "grad"]),
    "pink":   ("coursework", "#ec8aa0", ["wtp", "wt", "pink", "prod", "aiub|sd", "bus", "sarc", "parking", "vehicle"]),
    "cyan":   ("side quests", "#1ea2d8", ["oshud", "md", "who", "ttt"]),
    "brown":  ("interests", "#9a5b35", ["graph", "ml", "medimg", "cv", "nlp|sd"]),
}

# the map is laid out by hand in a 1600x900 space, then shrunk to leave room for the buttons
FIT = (0.935, 150 - 120 * 0.935, 150 - 110 * 0.935)
for _k, _v in list(S.items()):
    S[_k] = _v[:2] + (round(FIT[1] + _v[2] * FIT[0]), round(FIT[2] + _v[3] * FIT[0])) + _v[4:]

RIVER = "M-20,560 C120,560 180,600 260,640 S380,720 470,720 S620,640 700,700 S760,900 900,920"

THEMES = {
    "light": dict(bg="#f6f3ec", ink="#2f2f2f", station="#ffffff", river="#bfe3f5", label="#3a3a3a"),
    "dark":  dict(bg="#26282c", ink="#e9e9e9", station="#26282c", river="#2f4a5c", label="#d8d8d8"),
}


# --------------------------------------------------------------------------
# geometry: octilinear routes with rounded corners, like the game
# --------------------------------------------------------------------------
def stop(token):
    sid, _, bend = token.partition("|")
    return sid, bend or "ds"


def leg(a, b, bend):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    d = min(abs(dx), abs(dy))
    sx, sy = (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)
    if d == 0 or abs(dx) == abs(dy):
        return [b]
    if bend == "ds":
        return [(x1 + sx * d, y1 + sy * d), b]
    return [(x2 - sx * d, y2 - sy * d), b]


def route(line):
    pts = []
    for i, tok in enumerate(line):
        sid, bend = stop(tok)
        p = (S[sid][2], S[sid][3])
        pts += [p] if i == 0 else leg(pts[-1], p, bend)
    out = [pts[0]]  # drop collinear points
    for p in pts[1:]:
        if len(out) >= 2:
            (ax, ay), (bx, by) = out[-2], out[-1]
            if (bx - ax) * (p[1] - by) == (by - ay) * (p[0] - bx):
                out[-1] = p
                continue
        if p != out[-1]:
            out.append(p)
    return out


def rounded(pts, r=26):
    d = f"M{pts[0][0]},{pts[0][1]}"
    for i in range(1, len(pts) - 1):
        (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[i + 1]
        l1, l2 = math.dist((ax, ay), (bx, by)), math.dist((bx, by), (cx, cy))
        k = min(r, l1 / 2, l2 / 2)
        p1 = (bx - (bx - ax) / l1 * k, by - (by - ay) / l1 * k)
        p2 = (bx + (cx - bx) / l2 * k, by + (cy - by) / l2 * k)
        d += f" L{p1[0]:.1f},{p1[1]:.1f} Q{bx},{by} {p2[0]:.1f},{p2[1]:.1f}"
    d += f" L{pts[-1][0]},{pts[-1][1]}"
    return d


def cap(a, b, color):
    """The little T at the end of a line."""
    (x1, y1), (x2, y2) = a, b
    ux, uy = (x2 - x1), (y2 - y1)
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    ex, ey = x2 + ux * 22, y2 + uy * 22
    px, py = -uy * 13, ux * 13
    return (f'<path d="M{x2},{y2} L{ex:.1f},{ey:.1f} M{ex - px:.1f},{ey - py:.1f} L{ex + px:.1f},{ey + py:.1f}" '
            f'stroke="{color}" stroke-width="10" stroke-linecap="round" fill="none"/>')


def shape(kind, x, y, s=15, sw=4.5, fill="#fff", ink="#2f2f2f"):
    a = f'class="sh" fill="{fill}" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"'
    if kind == "circle":
        return f'<circle cx="{x}" cy="{y}" r="{s}" {a}/>'
    if kind == "square":
        return f'<rect x="{x - s * .9:.1f}" y="{y - s * .9:.1f}" width="{s * 1.8:.1f}" height="{s * 1.8:.1f}" {a}/>'
    if kind == "triangle":
        return f'<path d="M{x},{y - s * 1.15:.1f} L{x + s * 1.1:.1f},{y + s * .8:.1f} L{x - s * 1.1:.1f},{y + s * .8:.1f}Z" {a}/>'
    if kind == "diamond":
        return f'<path d="M{x},{y - s * 1.2:.1f} L{x + s * 1.2:.1f},{y} L{x},{y + s * 1.2:.1f} L{x - s * 1.2:.1f},{y}Z" {a}/>'
    if kind == "pentagon":
        p = " ".join(f"{x + s * 1.15 * math.sin(2 * math.pi * i / 5):.1f},{y - s * 1.15 * math.cos(2 * math.pi * i / 5):.1f}" for i in range(5))
        return f'<polygon points="{p}" {a}/>'
    if kind == "cross":
        w = s * .5
        return (f'<path d="M{x - w},{y - s} h{2 * w} v{s - w} h{s - w} v{2 * w} h{-(s - w)} v{s - w} h{-2 * w} '
                f'v{-(s - w)} h{-(s - w)} v{-2 * w} h{s - w}Z" {a}/>')
    if kind == "star":
        p = " ".join(f"{x + (s * 1.45 if i % 2 == 0 else s * .62) * math.sin(math.pi * i / 5):.1f},"
                     f"{y - (s * 1.45 if i % 2 == 0 else s * .62) * math.cos(math.pi * i / 5):.1f}" for i in range(10))
        return f'<polygon points="{p}" {a}/>'
    raise ValueError(kind)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def lines_at(sid):
    return [lid for lid, (_, _, st) in L.items() if sid in [stop(t)[0] for t in st]]


def label(sid, t):
    name, _, x, y, side = S[sid][:5]
    off = 30 if sid == "aiub" else 26
    pos = {"r": (x + off, y + 6, "start"), "l": (x - off, y + 6, "end"),
           "t": (x, y - off - 2, "middle"), "b": (x, y + off + 14, "middle")}[side]
    return (f'<text x="{pos[0]}" y="{pos[1]}" text-anchor="{pos[2]}" class="lbl" fill="{t["label"]}" '
            f'paint-order="stroke" stroke="{t["bg"]}" stroke-width="6" stroke-linejoin="round">{esc(name)}</text>')


def map_svg(t, interactive=True):
    o = [f'<rect class="bg" width="{W}" height="{H}" fill="{t["bg"]}"/>',
         f'<path class="river" transform="translate({FIT[1]:.1f} {FIT[2]:.1f}) scale({FIT[0]})" d="{RIVER}" fill="none" stroke="{t["river"]}" stroke-width="62" stroke-linejoin="round" stroke-linecap="round"/>']
    for lid, (name, color, st) in L.items():
        pts = route(st)
        o.append(f'<path id="L-{lid}" class="line" data-line="{lid}" d="{rounded(pts)}" fill="none" stroke="{color}" '
                 f'stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<g class="cap" data-line="{lid}">{cap(pts[1], pts[0], color)}{cap(pts[-2], pts[-1], color)}</g>')
    o.append('<g id="trains"></g>')
    for sid, (name, kind, x, y, *_rest) in S.items():
        inter = len(lines_at(sid)) > 1
        attrs = (f' class="stn" data-id="{sid}" tabindex="0" role="button" aria-label="{esc(name)}"' if interactive else "")
        ring = f'<circle class="sh" cx="{x}" cy="{y}" r="27" fill="{t["station"]}" stroke="{t["ink"]}" stroke-width="5"/>' if inter else ""
        o.append(f'<g{attrs}>{ring}{shape(kind, x, y, 15, 4.5, t["station"], t["ink"])}'
                 f'<circle cx="{x}" cy="{y}" r="34" fill="transparent"/>{label(sid, t)}</g>')
    o.append('<g id="pax"></g>')
    return "\n".join(o)


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------
def data_json():
    st = {sid: dict(name=v[0], shape=v[1], x=v[2], y=v[3], side=v[4], text=v[5], links=v[6], related=v[7], lines=lines_at(sid))
          for sid, v in S.items()}
    ln = {lid: dict(name=v[0], color=v[1], stations=[stop(s)[0] for s in v[2]]) for lid, v in L.items()}
    # "</" would end the <script> block early
    return json.dumps(dict(stations=st, lines=ln), ensure_ascii=False).replace("</", "<\\/")


def shapes_defs():
    """Small shape icons for passengers and cards, as <symbol>s."""
    kinds = ["circle", "square", "triangle", "pentagon", "diamond", "cross", "star"]
    return "".join(f'<symbol id="sh-{k}" viewBox="-20 -20 40 40">{shape(k, 0, 0, 13, 0, "currentColor", "currentColor")}</symbol>'
                   for k in kinds)


def page():
    t = THEMES["light"]
    line_btns = "".join(f'<button class="ldot" data-line="{lid}" style="--c:{c}" aria-label="{n} line">'
                        f'<span>{n}</span></button>' for lid, (n, c, _) in L.items())
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>yaqzan's metro</title>
<meta name="description" content="click a station, a train will take you there">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{shapes_defs()}</defs></svg>

<header class="city">
  <h1>dhaka</h1>
  <p>yaqzan's metro</p>
</header>

<div id="scroller">
  <svg id="map" viewBox="0 0 {W} {H}" role="img" aria-label="a metro map where every station is something yaqzan made or did">
{map_svg(t)}
  </svg>
</div>

<div class="hud">
  <div class="day"><b id="dayname">SAT</b><span id="count">0</span></div>
  <svg class="clock" viewBox="-30 -30 60 60" aria-hidden="true">
    <circle r="27" class="face"/>
    <g class="ticks"></g>
    <line id="hand" x1="0" y1="0" x2="0" y2="-19"/>
    <circle r="2.5" fill="#fff"/>
  </svg>
</div>

<nav class="speed" aria-label="speed">
  <button data-speed="0" aria-label="pause"><svg viewBox="0 0 24 24"><rect x="5" y="4" width="5" height="16"/><rect x="14" y="4" width="5" height="16"/></svg></button>
  <button data-speed="1" class="on" aria-label="play"><svg viewBox="0 0 24 24"><path d="M6 4 L20 12 L6 20Z"/></svg></button>
  <button data-speed="3" aria-label="fast forward"><svg viewBox="0 0 24 24"><path d="M2 5 L12 12 L2 19Z M12 5 L22 12 L12 19Z"/></svg></button>
</nav>

<nav class="linelist" aria-label="lines">{line_btns}</nav>

<nav class="tools" aria-label="links">
  <a href="https://github.com/yaqzans" title="github"><span>gh</span><i>github</i></a>
  <a href="https://www.linkedin.com/in/shamvi-md-abdullah-b42a321a6/" title="linkedin"><span>in</span><i>linkedin</i></a>
  <a href="https://scholar.google.com/citations?user=DwskOfEAAAAJ&hl=en" title="google scholar"><span>gs</span><i>google scholar</i></a>
  <a href="https://orcid.org/0009-0005-9717-9426" title="orcid"><span>iD</span><i>orcid</i></a>
  <a href="mailto:shamvi.abdullah@gmail.com" title="email"><span>@</span><i>email</i></a>
  <a href="ShamviMdAbdullah.pdf" title="cv"><span>cv</span><i>cv</i></a>
</nav>

<p class="hint" id="hint">click any station</p>

<aside class="card" id="card" hidden aria-live="polite">
  <button class="x" aria-label="close">&times;</button>
  <div class="card-head"><svg class="card-shape"><use href=""/></svg><h2></h2></div>
  <div class="card-lines"></div>
  <p class="card-text"></p>
  <div class="card-links"></div>
</aside>

<script id="data" type="application/json">{data_json()}</script>
<script src="app.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# teaser for the profile README: same map, trains on loops, no js
# --------------------------------------------------------------------------
def teaser(theme):
    t = THEMES[theme]
    body = map_svg(t, interactive=False)
    trains = []
    for i, (lid, (_, color, st)) in enumerate(L.items()):
        d = rounded(route(st))
        length = sum(math.dist(a, b) for a, b in zip(route(st), route(st)[1:]))
        dur = max(6, length / 90)
        trains.append(f'<rect x="-17" y="-9" width="34" height="18" rx="3" fill="{color}" stroke="{t["bg"]}" stroke-width="2">'
                      f'<animateMotion path="{d}" dur="{dur * 2:.1f}s" begin="-{i * 1.7:.1f}s" repeatCount="indefinite" '
                      f'rotate="auto" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear"/></rect>')
    title = (f'<text x="40" y="70" font-family="Jost,Futura,\'Century Gothic\',sans-serif" font-size="44" '
             f'font-weight="600" fill="{t["ink"]}">dhaka</text>'
             f'<text x="42" y="100" font-family="Jost,Futura,\'Century Gothic\',sans-serif" font-size="20" '
             f'fill="{t["label"]}">yaqzan\'s metro</text>'
             f'<text x="{W - 40}" y="70" text-anchor="end" font-family="Jost,Futura,\'Century Gothic\',sans-serif" '
             f'font-size="22" fill="{t["label"]}">click to ride →</text>')
    style = "<style>.lbl{font:500 17px Jost,Futura,'Century Gothic',sans-serif}</style>"
    body = body.replace('<g id="trains"></g>', "".join(trains))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{style}'
            f'<clipPath id="c"><rect width="{W}" height="{H}" rx="28"/></clipPath><g clip-path="url(#c)">'
            f'{body}{title}</g></svg>')


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    for lid, (_, _, st) in L.items():
        for tok in st:
            assert stop(tok)[0] in S, f"{lid}: unknown station {tok}"
    write("index.html", page())
    prof = os.path.join("..", "yaqzans")
    if os.path.isdir(prof):
        os.makedirs(os.path.join(prof, "assets"), exist_ok=True)
        for th in THEMES:
            write(os.path.join(prof, "assets", f"metro-{th}.svg"), teaser(th))
    print(f"{len(S)} stations, {len(L)} lines")
