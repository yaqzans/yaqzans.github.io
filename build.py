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
SEMS = [("su23", 1), ("f23", 1), ("sp24", 1), ("su24", 1), ("f24", 1), ("sp25", 1), ("su25", 1),
        ("f25", 1), ("sp26", 2), ("su26", 2), ("f26", 1), ("j27", 1)]
YEAR_OF = {"su23": 2023, "f23": 2023, "sp24": 2024, "su24": 2024, "f24": 2024, "sp25": 2025, "su25": 2025,
           "f25": 2025, "sp26": 2026, "su26": 2026, "f26": 2026, "j27": 2027}
SLOT, X0 = 175, 140
SEM_X = {}
_x = X0
for _s, _n in SEMS:
    SEM_X[_s] = (_x, _n)
    _x += _n * SLOT
X_END = _x
NOW_X = SEM_X["f26"][0] + SLOT * .55          # early October 2026


def col(sem, slot=0):
    x0, n = SEM_X[sem]
    return round(x0 + (slot + .5) * SLOT)


# lanes, from the trunk. lines above the trunk peel upwards, below downwards
TY = 560
LANE = {"yellow": TY - 350, "cyan": TY - 175, "aiub": TY, "red": TY + 175, "green": TY + 330, "blue": TY + 480}
BUNDLE = {"yellow": -26, "cyan": -13, "aiub": 0, "red": 13, "green": 26, "blue": 39}   # side by side on the trunk


# --------------------------------------------------------------------------
# stations. tag = the line printed under the name. side = where the name goes
# --------------------------------------------------------------------------
def st(name, tag, sem, slot, lane, side, text, links=(), related=()):
    return dict(name=name, tag=tag, sem=sem, x=col(sem, slot), y=LANE[lane], side=side, text=text,
                links=list(links), related=list(related))


