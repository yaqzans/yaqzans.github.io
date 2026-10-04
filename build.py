"""Build yaqzan's metro.

The map is a timeline. Left to right is time, from the first day at aiub in
summer 2023 to graduation in january 2027. Every line leaves the first-day
station together and peels off in the semester that thread began; each stop
sits in the semester it happened. Lines only meet where one thing led to
another.

Everything lives in this file. Edit it and run `python build.py`. It writes
index.html (the map is baked in as SVG, app.js animates it) and the teaser for
the profile README in ../yaqzans/assets/map.svg.
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
SLOT, X0 = 165, 140
SEM_X = {}
_x = X0
for _s, _n in SEMS:
    SEM_X[_s] = (_x, _n)
    _x += _n * SLOT
X_END = _x
NOW_X = SEM_X["f26"][0] + SLOT * .55          # early october 2026


def col(sem, slot=0):
    x0, n = SEM_X[sem]
    return round(x0 + (slot + .5) * SLOT)


# lanes, from the trunk. lines above the trunk peel upwards, below downwards
TY = 520
LANE = {"yellow": TY - 310, "cyan": TY - 150, "aiub": TY, "red": TY + 150, "green": TY + 290, "blue": TY + 430}
BUNDLE = {"yellow": -24, "cyan": -12, "aiub": 0, "red": 12, "green": 24, "blue": 36}   # side by side on the trunk


# --------------------------------------------------------------------------
# stations. tag = the line printed under the name. side = where the name goes
# --------------------------------------------------------------------------
def st(name, tag, sem, slot, lane, side, text, links=(), related=()):
    return dict(name=name, tag=tag, sem=sem, x=col(sem, slot), y=LANE[lane], side=side, text=text,
                links=list(links), related=list(related))


S = {
    # the aiub line, through the middle
    "start": st("first day, AIUB", "summer 2023", "su23", 0, "aiub", "l",
                "started a bsc in computer science and engineering at american international university-bangladesh, "
                "major in computational theory, minor in data science. every line on this map leaves from here."),
    "dl1": st("dean's list", "spring 2023-24", "sp24", 0, "aiub", "t",
              "dean's list honour award, spring 2023-24. on an academic scholarship the whole way."),
    "dl2": st("dean's list again", "fall 2024-25", "f24", 0, "aiub", "t",
              "dean's list honour award, fall 2024-25. cgpa 3.96."),
    "thesis": st("thesis", "final year, in progress", "su26", 1, "aiub", "t",
                 "final-year thesis on reliable machine learning evaluation. not public yet."),
    "grad": st("graduation", "january 2027", "j27", 0, "aiub", "t",
               "end of the line. bsc cse done in january 2027."),

    # out & about
    "poster": st("poster competition", "aiub, summer 2023", "su23", 0, "yellow", "t",
                 "selected participant in the aiub poster presentation competition, first semester."),
    "english": st("english club", "organiser, 10+ events", "f23", 0, "yellow", "b",
                  "organiser and content writer at the aiub english club. 10+ events and workshops, 50+ members."),
    "embassy": st("u.s. embassy", "ai workshop", "su24", 0, "yellow", "t",
                  "ai workshop at the american center, dhaka. the faculty of science and technology sent me to "
                  "represent aiub."),
    "undp": st("undp roundtable", "youth and the sdgs", "sp26", 0, "yellow", "b",
               "picked to represent aiub at let's talk with the undp resident representative, a roundtable on "
               "youth and the sdgs."),

    # software
    "parking": st("2d parking", "opengl game", "su25", 0, "cyan", "t",
                  "park the car before the timer runs out. opengl and glut, computer graphics course.",
                  [("repo", "https://github.com/yaqzans/2D-Parking-Game")]),
    "survey": st("needsurveyresponses", "survey credits, php", "f25", 0, "cyan", "b",
                 "answer other people's surveys to earn credits, spend credits to post your own. php, mysql, "
                 "separate user and admin sides."),
    "ttt": st("tictactoe ∞", "4 pieces, then move them", "sp26", 0, "cyan", "t",
              "tic-tac-toe where you only get 4 pieces, then you have to move them. has a bot with a "
              "difficulty slider.",
              [("play", "https://yaqzans.github.io/TicTacToeInfinity/"),
               ("repo", "https://github.com/yaqzans/TicTacToeInfinity")]),
    "md": st("markdown converter", "anything to markdown", "su26", 1, "cyan", "b",
             "pdf, word, powerpoint or excel in, clean markdown out. one windows exe, nothing to install.",
             [("repo", "https://github.com/yaqzans/markdown-converter-app")]),
    "who": st("who should count more", "voting sim, playable", "f26", 0, "cyan", "t",
              "should educated votes count more? set it up, run the election, see who wins.",
              [("play", "https://yaqzans.github.io/who-should-count-more/"),
               ("repo", "https://github.com/yaqzans/who-should-count-more")]),

    # machine learning
    "medease": st("medease bd", "offline medicine llm", "sp26", 0, "red", "b",
                  "medicine assistant in english, bangla and banglish. rag over 21,000+ medicines plus a gemma 3 4b "
                  "fine-tuned on 36,000+ medicine q&a pairs, running fully offline."),
    "oshud": st("oshudbot", "bangla medicine bot", "sp26", 1, "red", "t",
                "the light version of medease. 21,714 brands, answers in about 15 ms on a cpu. it used to carry "
                "1.1 gb of models, swapped them for transliteration and fuzzy matching and lost nothing.",
                [("repo", "https://github.com/yaqzans/oshudbot"), ("try it", "https://oshudbot.streamlit.app/")],
                ["medease"]),
    "vehicle": st("vehicle recognition", "yolo + convnext", "su26", 0, "red", "b",
                  "bangladeshi road vehicles on rsud20k. yolo26n finds them, convnext-tiny names every crop. code, "
                  "results and the paper.",
                  [("repo", "https://github.com/yaqzans/cvpr-two-stage-vehicle-recognition")]),
    "sarcasm": st("sarcasm detection", "bag of words vs tf-idf", "su26", 1, "red", "t",
                  "can a classifier tell when a tweet is being sarcastic? bag of words vs tf-idf across four "
                  "classifiers, in r.", [("repo", "https://github.com/yaqzans/ids-sarcasm-detection")]),

    # hardware
    "hand": st("robotic hand", "became the qpain paper", "f25", 0, "green", "b",
               "a camera watches your hand and a 7-servo robotic hand copies it. no gloves, no sensors. 88 ms end "
               "to end at 24.6 fps, built for about 2,800 taka. it became a paper: Gesture Controlled Robotic Hand "
               "Designed for Enhancing Industrial Automation and Innovation, ieee qpain 2026, second and "
               "corresponding author.",
               [("read the paper", "https://doi.org/10.1109/QPAIN69676.2026.11545528")]),
    "pm25": st("pm2.5 monitor", "air quality alerts, esp32", "sp26", 1, "green", "b",
               "pocket air quality monitor plus a react native app. it only alerts on real spikes, not on dhaka's "
               "normal bad air. two weeks of field testing: about 4 alerts a day instead of dozens, and people "
               "actually read them."),

    # papers
    "blood": st("blood-like solution", "physics conf 2024, journal 2025", "su24", 0, "blue", "b",
                "Development of a Simulated Blood-Like Solution for Medical Experiments. presented at the "
                "international conference on physics 2024, published in analytical chemistry letters 2025. "
                "fifth author.", [("read the paper", "https://doi.org/10.1080/22297928.2025.2533331")]),
    "hybrid": st("human-ai animation", "icctass 2025", "sp25", 0, "blue", "t",
                 "A Hybrid Human-AI Model for Sustainable Innovation in Media and Animation. presented at icctass "
                 "2025. third author."),
    "agile": st("agile + waterfall", "ieom bangladesh 2025", "su25", 0, "blue", "b",
                "Evaluating the Performance of Agile-Waterfall Integrated Approaches in Large Scale Engineering "
                "Projects in Bangladesh. ieom bangladesh 2025. fifth author.",
                [("read the paper", "https://doi.org/10.46254/BA08.20250467")]),
}
# the robotic hand is where hardware and papers meet: it sits between their lanes
S["hand"]["y"] = (LANE["green"] + LANE["blue"]) // 2 - 10


def peel(lid, first):
    """Leave the first-day station in the bundle, run along the trunk, then turn off to the line's lane
    so the line reaches its lane just before its first stop."""
    off, lane = BUNDLE[lid], LANE[lid]
    fx, fy = S[first]["x"], S[first]["y"]
    dy = fy - (TY + off)
    turn = fx - abs(dy) - 40
    return [("start", off), (turn, TY + off)]


# lines: id -> (name, color, route). a route is station ids, (station, dy) for a station
# passed off-centre, and (x, y) waypoints. the arrow goes on the end.
L = {
    "aiub":   ("aiub", "#e9edf5", ["start", "dl1", "dl2", "thesis", "grad"]),
    "yellow": ("out & about", "#ffb21e", [("start", -24), "poster", "english", "embassy", "undp",
                                          (NOW_X + 60, LANE["yellow"])]),
    "cyan":   ("software", "#28b8f0", peel("cyan", "parking") + ["parking", "survey", "ttt", "md", "who"]),
    "red":    ("machine learning", "#ff4a3d", peel("red", "medease") + ["medease", "oshud", "vehicle", "sarcasm"]),
    "green":  ("hardware", "#2fd26f", peel("green", "hand") + ["hand", "pm25"]),
    "blue":   ("papers", "#5b7bff", peel("blue", "blood") + ["blood", "hybrid", "agile", (S["hand"]["x"] - 130, LANE["blue"]),
                                                             "hand", (S["hand"]["x"] + 70, S["hand"]["y"]), (S["hand"]["x"] + 260, LANE["blue"])]),
}

W, H = X_END + 200, 1000
BG, PANEL, INK, SOFT, ZONE = "#0b0d12", "#11141b", "#eef1f7", "#8a93a6", "#151924"
FONT = "Inter,'Helvetica Neue',Arial,sans-serif"
LW = 7      # line width
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
        return (x - 8, y - 8, x + 8, y + 8)
    ps = where_lines_pass(sid)
    xs, ys = [p[0] for p in ps], [p[1] for p in ps]
    return (min(xs) - 12, min(ys) - 12, max(xs) + 12, max(ys) + 12)


def marker(sid):
    x0, y0, x1, y1 = marker_box(sid)
    if len(lines_at(sid)) == 1:
        return f'<circle class="sh" cx="{S[sid]["x"]}" cy="{S[sid]["y"]}" r="8" fill="{BG}" stroke="#fff" stroke-width="3"/>'
    w, h = x1 - x0, y1 - y0
    return (f'<rect class="sh" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{min(w, h) / 2:.1f}" '
            f'fill="{BG}" stroke="#fff" stroke-width="3.4"/>')


def label(sid):
    s = S[sid]
    x, y, side = s["x"], s["y"], s["side"]
    x0, y0, x1, y1 = marker_box(sid)
    nx, ny, anchor = {"r": (x1 + 8, y + 1, "start"), "l": (x0 - 8, y + 1, "end"),
                      "t": (x, y0 - 34, "middle"), "b": (x, y1 + 26, "middle")}[side]
    return (f'<text x="{nx:.0f}" y="{ny:.0f}" text-anchor="{anchor}" class="lbl">{esc(s["name"])}</text>'
            f'<text x="{nx:.0f}" y="{ny + 22:.0f}" text-anchor="{anchor}" class="tag">{esc(s["tag"])}</text>')


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
    dark = "#0b0d12" if lid in ("aiub", "yellow") else "#fff"
    return (f'<g class="badge" data-line="{lid}"><rect x="{cx - w / 2:.0f}" y="{cy - 13:.0f}" width="{w:.0f}" height="26" rx="3" fill="{color}"/>'
            f'<text x="{cx:.0f}" y="{cy + 5:.0f}" text-anchor="middle" fill="{dark}" font-family="{FONT}" font-size="14" '
            f'font-weight="700" letter-spacing=".6">{esc(name.upper())}</text></g>')


def view():
    xs = [X0 - 40, X_END + 40]
    ys = []
    for sid, v in S.items():
        x0, y0, x1, y1 = marker_box(sid)
        w = max(len(v["name"]) * 13, len(v["tag"]) * 9)
        if v["side"] == "l":
            xs.append(x0 - 8 - w)
        else:
            xs += [v["x"] - w / 2, v["x"] + w / 2]
        ys += [y0 - 66, y1 + 66]
    for lid in L:
        _, _, cx, cy, w = badge_box(lid)
        xs += [cx - w / 2, cx + w / 2]
        ys += [cy - 14, cy + 14]
    y0 = min(ys) - 70      # room for the year labels
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
        out.append(f'<text x="{(a + b) / 2:.0f}" y="{vy + 52}" text-anchor="middle" class="year">{yr}</text>')
    out.append(f'<rect x="{NOW_X:.0f}" y="{vy}" width="{X_END - NOW_X + 400:.0f}" height="{vh}" fill="url(#future)"/>')
    out.append(f'<line x1="{NOW_X:.0f}" y1="{vy + 70}" x2="{NOW_X:.0f}" y2="{vy + vh}" stroke="#ffb21e" stroke-width="1.5" stroke-dasharray="4 6" opacity=".7"/>')
    out.append(f'<text x="{NOW_X + 8:.0f}" y="{vy + 86}" class="now">NOW</text>')
    return "".join(out)


def map_defs():
    return ('<defs><filter id="glow" x="-5%" y="-30%" width="110%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>'
            f'<pattern id="future" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="14" height="14" fill="{BG}" opacity=".35"/><rect width="2" height="14" fill="#fff" opacity=".04"/></pattern></defs>')


def map_svg(interactive=True):
    style = (f"<style>.lbl{{font:600 23px {FONT};fill:{INK}}}.tag{{font:400 16.5px {FONT};fill:{SOFT}}}"
             f".lbl,.tag{{paint-order:stroke;stroke:{BG};stroke-width:5px;stroke-linejoin:round}}"
             f".year{{font:800 46px {FONT};fill:#232938;letter-spacing:2px}}"
             f".now{{font:700 17px {FONT};fill:#ffb21e;letter-spacing:3px}}</style>")
    o = [style, map_defs(), f'<rect x="-600" y="-600" width="{W + 1600}" height="{H + 1600}" fill="{BG}"/>', zones()]
    for lid, (name, color, _) in L.items():     # glow underneath every line
        o.append(f'<path class="glow" data-line="{lid}" d="{rounded(line_points(lid))}" fill="none" stroke="{color}" '
                 f'stroke-width="{LW + 8}" opacity=".55" filter="url(#glow)"/>')
    for lid, (name, color, _) in L.items():
        o.append(f'<path id="L-{lid}" class="line" data-line="{lid}" d="{rounded(line_points(lid))}" fill="none" '
                 f'stroke="{color}" stroke-width="{LW}" stroke-linejoin="round"/>')
        o.append(f'<g class="cap" data-line="{lid}">{arrow(lid)}</g>')
        o.append(line_badge(lid))
    # the future: the aiub line past 'now' is still being built
    gx = S["grad"]["x"]
    o.append(f'<path d="M{NOW_X:.0f},{TY} L{gx + 80},{TY}" stroke="{BG}" stroke-width="{LW + 2}" stroke-dasharray="9 9"/>')
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
            '<div class="led"><span class="led1">yaqzan\'s metro</span></div>'
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
<title>yaqzan's metro</title>
<meta name="description" content="everything i have done since 2023, as a metro map. pick a stop and a train takes you there.">
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
      <p>left to right is time, from my first day at aiub in 2023 to graduating in 2027. every line leaves from that first day and branches off when that thread started.</p>
      <p>where two lines meet, one thing led to the other. pick a stop and a train takes you there.</p>
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
          <h1>yaqzan's metro</h1>
          <p>every line is one thread of what i've done since 2023. read it left to right, like time.</p>
        </div>
      </header>
      <div id="scroller">
        <svg id="map" viewBox="{vx} {vy} {vw} {vh}" role="img" aria-label="a metro map of yaqzan's projects, papers and activities since 2023">
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
  <p class="m-intro">every line is one thread, stops in the order they happened. pick a line, then tap a stop.</p>
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
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset=".2" stop-color="#fff" stop-opacity="0"/><stop offset=".28" stop-color="#fff" stop-opacity=".05"/><stop offset=".36" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <style>@keyframes b{{50%{{opacity:.1}}}}.blink{{animation:b 1.2s steps(1) infinite}}</style>
</defs>
<rect width="{TW}" height="{TH}" rx="10" fill="url(#alu)"/>
<g transform="translate({pad} {pad})">
  <rect width="{pw}" height="{ph:.0f}" fill="{BG}"/>
  <svg x="24" y="22" width="52" height="52" viewBox="-30 -30 60 60"><circle r="22" fill="none" stroke="#dc241f" stroke-width="9"/><rect x="-29" y="-6" width="58" height="12" fill="#0019a8"/></svg>
  <text x="92" y="50" font-family="{FONT}" font-size="34" font-weight="700" fill="{INK}" letter-spacing="-.5">yaqzan's metro</text>
  <text x="93" y="76" font-family="{FONT}" font-size="17" fill="{SOFT}">everything since 2023, left to right. click the map to ride it.</text>
  <g transform="translate({bx} 16)">
    <rect width="{bw}" height="64" rx="3" fill="#0b0b0b" stroke="#333" stroke-width="3"/>
    <rect x="6" y="6" width="{bw - 12}" height="52" fill="url(#unlit)"/>
    <g filter="url(#glow)"><g mask="url(#ledmask)" font-family="ui-monospace,Consolas,monospace" font-weight="800" fill="#ffb238">
      <text x="18" y="44" font-size="30">all lines</text>
      <text x="{bw - 18}" y="44" font-size="30" text-anchor="end" class="blink">now boarding</text>
    </g></g>
  </g>
  <line x1="0" y1="{head}" x2="{pw}" y2="{head}" stroke="#232938" stroke-width="2"/>
  <svg x="0" y="{head}" width="{pw}" height="{mh:.0f}" viewBox="{vx} {vy} {vw} {vh}">{body}</svg>
  <line x1="0" y1="{head + mh:.0f}" x2="{pw}" y2="{head + mh:.0f}" stroke="#232938" stroke-width="2"/>
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
