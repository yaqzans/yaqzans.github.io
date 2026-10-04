"""Build yaqzan's network map.

Everything on the map lives in this file: stations, lines, what each card says.
Edit it and run `python build.py`. It writes index.html (the map is baked in
as SVG, app.js only animates it) and the teaser for the profile README in
../yaqzans/assets/map.svg.

Lines are lists of stations and (x, y) waypoints, so a line can wander like a
real one. Where two lines run between the same two stations they share track
and are drawn side by side; stations served by more than one line get an
interchange marker.
"""
import hashlib
import json
import math
import os


# --------------------------------------------------------------------------
# stations. tag = the line printed under the name on the map.
# side = where the name goes: r, l, t, b
# --------------------------------------------------------------------------
def st(name, tag, x, y, side, text, links=(), related=()):
    return dict(name=name, tag=tag, x=x, y=y, side=side, text=text, links=list(links), related=list(related))


S = {
    "aiub": st("AIUB", "bsc cse, class of 2027", 900, 500, "tl",
               "american international university-bangladesh. bsc in computer science and engineering, major in "
               "computational theory, minor in data science. cgpa 3.96, dean's list twice, on an academic "
               "scholarship. most lines on this map pass through here."),

    # machine learning, shared with language from aiub to medease
    "vehicle": st("vehicle recognition", "yolo + convnext", 340, 500, "t",
                  "bangladeshi road vehicles on rsud20k. yolo26n finds them, convnext-tiny names every crop. code, "
                  "results and the paper.",
                  [("repo", "https://github.com/yaqzans/cvpr-two-stage-vehicle-recognition")]),
    "sarcasm": st("sarcasm detection", "bag of words vs tf-idf", 1080, 500, "t",
                  "can a classifier tell when a tweet is being sarcastic? bag of words vs tf-idf across four "
                  "classifiers, in r.", [("repo", "https://github.com/yaqzans/ids-sarcasm-detection")]),
    "oshud": st("oshudbot", "bangla medicine bot", 1260, 500, "b",
                "21,714 medicine brands, ask in bangla, english or banglish. answers in about 15 ms on a cpu. it "
                "used to carry 1.1 gb of models, swapped them for transliteration and fuzzy matching and lost "
                "nothing.",
                [("repo", "https://github.com/yaqzans/oshudbot"), ("try it", "https://oshudbot.streamlit.app/")]),
    "medease": st("medease bd", "offline medicine llm", 1480, 500, "b",
                  "the heavier sibling of oshudbot. rag over 21,000+ medicines plus a gemma 3 4b fine-tuned on "
                  "36,000+ medicine q&a pairs, running fully offline.", [], ["oshud"]),

    # hardware, crossing the network north to south-east
    "hand": st("robotic hand", "esp32 + mediapipe, ieee qpain 2026", 680, 300, "b",
               "a camera watches your hand and a 7-servo robotic hand copies it. no gloves, no sensors. 88 ms end "
               "to end at 24.6 fps, built for about 2,800 taka. it became a paper: Gesture Controlled Robotic Hand "
               "Designed for Enhancing Industrial Automation and Innovation, ieee qpain 2026, second and "
               "corresponding author.",
               [("read the paper", "https://doi.org/10.1109/QPAIN69676.2026.11545528")]),
    "pm25": st("pm2.5 monitor", "air quality alerts, esp32", 1060, 300, "t",
               "pocket air quality monitor plus a react native app. it only alerts on real spikes, not on dhaka's "
               "normal bad air. two weeks of field testing: about 4 alerts a day instead of dozens, and people "
               "actually read them."),

    # papers
    "blood": st("blood-like solution", "analytical chemistry letters 2025", 540, 160, "t",
                "Development of a Simulated Blood-Like Solution for Medical Experiments. analytical chemistry "
                "letters, 2025. first shown at the international conference on physics 2024. fifth author.",
                [("read the paper", "https://doi.org/10.1080/22297928.2025.2533331")]),
    "agile": st("agile + waterfall", "ieom bangladesh 2025", 340, 160, "l",
                "Evaluating the Performance of Agile-Waterfall Integrated Approaches in Large Scale Engineering "
                "Projects in Bangladesh. ieom bangladesh 2025. fifth author.",
                [("read the paper", "https://doi.org/10.46254/BA08.20250467")]),
    "hybrid": st("human-ai animation", "icctass 2025", 200, 300, "l",
                 "A Hybrid Human-AI Model for Sustainable Innovation in Media and Animation. presented at icctass "
                 "2025. third author."),

    # out & about
    "english": st("english club", "organiser, 10+ events", 620, 800, "b",
                  "organiser and content writer at the aiub english club. 10+ events and workshops, 50+ members."),
    "undp": st("undp roundtable", "youth and the sdgs", 900, 800, "b",
               "picked to represent aiub at let's talk with the undp resident representative, a roundtable on "
               "youth and the sdgs."),
    "embassy": st("u.s. embassy", "ai workshop", 900, 160, "r",
                  "ai workshop at the american center, dhaka. the faculty of science and technology sent me to "
                  "represent aiub."),

    # side projects
    "md": st("markdown converter", "anything to markdown", 1080, 680, "b",
             "pdf, word, powerpoint or excel in, clean markdown out. one windows exe, nothing to install.",
             [("repo", "https://github.com/yaqzans/markdown-converter-app")]),
    "who": st("who should count more", "voting sim, playable", 1240, 680, "t",
              "should educated votes count more? set it up, run the election, see who wins.",
              [("play", "https://yaqzans.github.io/who-should-count-more/"),
               ("repo", "https://github.com/yaqzans/who-should-count-more")]),
    "ttt": st("tictactoe ∞", "4 pieces, then move them", 1500, 790, "b",
              "tic-tac-toe where you only get 4 pieces, then you have to move them. has a bot with a "
              "difficulty slider.",
              [("play", "https://yaqzans.github.io/TicTacToeInfinity/"),
               ("repo", "https://github.com/yaqzans/TicTacToeInfinity")]),
}