S = {
    # the AIUB line, through the middle
    "start": st("First Day at AIUB", "Summer 2023", "su23", 0, "aiub", "l",
                "Started a BSc in Computer Science and Engineering at American International University-Bangladesh, "
                "majoring in Computational Theory with a minor in Data Science. Every line on this map leaves from here."),
    "dl1": st("Dean's List", "Spring 2023-24", "sp24", 0, "aiub", "t",
              "Dean's List Honour Award, Spring 2023-24. On an academic scholarship the whole way through."),
    "dl2": st("Dean's List Again", "Fall 2024-25", "f24", 0, "aiub", "t",
              "Dean's List Honour Award, Fall 2024-25. CGPA 3.96."),
    "thesis": st("Thesis", "Final year, in progress", "su26", 0, "aiub", "t",
                 "Final-year thesis on reliable machine learning evaluation. Not public yet."),
    "grad": st("Graduation", "January 2027", "j27", 0, "aiub", "t",
               "End of the line: BSc CSE, January 2027."),

    # out & about
    "poster": st("Poster Competition", "AIUB, Summer 2023", "su23", 0, "yellow", "t",
                 "Selected participant in the AIUB Poster Presentation Competition in my first semester."),
    "english": st("English Club", "Organiser, 10+ events", "f23", 0, "yellow", "b",
                  "Organiser and content writer at the AIUB English Club. Ran 10+ events and workshops for 50+ members."),
    "embassy": st("U.S. Embassy", "AI workshop", "su24", 0, "yellow", "t",
                  "AI workshop at the American Center, Dhaka. Selected by the Faculty of Science and Technology to "
                  "represent AIUB."),
    "undp": st("UNDP Roundtable", "Youth and the SDGs", "sp26", 0, "yellow", "b",
               "Selected to represent AIUB at \"Let's Talk with the UNDP Resident Representative\", a roundtable on "
               "youth engagement in the SDGs."),

    # software
    "parking": st("2D Parking", "OpenGL game", "su25", 0, "cyan", "t",
                  "Park the car before the timer runs out. Built with OpenGL and GLUT for the computer graphics course.",
                  [("Repo", "https://github.com/yaqzans/2D-Parking-Game")]),
    "survey": st("NeedSurveyResponses", "Survey credit platform", "f25", 0, "cyan", "b",
                 "Answer other people's surveys to earn credits, then spend credits to publish your own. PHP and "
                 "MySQL, with separate user and admin views."),
    "ttt": st("TicTacToe ∞", "4 pieces, then move them", "sp26", 0, "cyan", "t",
              "Tic-tac-toe where each player only gets 4 pieces and then has to move them. Includes a bot with a "
              "difficulty slider.",
              [("Play", "https://yaqzans.github.io/TicTacToeInfinity/"),
               ("Repo", "https://github.com/yaqzans/TicTacToeInfinity")]),
    "md": st("Markdown Converter", "Anything to Markdown", "su26", 1, "cyan", "b",
             "PDF, Word, PowerPoint or Excel in, clean Markdown out. A single Windows executable, nothing to install.",
             [("Repo", "https://github.com/yaqzans/markdown-converter-app")]),
    "who": st("Who Should Count More", "Voting simulation", "f26", 0, "cyan", "t",
              "Should educated votes count more? Set up the electorate, run the election and see who wins.",
              [("Play", "https://yaqzans.github.io/who-should-count-more/"),
               ("Repo", "https://github.com/yaqzans/who-should-count-more")]),

    # machine learning
    "medease": st("MedEase BD", "Offline medicine LLM", "sp26", 0, "red", "b",
                  "Medicine assistant for English, Bangla and Banglish queries. RAG over 21,000+ medicines plus a "
                  "Gemma 3 4B fine-tuned on 36,000+ medicine Q&A pairs, running fully offline."),
    "oshud": st("OshudBot", "Bangla medicine bot", "sp26", 1, "red", "t",
                "The lightweight sibling of MedEase. Covers 21,714 brands and answers in about 15 ms on a CPU. "
                "It replaced 1.1 GB of models with transliteration and fuzzy matching at no loss in answer quality.",
                [("Repo", "https://github.com/yaqzans/oshudbot"), ("Try it", "https://oshudbot.streamlit.app/")],
                ["medease"]),
    "vehicle": st("Vehicle Recognition", "YOLO + ConvNeXt", "su26", 0, "red", "b",
                  "Bangladeshi road vehicles on RSUD20K. YOLO26n finds them and ConvNeXt-Tiny classifies every crop. "
                  "Code, results and the paper.",
                  [("Repo", "https://github.com/yaqzans/cvpr-two-stage-vehicle-recognition")]),
    "sarcasm": st("Sarcasm Detection", "Bag of Words vs TF-IDF", "su26", 1, "red", "t",
                  "Can a classifier tell when a tweet is sarcastic? Bag of Words against TF-IDF across four "
                  "classifiers, in R.", [("Repo", "https://github.com/yaqzans/ids-sarcasm-detection")]),

    # hardware
    "hand": st("Robotic Hand", "Became the QPAIN paper", "f25", 0, "green", "b",
               "A camera watches your hand and a 7-servo robotic hand copies it, with no gloves or sensors. 88 ms "
               "end to end at 24.6 FPS, built for about 2,800 BDT. It became a paper: Gesture Controlled Robotic "
               "Hand Designed for Enhancing Industrial Automation and Innovation, IEEE QPAIN 2026, second and "
               "corresponding author.",
               [("Read the paper", "https://doi.org/10.1109/QPAIN69676.2026.11545528")]),
    "pm25": st("PM2.5 Monitor", "Air quality alerts, ESP32", "sp26", 1, "green", "b",
               "Pocket air quality monitor with a React Native app. It alerts only on genuine spikes, not on Dhaka's "
               "constantly high baseline. In a two-week field study it sent about 4 alerts a day instead of dozens, "
               "and each one was acted on."),

    # papers
    "blood": st("Blood-Like Solution", "Physics conf. 2024, journal 2025", "su24", 0, "blue", "b",
                "Development of a Simulated Blood-Like Solution for Medical Experiments. Presented at the "
                "International Conference on Physics 2024 and published in Analytical Chemistry Letters (2025). "
                "Fifth author.", [("Read the paper", "https://doi.org/10.1080/22297928.2025.2533331")]),
    "hybrid": st("Human-AI Animation", "ICCTASS 2025", "sp25", 0, "blue", "t",
                 "A Hybrid Human-AI Model for Sustainable Innovation in Media and Animation. Presented at ICCTASS "
                 "2025. Third author."),
    "agile": st("Agile + Waterfall", "IEOM Bangladesh 2025", "su25", 0, "blue", "b",
                "Evaluating the Performance of Agile-Waterfall Integrated Approaches in Large Scale Engineering "
                "Projects in Bangladesh. IEOM Bangladesh 2025. Fifth author.",
                [("Read the paper", "https://doi.org/10.46254/BA08.20250467")]),
}
# the robotic hand is where hardware and papers meet: it sits between their lanes
S["hand"]["y"] = (LANE["green"] + LANE["blue"]) // 2 - 10


