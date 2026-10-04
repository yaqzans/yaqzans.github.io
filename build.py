"""Build the metro map site and the profile README image.

The map is a timeline. Left to right is time, from the first day at AIUB in
summer 2023 to graduation in January 2027. Every line leaves the first-day
station together and peels off in the semester that thread began; each stop
sits in the semester it happened. Lines only meet where one thing led to
another.

Everything lives in this file. Edit it and run `python build.py`. It writes
index.html (the map is baked in as SVG, app.js animates it) and the README
image in ../yaqzans/assets/.
"""
import hashlib
import json
import math
import os

# --------------------------------------------------------------------------
# time: semesters left to right. width = how many stops one line needs there
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# lines are what things are built with (plus papers and things I showed up
# for). a project sits on every line it really uses, so an interchange means
# that project used both.
# --------------------------------------------------------------------------
def st(name, tag, x, y, side, text, links=(), related=()):
    return dict(name=name, tag=tag, x=x, y=y, side=side, text=text, links=list(links), related=list(related))


S = {
    # python
    "md": st("Markdown Converter", "Anything to Markdown", 160, 250, "t",
             "PDF, Word, PowerPoint or Excel in, clean Markdown out. A single Windows executable, nothing to install.",
             [("Repo", "https://github.com/yaqzans/markdown-converter-app")]),
    "oshud": st("OshudBot", "Bangla medicine bot", 300, 250, "b",
                "Covers 21,714 medicine brands and answers in Bangla, English or Banglish in about 15 ms on a CPU. "
                "It replaced 1.1 GB of models with transliteration and fuzzy matching at no loss in answer quality.",
                [("Repo", "https://github.com/yaqzans/oshudbot"), ("Try it", "https://oshudbot.streamlit.app/")],
                ["medease"]),
    "medease": st("MedEase BD", "Offline medicine LLM", 440, 250, "t",
                  "The heavier sibling of OshudBot. RAG over 21,000+ medicines plus a Gemma 3 4B fine-tuned on "
                  "36,000+ medicine Q&A pairs, running fully offline.", [], ["oshud"]),
    "vehicle": st("Vehicle Recognition", "YOLO + ConvNeXt", 760, 430, "b",
                  "Bangladeshi road vehicles on RSUD20K. YOLO26n finds them and ConvNeXt-Tiny classifies every crop. "
                  "Code, results and the paper.",
                  [("Repo", "https://github.com/yaqzans/cvpr-two-stage-vehicle-recognition")]),
    "hand": st("Robotic Hand", "Became the QPAIN paper", 900, 430, "tl",
               "A camera watches your hand and a 7-servo robotic hand copies it, with no gloves or sensors. Python "
               "and MediaPipe on the laptop, an ESP32 driving the servos. 88 ms end to end at 24.6 FPS, built for "
               "about 2,800 BDT. It became a paper: Gesture Controlled Robotic Hand Designed for Enhancing "
               "Industrial Automation and Innovation, IEEE QPAIN 2026, second and corresponding author.",
               [("Read the paper", "https://doi.org/10.1109/QPAIN69676.2026.11545528")]),
    "who": st("Who Should Count More", "Voting simulation", 1240, 430, "br",
              "Should educated votes count more? A Python simulation with a playable JavaScript front end: set up "
              "the electorate, run the election and see who wins.",
              [("Play", "https://yaqzans.github.io/who-should-count-more/"),
               ("Repo", "https://github.com/yaqzans/who-should-count-more")]),

    # c++
    "parking": st("2D Parking", "OpenGL game", 900, 170, "r",
                  "Park the car before the timer runs out. C++ with OpenGL and GLUT, for a computer graphics course.",
                  [("Repo", "https://github.com/yaqzans/2D-Parking-Game")]),
    "pm25": st("PM2.5 Monitor", "ESP32 + React Native", 1060, 590, "l",
               "Pocket air quality monitor: ESP32-C3 firmware plus a React Native app over BLE. It alerts only on "
               "genuine spikes, not on Dhaka's constantly high baseline. In a two-week field study it sent about 4 "
               "alerts a day instead of dozens, and each one was acted on."),

    # javascript
    "ttt": st("TicTacToe ∞", "4 pieces, then move them", 1400, 250, "t",
              "Tic-tac-toe where each player only gets 4 pieces and then has to move them. Vanilla JavaScript, "
              "with a bot that has a difficulty slider.",
              [("Play", "https://yaqzans.github.io/TicTacToeInfinity/"),
               ("Repo", "https://github.com/yaqzans/TicTacToeInfinity")]),
    "survey": st("Survey Platform", "NeedSurveyResponses", 920, 760, "br",
                 "NeedSurveyResponses: answer other people's surveys to earn credits, then spend credits to publish "
                 "your own. PHP, MySQL and JavaScript, with separate user and admin views."),

    # data
    "prod": st("Productivity Manager", "C# + MS SQL", 600, 760, "b",
               "Notes, reminders and a timer in one C# desktop app, with logins and an MS SQL database underneath.",
               [("Repo", "https://github.com/yaqzans/Productivity-Manager")]),
    "sarcasm": st("Sarcasm Detection", "R, Bag of Words vs TF-IDF", 1240, 760, "t",
                  "Can a classifier tell when a tweet is sarcastic? Bag of Words against TF-IDF across four "
                  "classifiers, in R.", [("Repo", "https://github.com/yaqzans/ids-sarcasm-detection")]),

    # papers
    "blood": st("Blood-Like Solution", "Analytical Chemistry Letters", 420, 620, "b",
                "Development of a Simulated Blood-Like Solution for Medical Experiments. Presented at the "
                "International Conference on Physics 2024 and published in Analytical Chemistry Letters (2025). "
                "Fifth author.", [("Read the paper", "https://doi.org/10.1080/22297928.2025.2533331")]),
    "agile": st("Agile + Waterfall", "IEOM Bangladesh 2025", 580, 620, "t",
                "Evaluating the Performance of Agile-Waterfall Integrated Approaches in Large Scale Engineering "
                "Projects in Bangladesh. IEOM Bangladesh 2025. Fifth author.",
                [("Read the paper", "https://doi.org/10.46254/BA08.20250467")]),
    "hybrid": st("Human-AI Animation", "ICCTASS 2025", 740, 620, "b",
                 "A Hybrid Human-AI Model for Sustainable Innovation in Media and Animation. Presented at ICCTASS "
                 "2025. Third author."),

    # out & about
    "poster": st("Poster Competition", "Selected participant", 40, 900, "t",
                 "Selected participant in the AIUB Poster Presentation Competition."),
    "english": st("English Club", "Organiser, 10+ events", 200, 900, "b",
                  "Organiser and content writer at the AIUB English Club. Ran 10+ events and workshops for 50+ members."),
    "embassy": st("U.S. Embassy", "AI workshop", 360, 900, "t",
                  "AI workshop at the American Center, Dhaka. Selected by the Faculty of Science and Technology to "
                  "represent the university."),
    "undp": st("UNDP Roundtable", "Youth and the SDGs", 520, 900, "b",
               "Selected to represent the university at \"Let's Talk with the UNDP Resident Representative\", a "
               "roundtable on youth engagement in the SDGs."),
}