# lines: id -> (name, color, route). a route is station ids and (x, y) waypoints;
# the arrow goes on the last stop.
L = {
    "red":    ("machine learning", "#dc241f", ["vehicle", "aiub", "sarcasm", "oshud", "medease"]),
    "pink":   ("language", "#d6559b", ["english", "aiub", "sarcasm", "oshud", "medease", (1600, 380)]),
    "blue":   ("papers", "#0019a8", ["hand", "blood", "agile", "hybrid"]),
    "green":  ("hardware", "#00843d", ["hand", "pm25", (1375, 300), (1375, 880)]),
    "yellow": ("out & about", "#e8a200", ["english", "undp", "aiub", "embassy"]),
    "cyan":   ("side projects", "#0098d4", ["aiub", "md", "who", "ttt"]),
}

RIVER = "M-60,610 C120,600 220,560 330,600 S470,700 560,690 S700,600 800,610 S960,640 1040,620 S1200,560 1300,620 S1500,720 1720,700"

W, H = 1600, 960
INK, PAPER, SOFT, RIVERC = "#1d1d1f", "#ffffff", "#6e6e73", "#d4ebf7"
FONT = "Inter,'Helvetica Neue',Arial,sans-serif"
LW = 7      # line width
GAP = 2.5   # space between lines sharing track


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------
def pos(tok):
    return (S[tok]["x"], S[tok]["y"]) if isinstance(tok, str) else tok


def stations_of(lid):
    return [t for t in L[lid][2] if isinstance(t, str)]


def lines_at(sid):
    return [lid for lid in L if sid in stations_of(lid)]