def peel(lid, first):
    """Leave the first-day station in the bundle, run along the trunk, then turn off to the line's lane
    so the line reaches its lane just before its first stop."""
    off = BUNDLE[lid]
    fx, fy = S[first]["x"], S[first]["y"]
    dy = fy - (TY + off)
    turn = fx - abs(dy) - 40
    return [("start", off), (turn, TY + off)]


# lines: id -> (name, color, route). a route is station ids, (station, dy) for a station
# passed off-centre, and (x, y) waypoints. the arrow goes on the end.
L = {
    "aiub":   ("AIUB", "#1d1d1f", ["start", "dl1", "dl2", "thesis", "grad"]),
    "yellow": ("Out & About", "#f2a900", [("start", -26), "poster", "english", "embassy", "undp",
                                          (NOW_X + 60, LANE["yellow"])]),
    "cyan":   ("Software", "#009fe3", peel("cyan", "parking") + ["parking", "survey", "ttt", "md", "who"]),
    "red":    ("Machine Learning", "#e1251b", peel("red", "medease") + ["medease", "oshud", "vehicle", "sarcasm"]),
    "green":  ("Hardware", "#00a651", peel("green", "hand") + ["hand", "pm25"]),
    "blue":   ("Papers", "#1f3fa8", peel("blue", "blood") + ["blood", "hybrid", "agile", (S["hand"]["x"] - 130, LANE["blue"]),
                                                             "hand", (S["hand"]["x"] + 70, S["hand"]["y"]),
                                                             (S["hand"]["x"] + 260, LANE["blue"])]),
}

W, H = X_END + 200, 1100
BG, INK, SOFT, ZONE, NOWC = "#fbfaf7", "#1d1d1f", "#6e6e73", "#f1eee8", "#e1251b"
FONT = "Inter,'Helvetica Neue',Arial,sans-serif"
LW = 8      # line width
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
        return (x - 10, y - 10, x + 10, y + 10)
    ps = where_lines_pass(sid)
    xs, ys = [p[0] for p in ps], [p[1] for p in ps]
    return (min(xs) - 14, min(ys) - 14, max(xs) + 14, max(ys) + 14)


def marker(sid):
    x0, y0, x1, y1 = marker_box(sid)
    if len(lines_at(sid)) == 1:
        return f'<circle class="sh" cx="{S[sid]["x"]}" cy="{S[sid]["y"]}" r="10" fill="#fff" stroke="{INK}" stroke-width="3.5"/>'
    w, h = x1 - x0, y1 - y0
    return (f'<rect class="sh" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{min(w, h) / 2:.1f}" '
            f'fill="#fff" stroke="{INK}" stroke-width="4"/>')