# lines: id -> (name, color, route). a route is station ids and (x, y) waypoints; the arrow goes on the end
L = {
    "py":     ("Python", "#6b7d2a", ["md", "oshud", "medease", "vehicle", "hand", "who", (1560, 430)]),
    "js":     ("JavaScript", "#d6a21e", ["ttt", "who", "pm25", "survey", (920, 860)]),
    "cpp":    ("C++", "#7a3f22", ["parking", "hand", "pm25"]),
    "data":   ("Data", "#2f7f8f", ["prod", "survey", "sarcasm", (1560, 760)]),
    "papers": ("Papers", "#233a6b", ["blood", "agile", "hybrid", "hand", (1020, 310)]),
    "out":    ("Out & About", "#e8731c", ["poster", "english", "embassy", "undp", (600, 900)]),
}

W, H = 1800, 1000
BG, INK, SOFT, ZONE, NOWC = "#efe9dc", "#111111", "#6b5f4f", "#e7dfcd", "#e8731c"
FONT = "'Helvetica Neue',Helvetica,Arial,sans-serif"
LW = 14     # line width: thick and flat, like a 70s diagram
GAP = 2.5   # space between lines sharing track


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------
def is_stop(tok):
    return isinstance(tok, str) or (isinstance(tok, tuple) and isinstance(tok[0], str))