def leg(a, b):
    """Octilinear path from a to b: diagonal first, then straight."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    d = min(abs(dx), abs(dy))
    sx, sy = (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)
    if d == 0 or abs(dx) == abs(dy):
        return [a, b]
    return [a, (x1 + sx * d, y1 + sy * d), b]


def shared():
    """Which lines run between the same two stations, in a fixed order."""
    use = {}
    for lid, (_, _, r) in L.items():
        for a, b in zip(r, r[1:]):
            if isinstance(a, str) and isinstance(b, str):
                use.setdefault(tuple(sorted((a, b))), []).append(lid)
    return use


SHARED = shared()


def offset_poly(pts, o):
    """Shift a polyline sideways by o, keeping the corners sharp (mitre)."""
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
    """The polyline actually drawn for a line, with shared track pushed apart."""
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


def rounded(pts, r=34):
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
    """Points where each line serving a station actually passes it."""
    x, y = S[sid]["x"], S[sid]["y"]
    out = []
    for lid in lines_at(sid):
        pts = line_points(lid)
        out.append(min(pts, key=lambda p: math.dist(p, (x, y))))
    return out


def marker_box(sid):
    """(x0, y0, x1, y1) of the station marker."""
    x, y = S[sid]["x"], S[sid]["y"]
    n = len(lines_at(sid))
    if n == 1:
        return (x - 8, y - 8, x + 8, y + 8)
    ps = where_lines_pass(sid)
    xs, ys = [p[0] for p in ps], [p[1] for p in ps]
    pad = 12 if sid != "aiub" else 15
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def marker(sid):
    x0, y0, x1, y1 = marker_box(sid)
    if len(lines_at(sid)) == 1:
        return f'<circle class="sh" cx="{S[sid]["x"]}" cy="{S[sid]["y"]}" r="8" fill="#fff" stroke="{INK}" stroke-width="2.8"/>'
    w, h = x1 - x0, y1 - y0
    r = min(w, h) / 2
    return (f'<rect class="sh" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:.1f}" '
            f'fill="#fff" stroke="{INK}" stroke-width="{3.6 if sid == "aiub" else 3}"/>')


def label(sid):
    s = S[sid]
    x, y, side = s["x"], s["y"], s["side"]
    x0, y0, x1, y1 = marker_box(sid)
    big = " hubname" if sid == "aiub" else ""
    nx, ny, anchor = {"r": (x1 + 8, y + 1, "start"), "l": (x0 - 8, y + 1, "end"),
                      "t": (x, y0 - 28, "middle"), "b": (x, y1 + 22, "middle"),
                      "tl": (x0 - 4, y0 - 26, "end")}[side]
    return (f'<text x="{nx:.0f}" y="{ny:.0f}" text-anchor="{anchor}" class="lbl{big}">{esc(s["name"])}</text>'
            f'<text x="{nx:.0f}" y="{ny + 19:.0f}" text-anchor="{anchor}" class="tag">{esc(s["tag"])}</text>')


def end_dir(lid):
    pts = line_points(lid)
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    n = math.dist((ax, ay), (bx, by))
    return (bx, by), ((bx - ax) / n, (by - ay) / n)


def arrow(lid):
    """The line runs on past its last stop into an arrowhead."""
    color = L[lid][1]
    (x2, y2), (ux, uy) = end_dir(lid)
    sx, sy = x2 + ux * 30, y2 + uy * 30
    tx, ty = sx + ux * 19, sy + uy * 19
    px, py = -uy * 12, ux * 12
    return (f'<path d="M{x2:.1f},{y2:.1f} L{sx:.1f},{sy:.1f}" stroke="{color}" stroke-width="{LW}" fill="none"/>'
            f'<path d="M{tx:.1f},{ty:.1f} L{sx + px:.1f},{sy + py:.1f} L{sx - px:.1f},{sy - py:.1f}Z" fill="{color}"/>')


def badge_box(lid):
    name, color, _ = L[lid]
    (bx, by), (ux, uy) = end_dir(lid)
    w = len(name) * 9.2 + 20
    tip = (bx + ux * 50, by + uy * 50)
    if abs(ux) > .9:
        cx, cy = tip[0] + ux * (12 + w / 2), tip[1]
    elif abs(uy) > .9:
        cx, cy = tip[0], tip[1] + uy * 24
    else:
        cx, cy = tip[0] + ux * (10 + w / 2), tip[1] + uy * 22
    return name, color, cx, cy, w


def line_badge(lid):
    name, color, cx, cy, w = badge_box(lid)
    return (f'<g class="badge" data-line="{lid}"><rect x="{cx - w / 2:.0f}" y="{cy - 13:.0f}" width="{w:.0f}" height="26" rx="2" fill="{color}"/>'
            f'<text x="{cx:.0f}" y="{cy + 5:.0f}" text-anchor="middle" fill="#fff" font-family="{FONT}" font-size="14" '
            f'font-weight="700" letter-spacing=".6">{esc(name.upper())}</text></g>')


def view():
    """Bounding box of everything drawn, with a margin: the part of the canvas the poster shows."""
    xs = [v["x"] for v in S.values()]
    ys = [v["y"] for v in S.values()]
    for sid, v in S.items():          # rough label extents, so no name gets cut off
        x0, _, x1, _ = marker_box(sid)
        w = max(len(v["name"]) * 10, len(v["tag"]) * 7.6)
        if v["side"] in ("l", "tl"):
            xs.append(x0 - 8 - w)
        elif v["side"] == "r":
            xs.append(x1 + 8 + w)
        else:
            xs += [v["x"] - w / 2, v["x"] + w / 2]
    for lid in L:
        _, _, cx, cy, w = badge_box(lid)
        xs += [cx - w / 2, cx + w / 2]
        ys += [cy - 14, cy + 14]
        for p in line_points(lid):
            xs.append(p[0]); ys.append(p[1])
    x0, x1 = min(xs) - 30, max(xs) + 30
    y0, y1 = min(ys) - 64, max(ys) + 70
    return (round(x0), round(y0), round(x1 - x0), round(y1 - y0))


def map_svg(interactive=True):
    style = (f"<style>.lbl{{font:500 18.5px {FONT};fill:{INK}}}.hubname{{font-weight:700;font-size:22px;letter-spacing:1px}}"
             f".tag{{font:400 14.5px {FONT};fill:{SOFT}}}"
             f".lbl,.tag{{paint-order:stroke;stroke:{PAPER};stroke-width:5px;stroke-linejoin:round}}</style>")
    o = [style, f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="{PAPER}"/>',
         f'<path class="river" d="{RIVER}" fill="none" stroke="{RIVERC}" stroke-width="54" stroke-linecap="round"/>']
    for lid, (name, color, _) in L.items():
        o.append(f'<path id="L-{lid}" class="line" data-line="{lid}" d="{rounded(line_points(lid))}" fill="none" '
                 f'stroke="{color}" stroke-width="{LW}" stroke-linejoin="round"/>')
        o.append(f'<g class="cap" data-line="{lid}">{arrow(lid)}</g>')
        o.append(line_badge(lid))
    o.append('<g id="trains"></g>')
    for sid, s in S.items():
        attrs = (f' class="stn" data-id="{sid}" tabindex="0" role="button" aria-label="{esc(s["name"])}: {esc(s["tag"])}"'
                 if interactive else "")
        o.append(f'<g{attrs}>{marker(sid)}<circle cx="{s["x"]}" cy="{s["y"]}" r="26" fill="transparent"/>{label(sid)}</g>')
    return "\n".join(o)


# --------------------------------------------------------------------------
# the page: a framed map on a station wall, a departures board, a clock
# --------------------------------------------------------------------------
def data_json():
    ln = {lid: dict(name=n, color=c, stations=stations_of(lid)) for lid, (n, c, _) in L.items()}
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
                     f'<span>{len(stations_of(lid))} stops</span></button>' for lid, (n, c, _) in L.items())
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
      <p>each coloured line is one part of what i do. each stop is one thing: a project, a paper, an event. where lines meet, the two things are connected.</p>
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
  <p class="m-intro">each line is one part of what i do. pick a line, then tap a stop.</p>
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
    """Profile README image: the map poster itself, LED board set into its header, trains running."""
    vx, vy, vw, vh = view()
    TW, pad = 1600, 16
    pw = TW - 2 * pad
    mh = pw * vh / vw
    head, foot = 96, 54
    ph = head + mh + foot
    TH = round(ph + 2 * pad)
    trains = []
    for i, lid in enumerate(L):
        color = L[lid][1]
        pts = line_points(lid)
        length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        dur = max(5, length / 120)
        trains.append(f'<rect x="-15" y="-6.5" width="30" height="13" rx="2" fill="{color}" stroke="#fff" stroke-width="2">'
                      f'<animateMotion path="{rounded(pts)}" dur="{dur * 2:.1f}s" begin="-{i * 2.3:.1f}s" repeatCount="indefinite" '
                      f'rotate="auto" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear"/></rect>')
    body = map_svg(interactive=False).replace('<g id="trains"></g>', "".join(trains))
    legend, lx = [], 28
    for n, c, _ in L.values():   # spaced by name length
        legend.append(f'<g transform="translate({lx} {head + mh + 34:.0f})"><rect width="30" height="7" y="-8" fill="{c}"/>'
                      f'<text x="40" y="0" font-family="{FONT}" font-size="18" fill="{INK}">{esc(n)}</text></g>')
        lx += 40 + len(n) * 10 + 34
    legend = "".join(legend)
    bx, bw = pw - 500, 476
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}" width="{TW}" height="{TH}">
<defs>
  <pattern id="unlit" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1.3" fill="#2a1a07"/></pattern>
  <pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="2.05" fill="#fff"/></pattern>
  <mask id="ledmask"><rect width="{TW}" height="{TH}" fill="url(#dots)"/></mask>
  <filter id="glow" x="-10%" y="-60%" width="120%" height="220%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="alu" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#dcdde0"/><stop offset=".5" stop-color="#9ea1a6"/><stop offset="1" stop-color="#d2d4d7"/></linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset=".2" stop-color="#fff" stop-opacity="0"/><stop offset=".28" stop-color="#fff" stop-opacity=".16"/><stop offset=".36" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <style>@keyframes b{{50%{{opacity:.1}}}}.blink{{animation:b 1.2s steps(1) infinite}}</style>
</defs>
<rect width="{TW}" height="{TH}" rx="10" fill="url(#alu)"/>
<g transform="translate({pad} {pad})">
  <rect width="{pw}" height="{ph:.0f}" fill="#fff"/>
  <svg x="24" y="22" width="52" height="52" viewBox="-30 -30 60 60"><circle r="22" fill="none" stroke="#dc241f" stroke-width="9"/><rect x="-29" y="-6" width="58" height="12" fill="#0019a8"/></svg>
  <text x="92" y="50" font-family="{FONT}" font-size="34" font-weight="700" fill="{INK}" letter-spacing="-.5">yaqzan's network map</text>
  <text x="93" y="76" font-family="{FONT}" font-size="17" fill="{SOFT}">projects, papers and things i showed up for. click the map to ride it.</text>
  <g transform="translate({bx} 16)">
    <rect width="{bw}" height="64" rx="3" fill="#0b0b0b" stroke="#333" stroke-width="3"/>
    <rect x="6" y="6" width="{bw - 12}" height="52" fill="url(#unlit)"/>
    <g filter="url(#glow)"><g mask="url(#ledmask)" font-family="ui-monospace,Consolas,monospace" font-weight="800" fill="#ffb238">
      <text x="18" y="44" font-size="30">all lines</text>
      <text x="{bw - 18}" y="44" font-size="30" text-anchor="end" class="blink">now boarding</text>
    </g></g>
  </g>
  <line x1="0" y1="{head}" x2="{pw}" y2="{head}" stroke="#d7d7db" stroke-width="2"/>
  <svg x="0" y="{head}" width="{pw}" height="{mh:.0f}" viewBox="{vx} {vy} {vw} {vh}">{body}</svg>
  <line x1="0" y1="{head + mh:.0f}" x2="{pw}" y2="{head + mh:.0f}" stroke="#d7d7db" stroke-width="2"/>
  {legend}
  <rect width="{pw}" height="{ph:.0f}" fill="url(#glass)"/>
</g>
</svg>'''


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    for lid, (_, _, r) in L.items():
        for tok in r:
            assert not isinstance(tok, str) or tok in S, f"{lid}: unknown station {tok}"
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