def label(sid):
    s = S[sid]
    x, y, side = s["x"], s["y"], s["side"]
    x0, y0, x1, y1 = marker_box(sid)
    nx, ny, anchor = {"r": (x1 + 12, y + 2, "start"), "l": (x0 - 12, y + 2, "end"),
                      "t": (x, y0 - 42, "middle"), "b": (x, y1 + 33, "middle")}[side]
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
    tx, ty = sx + ux * 19, sy + uy * 19
    px, py = -uy * 12, ux * 12
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
    dark = "#1d1d1f" if lid == "yellow" else "#fff"
    return (f'<g class="badge" data-line="{lid}"><rect x="{cx - w / 2:.0f}" y="{cy - 16:.0f}" width="{w:.0f}" height="32" rx="2" fill="{color}"/>'
            f'<text x="{cx:.0f}" y="{cy + 6:.0f}" text-anchor="middle" fill="{dark}" font-family="{FONT}" font-size="17" '
            f'font-weight="700" letter-spacing=".6">{esc(name.upper())}</text></g>')


def view():
    xs = [X0 - 40, X_END + 40]
    ys = []
    for sid, v in S.items():
        x0, y0, x1, y1 = marker_box(sid)
        w = max(len(v["name"]) * 16, len(v["tag"]) * 10.5)
        if v["side"] == "l":
            xs.append(x0 - 8 - w)
        else:
            xs += [v["x"] - w / 2, v["x"] + w / 2]
        ys += [y0 - 80, y1 + 80]
    for lid in L:
        _, _, cx, cy, w = badge_box(lid)
        xs += [cx - w / 2, cx + w / 2]
        ys += [cy - 14, cy + 14]
    y0 = min(ys) - 100     # room for the year labels
    return (round(min(xs) - 30), round(y0), round(max(xs) - min(xs) + 60), round(max(ys) - y0 + 30))


def zones():
    """Years as fare zones: alternate bands, the year written at the top, 'now' and the future."""
    vx, vy, vw, vh = view()
    out, years = [], {}
    for s, n in SEMS:
        x0, _ = SEM_X[s]
        y = YEAR_OF[s]
        a, b = years.get(y, (x0, x0 + n * SLOT))
        years[y] = (min(a, x0), max(b, x0 + n * SLOT))
    for i, (yr, (a, b)) in enumerate(sorted(years.items())):
        if i % 2 == 0:
            out.append(f'<rect x="{a}" y="{vy}" width="{b - a}" height="{vh}" fill="{ZONE}"/>')
        out.append(f'<text x="{(a + b) / 2:.0f}" y="{vy + 62}" text-anchor="middle" class="year">{yr}</text>')
    out.append(f'<rect x="{NOW_X:.0f}" y="{vy}" width="{X_END - NOW_X + 400:.0f}" height="{vh}" fill="url(#future)"/>')
    out.append(f'<line x1="{NOW_X:.0f}" y1="{vy + 84}" x2="{NOW_X:.0f}" y2="{vy + vh}" stroke="{NOWC}" stroke-width="2" stroke-dasharray="5 7"/>')
    out.append(f'<text x="{NOW_X + 10:.0f}" y="{vy + 102}" class="now">NOW</text>')
    return "".join(out)