def sid_of(tok):
    return tok if isinstance(tok, str) else tok[0]


def pos(tok):
    if isinstance(tok, str):
        return (S[tok]["x"], S[tok]["y"])
    if isinstance(tok[0], str):
        return (S[tok[0]]["x"], S[tok[0]]["y"] + tok[1])
    return tok


def stations_of(lid):
    return [sid_of(t) for t in L[lid][2] if is_stop(t)]


def lines_at(sid):
    return [lid for lid in L if sid in stations_of(lid)]


def leg(a, b):
    """Octilinear path from a to b: diagonal first, then straight."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    d = min(abs(dx), abs(dy))
    sx, sy = (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)
    if d < .01 or abs(abs(dx) - abs(dy)) < .01:
        return [a, b]
    return [a, (x1 + sx * d, y1 + sy * d), b]


def shared():
    use = {}
    for lid, (_, _, r) in L.items():
        for a, b in zip(r, r[1:]):
            if isinstance(a, str) and isinstance(b, str):
                use.setdefault(tuple(sorted((a, b))), []).append(lid)
    return use


SHARED = shared()


def offset_poly(pts, o):
    if o == 0:
        return list(pts)
    segs = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = math.hypot(x2 - x1, y2 - y1)
        nx, ny = -(y2 - y1) / n, (x2 - x1) / n
        segs.append(((x1 + nx * o, y1 + ny * o), (x2 + nx * o, y2 + ny * o)))
    out = [segs[0][0]]
    for (p1, p2), (q1, q2) in zip(segs, segs[1:]):
        d1, d2 = (p2[0] - p1[0], p2[1] - p1[1]), (q2[0] - q1[0], q2[1] - q1[1])
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9:
            out.append(p2)
            continue
        t = ((q1[0] - p1[0]) * d2[1] - (q1[1] - p1[1]) * d2[0]) / den
        out.append((p1[0] + d1[0] * t, p1[1] + d1[1] * t))
    out.append(segs[-1][1])
    return out


def line_points(lid):
    r = L[lid][2]
    pts = []
    for a, b in zip(r, r[1:]):
        o = 0.0
        if isinstance(a, str) and isinstance(b, str):
            key = tuple(sorted((a, b)))
            group = SHARED[key]
            if len(group) > 1:
                o = (group.index(lid) - (len(group) - 1) / 2) * (LW + GAP)
                if (a, b) != key:
                    o = -o
        seg = offset_poly(leg(pos(a), pos(b)), o)
        if pts and math.dist(pts[-1], seg[0]) < .01:
            seg = seg[1:]
        pts += seg
    clean = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, clean[-1]) > .01:
            clean.append(p)
    return clean


def rounded(pts, r=30):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[i + 1]
        if abs((bx - ax) * (cy - by) - (by - ay) * (cx - bx)) < 1e-6:
            d += f" L{bx:.1f},{by:.1f}"
            continue
        l1, l2 = math.dist((ax, ay), (bx, by)), math.dist((bx, by), (cx, cy))
        k = min(r, l1 / 2, l2 / 2)
        p1 = (bx - (bx - ax) / l1 * k, by - (by - ay) / l1 * k)
        p2 = (bx + (cx - bx) / l2 * k, by + (cy - by) / l2 * k)
        d += f" L{p1[0]:.1f},{p1[1]:.1f} Q{bx:.1f},{by:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def where_lines_pass(sid):
    x, y = S[sid]["x"], S[sid]["y"]
    out = []
    for lid in lines_at(sid):
        for tok in L[lid][2]:
            if is_stop(tok) and sid_of(tok) == sid:
                out.append(pos(tok))
    return out


def marker_box(sid):
    x, y = S[sid]["x"], S[sid]["y"]
    if len(lines_at(sid)) == 1:
        return (x - 12, y - 12, x + 12, y + 12)
    ps = where_lines_pass(sid)
    xs, ys = [p[0] for p in ps], [p[1] for p in ps]
    return (min(xs) - 15, min(ys) - 15, max(xs) + 15, max(ys) + 15)


def marker(sid):
    x0, y0, x1, y1 = marker_box(sid)
    if len(lines_at(sid)) == 1:
        return f'<circle class="sh" cx="{S[sid]["x"]}" cy="{S[sid]["y"]}" r="11" fill="#fff" stroke="{INK}" stroke-width="4.5"/>'
    w, h = x1 - x0, y1 - y0
    return (f'<rect class="sh" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{min(w, h) / 2:.1f}" '
            f'fill="#fff" stroke="{INK}" stroke-width="5"/>')


def label(sid):
    s = S[sid]
    x, y, side = s["x"], s["y"], s["side"]
    x0, y0, x1, y1 = marker_box(sid)
    nx, ny, anchor = {"r": (x1 + 12, y + 2, "start"), "l": (x0 - 12, y + 2, "end"),
                      "t": (x, y0 - 42, "middle"), "b": (x, y1 + 33, "middle"),
                      "tl": (x0 - 10, y0 - 34, "end"), "br": (x1 + 10, y1 + 30, "start")}[side]
    return (f'<text x="{nx:.0f}" y="{ny:.0f}" text-anchor="{anchor}" class="lbl">{esc(s["name"])}</text>'
            f'<text x="{nx:.0f}" y="{ny + 26:.0f}" text-anchor="{anchor}" class="tag">{esc(s["tag"])}</text>')


def end_dir(lid):
    pts = line_points(lid)
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    n = math.dist((ax, ay), (bx, by))
    return (bx, by), ((bx - ax) / n, (by - ay) / n)


def arrow(lid):
    color = L[lid][1]
    (x2, y2), (ux, uy) = end_dir(lid)
    sx, sy = x2 + ux * 30, y2 + uy * 30
    tx, ty = sx + ux * 24, sy + uy * 24
    px, py = -uy * 16, ux * 16
    return (f'<path d="M{x2:.1f},{y2:.1f} L{sx:.1f},{sy:.1f}" stroke="{color}" stroke-width="{LW}" fill="none"/>'
            f'<path d="M{tx:.1f},{ty:.1f} L{sx + px:.1f},{sy + py:.1f} L{sx - px:.1f},{sy - py:.1f}Z" fill="{color}"/>')


def badge_box(lid):
    name, color, _ = L[lid]
    (bx, by), (ux, uy) = end_dir(lid)
    w = len(name) * 11.5 + 26
    tip = (bx + ux * 50, by + uy * 50)
    if abs(ux) > .9:
        cx, cy = tip[0] + ux * (24 + w / 2), tip[1]
    elif abs(uy) > .9:
        cx, cy = tip[0], tip[1] + uy * 24
    else:
        cx, cy = tip[0] + ux * (10 + w / 2), tip[1] + uy * 22
    return name, color, cx, cy, w


def line_badge(lid):
    name, color, cx, cy, w = badge_box(lid)
    dark = "#111" if lid == "js" else "#fff"
    return (f'<g class="badge" data-line="{lid}"><rect x="{cx - w / 2:.0f}" y="{cy - 16:.0f}" width="{w:.0f}" height="32" rx="2" fill="{color}"/>'
            f'<text x="{cx:.0f}" y="{cy + 6:.0f}" text-anchor="middle" fill="{dark}" font-family="{FONT}" font-size="17" '
            f'font-weight="700" letter-spacing=".6">{esc(name.upper())}</text></g>')


def view():
    xs = []
    ys = []
    for sid, v in S.items():
        x0, y0, x1, y1 = marker_box(sid)
        w = max(len(v["name"]) * 16, len(v["tag"]) * 10.5)
        if v["side"] in ("l", "tl"):
            xs.append(x0 - 8 - w)
        elif v["side"] in ("r", "br"):
            xs.append(x1 + 8 + w)
        else:
            xs += [v["x"] - w / 2, v["x"] + w / 2]
        ys += [y0 - 80, y1 + 80]
    for lid in L:
        _, _, cx, cy, w = badge_box(lid)
        xs += [cx - w / 2, cx + w / 2]
        ys += [cy - 14, cy + 14]
    y0 = min(ys) - 20
    return (round(min(xs) - 30), round(y0), round(max(xs) - min(xs) + 60), round(max(ys) - y0 + 30))


def zones():
    """No timeline any more: nothing behind the lines."""
    return ""


def map_svg(interactive=True):
    style = (f"<style>.lbl{{font:700 27px {FONT};fill:{INK}}}.tag{{font:500 19px {FONT};fill:{SOFT}}}"
             f".lbl,.tag{{paint-order:stroke;stroke:{BG};stroke-width:6px;stroke-linejoin:round}}"
             f".year{{font:800 62px {FONT};fill:#e2ded5;letter-spacing:2px}}"
             f".now{{font:700 18px {FONT};fill:{NOWC};letter-spacing:4px}}</style>")
    defs = ('<defs><pattern id="future" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="1.5" height="14" fill="{INK}" opacity=".07"/></pattern></defs>')
    o = [style, defs, f'<rect x="-600" y="-600" width="{W + 1600}" height="{H + 1600}" fill="{BG}"/>', zones()]
    for lid, (name, color, _) in L.items():
        o.append(f'<path id="L-{lid}" class="line" data-line="{lid}" d="{rounded(line_points(lid))}" fill="none" '
                 f'stroke="{color}" stroke-width="{LW}" stroke-linejoin="round"/>')
        o.append(f'<g class="cap" data-line="{lid}">{arrow(lid)}</g>')
    for lid in L:
        o.append(line_badge(lid))
    o.append('<g id="trains"></g>')
    for sid, s in S.items():
        attrs = (f' class="stn" data-id="{sid}" tabindex="0" role="button" aria-label="{esc(s["name"])}: {esc(s["tag"])}"'
                 if interactive else "")
        o.append(f'<g{attrs}>{marker(sid)}<circle cx="{s["x"]}" cy="{s["y"]}" r="28" fill="transparent"/>{label(sid)}</g>')
    return "\n".join(o)


# --------------------------------------------------------------------------
# the page: a station wall with a clock, a departures board, a name sign,
# an exit sign, and the map in a frame
# --------------------------------------------------------------------------
EXITS = [  # letter, arrow, label, url
    ("A", "←", "GitHub", "https://github.com/yaqzans"),
    ("B", "↖", "LinkedIn", "https://www.linkedin.com/in/shamvi-md-abdullah-b42a321a6/"),
    ("C", "↑", "Google Scholar", "https://scholar.google.com/citations?user=DwskOfEAAAAJ&hl=en"),
    ("D", "↗", "ORCID", "https://orcid.org/0009-0005-9717-9426"),
    ("E", "→", "Email", "mailto:shamvi.abdullah@gmail.com"),
    ("F", "↘", "CV", "ShamviMdAbdullah.pdf"),
]


def data_json():
    ln = {lid: dict(name=n, color=c, stations=stations_of(lid)) for lid, (n, c, _) in L.items()}
    st_ = {sid: dict(s, lines=lines_at(sid)) for sid, s in S.items()}
    # "</" would end the <script> block early
    return json.dumps(dict(stations=st_, lines=ln, view=view()), ensure_ascii=False).replace("</", "<\\/")


def stripes():
    return "".join(f'<i style="background:{c}"></i>' for _, c, _ in L.values())


def exits_html(cls):
    items = "".join(f'<a href="{esc(u)}"><span class="ex">{l}</span><span class="ar">{a}</span>{esc(t)}</a>'
                    for l, a, t, u in EXITS)
    return f'<nav class="{cls}" aria-label="Links">{items}</nav>'


def stamp(path):
    """Short content hash, so browsers fetch the new file after every deploy."""
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


KEY = ("Each line is a language or a kind of work. A stop sits on every line it uses, so where lines cross, "
       "that project used both.")


def page():
    legend = "".join(f'<button class="ldot" data-line="{lid}" style="--c:{c}"><i></i>{esc(n)}'
                     f'<span>{len(stations_of(lid))}</span></button>' for lid, (n, c, _) in L.items())
    m_tabs = "".join(f'<button class="m-tab" role="tab" data-line="{lid}" style="--c:{c}"><i></i><b>{esc(n)}</b>'
                     f'<span>{len(stations_of(lid))} stops</span></button>' for lid, (n, c, _) in L.items())
    vx, vy, vw, vh = view()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Yaqzan's</title>
<meta name="description" content="Projects, papers and the rest, drawn as a metro map. Pick a stop and a train takes you there.">
<link rel="stylesheet" href="style.css?v={stamp('style.css')}">
</head>
<body>

<div class="d">
  <aside class="column">
    <h1>Yaqzan’s</h1>
    <div class="stripes">{stripes()}</div>
    <p class="key">{KEY}</p>
    <nav class="legend" aria-label="Lines">{legend}</nav>
    {exits_html("exits")}
    <p class="hint">Click any stop to ride there.</p>
  </aside>

  <main class="mapside"><div class="mapframe">
    <svg id="map" viewBox="{vx} {vy} {vw} {vh}" preserveAspectRatio="xMidYMid meet" role="img"
         aria-label="Metro map of projects, papers and activities. Lines are languages and kinds of work.">
{map_svg()}
    </svg>
  </div></main>

  <aside class="card" id="card" hidden aria-live="polite">
    <button class="x" aria-label="Close">&times;</button>
    <div class="card-lines"></div>
    <h2></h2>
    <p class="card-tag"></p>
    <p class="card-text"></p>
    <div class="card-links"></div>
  </aside>
</div>

<!-- phone version: a line strip map, like the one above the doors in a train -->
<div class="m">
  <header class="m-head"><h1>Yaqzan’s</h1><div class="stripes">{stripes()}</div></header>
  <p class="m-intro">{KEY} Pick a line, then tap a stop.</p>
  <nav class="m-tabs" role="tablist">{m_tabs}</nav>
  <section class="m-route" id="m-route" aria-live="polite"></section>
  {exits_html("m-exits")}
</div>

<script id="data" type="application/json">{data_json()}</script>
<script src="app.js?v={stamp('app.js')}"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# profile README image: the black band with the name, the map below, trains running
# --------------------------------------------------------------------------
GRAIN_DEF = ('<filter id="grain" x="0" y="0" width="100%" height="100%">'
             '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4"/>'
             '<feColorMatrix values="0 0 0 0 .3  0 0 0 0 .25  0 0 0 0 .18  0 0 0 .45 -.12"/></filter>')


def teaser():
    vx, vy, vw, vh = view()
    TW = 1600
    band, stripe = 120, 14
    fb = 16                     # brown border round the edges of the map
    mw = TW - 2 * fb - 40
    mh = mw * vh / vw
    TH = round(band + stripe + 30 + mh + 30 + fb)
    trains = []
    for i, lid in enumerate(L):
        color = L[lid][1]
        pts = line_points(lid)
        length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        dur = max(4, length / 120)
        trains.append(f'<rect x="-20" y="-9" width="40" height="18" rx="3" fill="{color}" stroke="#fff" stroke-width="3">'
                      f'<animateMotion path="{rounded(pts)}" dur="{dur * 2:.1f}s" begin="-{i * 1.9:.1f}s" repeatCount="indefinite" '
                      f'rotate="auto" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear"/></rect>')
    body = map_svg(interactive=False).replace('<g id="trains"></g>', "".join(trains))
    sw = TW / len(L)
    bars = "".join(f'<rect x="{i * sw:.1f}" y="{band}" width="{sw + 1:.1f}" height="{stripe}" fill="{c}"/>'
                   for i, (_, c, _) in enumerate(L.values()))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}" width="{TW}" height="{TH}">
<defs>{GRAIN_DEF}<clipPath id="r"><rect width="{TW}" height="{TH}" rx="10"/></clipPath></defs>
<g clip-path="url(#r)">
  <rect width="{TW}" height="{TH}" fill="{BG}"/>
  <rect width="{TW}" height="{band}" fill="#111"/>
  <text x="44" y="84" font-family="{FONT}" font-size="64" font-weight="800" fill="#fff" letter-spacing="-2">Yaqzan’s</text>
  <text x="{TW - 44}" y="72" text-anchor="end" font-family="{FONT}" font-size="22" font-weight="700" fill="#e8731c">Projects, papers and the rest</text>
  <text x="{TW - 44}" y="98" text-anchor="end" font-family="{FONT}" font-size="17" fill="#bdb3a2">Lines are languages. Where they cross, a project used both.</text>
  {bars}
  <svg x="{fb + 20}" y="{band + stripe + 30}" width="{mw:.0f}" height="{mh:.0f}" viewBox="{vx} {vy} {vw} {vh}">{body}</svg>
  <path d="M{fb / 2},{band + stripe} V{TH - fb / 2} H{TW - fb / 2} V{band + stripe}" fill="none" stroke="#3d2617" stroke-width="{fb}"/>
  <rect width="{TW}" height="{TH}" filter="url(#grain)" opacity=".5" pointer-events="none"/>
</g>
</svg>'''


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    for lid, (_, _, r) in L.items():
        for tok in r:
            assert not is_stop(tok) or sid_of(tok) in S, f"{lid}: unknown station {tok}"
    for sid, s in S.items():
        for rel in s["related"]:
            assert rel in S, f"{sid}: unknown related {rel}"
    write("index.html", page())
    prof = os.path.join("..", "yaqzans", "assets")
    if os.path.isdir(os.path.dirname(prof)):
        os.makedirs(prof, exist_ok=True)
        # github caches readme images by url, so the file gets a new name whenever it changes
        svg = teaser()
        name = f"map-{hashlib.sha1(svg.encode()).hexdigest()[:8]}.svg"
        for old in os.listdir(prof):
            if old.startswith(("map", "metro", "room")) and old.endswith(".svg") and old != name:
                os.remove(os.path.join(prof, old))
        write(os.path.join(prof, name), svg)
        write(os.path.join(prof, "..", "README.md"),
              f'<a href="https://yaqzans.github.io"><img src="assets/{name}" width="100%" '
              'alt="Yaqzan&#39;s Metro: projects, papers and everything since 2023 as a metro map, time running left '
              'to right. Click to ride."></a>\n')
    print(f"{len(S)} stations, {len(L)} lines")