def map_svg(interactive=True):
    style = (f"<style>.lbl{{font:600 27px {FONT};fill:{INK}}}.tag{{font:400 19px {FONT};fill:{SOFT}}}"
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
    # the future: the AIUB line past 'now' is still being built
    o.append(f'<path d="M{NOW_X:.0f},{TY} L{S["grad"]["x"] + 80},{TY}" stroke="{BG}" stroke-width="{LW + 2}" stroke-dasharray="10 10"/>')
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


def clock_svg():
    ticks = "".join(f'<line x1="0" y1="-38" x2="0" y2="{-30 if i % 3 == 0 else -34}" stroke="#fff" '
                    f'stroke-width="{3 if i % 3 == 0 else 1.6}" transform="rotate({i * 30})"/>' for i in range(12))
    return (f'<svg class="sclock" viewBox="-50 -50 100 100" aria-hidden="true">'
            f'<rect x="-50" y="-50" width="100" height="100" rx="6" fill="#141414"/>'
            f'<circle r="43" fill="#0b0b0b" stroke="#262626" stroke-width="2"/>{ticks}'
            f'<line class="ch" y2="-21" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>'
            f'<line class="cm" y2="-32" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>'
            f'<line class="cs" y1="6" y2="-34" stroke="#e1251b" stroke-width="1.2"/>'
            f'<circle r="2.5" fill="#e1251b"/></svg>')


def board_html():
    return ('<div class="board" aria-live="polite"><div class="screen">'
            '<div class="led"><span class="led1">All Lines</span></div>'
            '<div class="led row"><span class="led2">Good Service</span><span class="led3"></span></div>'
            '</div></div>')


def namesign():
    bars = "".join(f'<i style="background:{c}"></i>' for _, c, _ in L.values())
    return f'<div class="namesign"><b>Yaqzan’s</b><div class="bars">{bars}</div></div>'


def exits_html(cls):
    items = "".join(f'<a href="{esc(u)}"><span class="ex">{l}</span><span class="ar">{a}</span>{esc(t)}</a>'
                    for l, a, t, u in EXITS)
    return f'<nav class="{cls}" aria-label="Links"><div class="exit-head">Exits</div><div class="exit-list">{items}</div></nav>'


def roundel(size=44):
    return (f'<svg class="roundel" viewBox="-30 -30 60 60" width="{size}" height="{size}" aria-hidden="true">'
            f'<circle r="22" fill="none" stroke="#e1251b" stroke-width="9"/>'
            f'<rect x="-29" y="-6" width="58" height="12" fill="#1f3fa8"/></svg>')


def stamp(path):
    """Short content hash, so browsers fetch the new file after every deploy."""
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


KEY = ("Time runs left to right. Every line leaves the first day at AIUB and branches off when that thread "
       "began. Where two lines meet, one thing led to the other.")


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
<title>Yaqzan's Metro</title>
<meta name="description" content="Projects, papers and everything else since 2023, drawn as a metro map. Pick a stop and a train takes you there.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Doto:wght@800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v={stamp('style.css')}">
</head>
<body>

<div class="d">
<div class="ceiling"><i></i><i></i></div>

<div class="wall">
  <header class="top">
    <div class="hang">{clock_svg()}{board_html()}</div>
    {namesign()}
    {exits_html("exits")}
  </header>

  <main class="poster-wrap">
    <figure class="poster" style="--ar:{vw / vh:.3f}">
      <header class="poster-head">
        {roundel()}
        <div>
          <h1>2023 → 2027</h1>
          <p>Every line is one thread of my work. Read it left to right.</p>
        </div>
      </header>
      <div id="scroller">
        <svg id="map" viewBox="{vx} {vy} {vw} {vh}" role="img" aria-label="Metro map of projects, papers and activities since 2023">
{map_svg()}
        </svg>
      </div>
      <footer class="poster-foot">
        <div class="legend">{legend}</div>
        <p class="key">{KEY} Pick any stop to ride there.</p>
      </footer>
      <div class="glass"></div>
    </figure>
  </main>
</div>

<div class="platform"></div>

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
  <div class="m-ceiling"></div>
  <div class="m-hang">{clock_svg()}{board_html()}</div>
  {namesign()}
  <p class="m-intro">{KEY}</p>
  <nav class="m-tabs" role="tablist">{m_tabs}</nav>
  <section class="m-route" id="m-route" aria-live="polite"></section>
  {exits_html("m-exits")}
  <div class="m-platform"></div>
</div>

<script id="data" type="application/json">{data_json()}</script>
<script src="app.js?v={stamp('app.js')}"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# profile README image: the framed map with the board in its header, no js
# --------------------------------------------------------------------------
def teaser():
    vx, vy, vw, vh = view()
    TW, pad = 1600, 16
    pw = TW - 2 * pad
    mh = pw * vh / vw
    head, foot = 100, 56
    ph = head + mh + foot
    TH = round(ph + 2 * pad)
    trains = []
    for i, lid in enumerate(L):
        color = L[lid][1]
        pts = line_points(lid)
        length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        dur = max(5, length / 130)
        trains.append(f'<rect x="-17" y="-7.5" width="34" height="15" rx="2" fill="{color}" stroke="#fff" stroke-width="2.5">'
                      f'<animateMotion path="{rounded(pts)}" dur="{dur * 2:.1f}s" begin="-{i * 2.3:.1f}s" repeatCount="indefinite" '
                      f'rotate="auto" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear"/></rect>')
    body = map_svg(interactive=False).replace('<g id="trains"></g>', "".join(trains))
    legend, lx = [], 28
    for n, c, _ in L.values():
        legend.append(f'<g transform="translate({lx} {head + mh + 35:.0f})"><rect width="32" height="8" y="-9" fill="{c}"/>'
                      f'<text x="42" y="0" font-family="{FONT}" font-size="19" fill="{INK}">{esc(n)}</text></g>')
        lx += 42 + len(n) * 11 + 34
    legend = "".join(legend)
    bx, bw = pw - 470, 446
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}" width="{TW}" height="{TH}">
<defs>
  <pattern id="unlit" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1.3" fill="#2a1a07"/></pattern>
  <pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="2.05" fill="#fff"/></pattern>
  <mask id="ledmask"><rect width="{TW}" height="{TH}" fill="url(#dots)"/></mask>
  <filter id="glow" x="-10%" y="-60%" width="120%" height="220%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="alu" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e2e3e6"/><stop offset=".5" stop-color="#a3a6ab"/><stop offset="1" stop-color="#d6d8db"/></linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset=".2" stop-color="#fff" stop-opacity="0"/><stop offset=".28" stop-color="#fff" stop-opacity=".22"/><stop offset=".36" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <style>@keyframes b{{50%{{opacity:.1}}}}.blink{{animation:b 1.2s steps(1) infinite}}</style>
</defs>
<rect width="{TW}" height="{TH}" rx="8" fill="url(#alu)"/>
<g transform="translate({pad} {pad})">
  <rect width="{pw}" height="{ph:.0f}" fill="{BG}"/>
  <svg x="26" y="24" width="54" height="54" viewBox="-30 -30 60 60"><circle r="22" fill="none" stroke="#e1251b" stroke-width="9"/><rect x="-29" y="-6" width="58" height="12" fill="#1f3fa8"/></svg>
  <text x="96" y="54" font-family="{FONT}" font-size="38" font-weight="800" fill="{INK}" letter-spacing="-.5">Yaqzan’s Metro</text>
  <text x="97" y="80" font-family="{FONT}" font-size="18" fill="{SOFT}">2023 → 2027. Every line is one thread of my work. Click the map to ride it.</text>
  <g transform="translate({bx} 18)">
    <rect width="{bw}" height="64" rx="3" fill="#0b0b0b" stroke="#333" stroke-width="3"/>
    <rect x="6" y="6" width="{bw - 12}" height="52" fill="url(#unlit)"/>
    <g filter="url(#glow)"><g mask="url(#ledmask)" font-family="ui-monospace,Consolas,monospace" font-weight="800" fill="#ffb238">
      <text x="18" y="44" font-size="30">All Lines</text>
      <text x="{bw - 18}" y="44" font-size="30" text-anchor="end" class="blink">Good Service</text>
    </g></g>
  </g>
  <line x1="0" y1="{head}" x2="{pw}" y2="{head}" stroke="#d9d6cf" stroke-width="2"/>
  <svg x="0" y="{head}" width="{pw}" height="{mh:.0f}" viewBox="{vx} {vy} {vw} {vh}">{body}</svg>
  <line x1="0" y1="{head + mh:.0f}" x2="{pw}" y2="{head + mh:.0f}" stroke="#d9d6cf" stroke-width="2"/>
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
