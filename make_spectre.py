#!/usr/bin/env python3
"""Build the Spectre mosaic from scratch.

Running this writes two pictures next to the script (or into the folder given as argument):

  spectre-shapes.svg   the four base shapes and one Spectre tile built from them
  spectre-patch.svg    71 tiles of the Spectre tiling, each filled with the same pieces

It needs only the Python standard library. Before writing anything it checks that no two
pieces overlap, that every piece lies inside the tile, and that the patch has 71 tiles.

Coordinates in this file are in tile units: the Spectre has 14 edges of length 1, y points up.
"""
import colorsys, math, os, sys

R3 = math.sqrt(3) / 2

# The 14 corners of the straight-sided Spectre.
SPECTRE = [(0, 0), (1, 0), (1.5, -R3), (1.5 + R3, .5 - R3), (1.5 + R3, 1.5 - R3), (2.5 + R3, 1.5 - R3),
           (3 + R3, 1.5), (3, 2), (3 - R3, 1.5), (2.5 - R3, 1.5 + R3), (1.5 - R3, 1.5 + R3),
           (.5 - R3, 1.5 + R3), (-R3, 1.5), (0, 1)]

# The pieces that fill one tile. They were placed by hand and by search in Inkscape, so they
# are data, not the result of a rule. Each piece is listed by its corners.
PIECES = {
    "triangle": [
        ((0.13398, 2.36603), (-0.36602, 2.36603), (-0.11602, 2.79904)),
        ((-0.11602, 2.79904), (0.38398, 2.79904), (0.13398, 2.36603)),
        ((0.63398, 2.36603), (0.13398, 2.36603), (0.38398, 2.79904)),
        ((0.38398, 1.93301), (0.88398, 1.93301), (0.63398, 2.36603)),
        ((-0.36602, 2.36603), (0.13398, 2.36603), (-0.11602, 1.93301)),
        ((0.38398, 1.93301), (-0.11602, 1.93301), (0.13398, 2.36603)),
        ((0.13398, 2.36603), (0.63398, 2.36603), (0.38398, 1.93301)),
        ((1.88398, 1.93301), (1.38398, 1.93301), (1.63398, 2.36603)),
        ((1.63398, 2.36603), (2.13398, 2.36603), (1.88398, 1.93301)),
        ((2.38398, 1.93301), (1.88398, 1.93301), (2.13398, 2.36603)),
        ((3.43301, 2.25000), (3.00000, 2.00000), (3.43301, 1.75000)),
        ((3.43301, 1.75000), (3.86602, 2.00000), (3.43301, 2.25000)),
        ((3.43301, 1.75000), (3.00000, 2.00000), (3.00000, 1.50000)),
        ((3.86602, 2.00000), (3.43301, 1.75000), (3.86602, 1.50000)),
        ((0.13398, 1.50000), (-0.36602, 1.50000), (-0.11602, 1.93301)),
        ((-0.11602, 1.93301), (0.38398, 1.93301), (0.13398, 1.50000)),
        ((0.13398, 1.50000), (0.63398, 1.50000), (0.38398, 1.93301)),
        ((0.38398, 1.93301), (0.88398, 1.93301), (0.63398, 1.50000)),
        ((0.63398, 1.50000), (1.13398, 1.50000), (0.88398, 1.93301)),
        ((0.88398, 1.93301), (1.38398, 1.93301), (1.13398, 1.50000)),
        ((1.13398, 1.50000), (1.63398, 1.50000), (1.38398, 1.93301)),
        ((1.38398, 1.93301), (1.88398, 1.93301), (1.63398, 1.50000)),
        ((2.13398, 1.50000), (1.63398, 1.50000), (1.88398, 1.93301)),
        ((1.88398, 1.93301), (2.38398, 1.93301), (2.13398, 1.50000)),
        ((-0.86602, 1.00000), (-0.43301, 1.25000), (-0.86602, 1.50000)),
        ((-0.43301, 1.25000), (0.00000, 1.00000), (0.00000, 1.50000)),
        ((0.43301, 1.25000), (0.00000, 1.50000), (0.00000, 1.00000)),
        ((0.86602, 1.00000), (0.43301, 1.25000), (0.86602, 1.50000)),
        ((0.86602, 1.50000), (1.29904, 1.25000), (0.86602, 1.00000)),
        ((1.38398, 1.06699), (1.88398, 1.06699), (1.63398, 1.50000)),
        ((1.63398, 1.50000), (2.13398, 1.50000), (1.88398, 1.06699)),
        ((-0.43301, 1.25000), (-0.86602, 1.00000), (-0.43301, 0.75000)),
        ((-0.43301, 0.75000), (0.00000, 1.00000), (-0.43301, 1.25000)),
        ((0.00000, 1.00000), (0.43301, 0.75000), (0.43301, 1.25000)),
        ((0.43301, 1.25000), (0.86602, 1.00000), (0.43301, 0.75000)),
        ((1.29904, 0.75000), (0.86602, 1.00000), (1.29904, 1.25000)),
        ((2.36602, 0.63397), (2.36602, 1.13398), (1.93301, 0.88397)),
        ((1.29904, 1.06699), (1.29904, 0.56699), (1.73205, 0.81699)),
        ((2.86602, 0.63397), (2.36602, 0.63397), (2.61602, 1.06699)),
        ((2.61602, 1.06699), (3.11602, 1.06699), (2.86602, 0.63397)),
        ((3.36602, 0.63397), (2.86602, 0.63397), (3.11602, 1.06699)),
        ((0.43301, 0.75000), (0.86602, 1.00000), (0.86602, 0.50000)),
        ((1.29904, 0.75000), (0.86602, 0.50000), (0.86602, 1.00000)),
        ((1.50000, 0.63397), (1.93301, 0.88397), (1.93301, 0.38397)),
        ((2.36602, 0.63397), (1.93301, 0.88397), (1.93301, 0.38397)),
        ((0.86603, 0.50000), (0.43301, 0.75000), (0.43301, 0.25000)),
        ((1.50000, 0.13397), (1.93301, 0.38397), (1.50000, 0.63397)),
        ((2.36602, 0.63397), (2.86602, 0.63397), (2.61602, 0.20096)),
        ((3.11602, 0.20096), (2.61602, 0.20096), (2.86602, 0.63397)),
        ((2.86602, 0.63397), (3.36602, 0.63397), (3.11602, 0.20096)),
        ((0.50000, 0.00000), (1.00000, 0.00000), (0.75000, 0.43301)),
        ((1.25000, 0.43301), (0.75000, 0.43301), (1.00000, 0.00000)),
        ((1.00000, 0.00000), (1.50000, 0.00000), (1.25000, 0.43301)),
        ((1.50000, 0.13397), (1.93301, 0.38397), (1.93301, -0.11603)),
        ((0.50000, 0.00000), (0.00000, 0.00000), (0.25000, -0.43301)),
        ((0.25000, -0.43301), (0.75000, -0.43301), (0.50000, 0.00000)),
        ((1.00000, 0.00000), (0.50000, 0.00000), (0.75000, -0.43301)),
        ((2.36602, -0.36603), (1.93301, -0.11603), (1.93301, -0.61603)),
        ((1.93301, -0.61603), (2.36602, -0.86603), (2.36602, -0.36603)),
        ((1.50000, -0.86603), (1.93301, -1.11603), (1.93301, -0.61603)),
        ((2.36602, -0.86603), (1.93301, -0.61603), (1.93301, -1.11603)),
    ],
    "half": [
        ((3.00000, 1.50000), (3.43301, 1.50000), (3.43301, 1.75000)),
        ((3.86602, 1.50000), (3.43301, 1.50000), (3.43301, 1.75000)),
        ((-0.86602, 1.50000), (-0.43301, 1.50000), (-0.43301, 1.25000)),
        ((0.00000, 1.50000), (-0.43301, 1.50000), (-0.43301, 1.25000)),
        ((0.43301, 1.50000), (0.43301, 1.25000), (-0.00000, 1.50000)),
        ((0.43301, 1.50000), (0.43301, 1.25000), (0.86602, 1.50000)),
        ((1.29904, 1.50000), (1.29904, 1.25000), (0.86602, 1.50000)),
        ((1.29904, 1.50000), (1.54904, 1.50000), (1.29904, 1.06699)),
        ((2.13398, 1.06699), (1.88398, 1.06699), (2.13398, 1.50000)),
        ((2.13398, 1.25000), (2.56699, 1.25000), (2.13398, 1.50000)),
        ((3.00000, 1.50000), (2.62500, 1.28349), (2.75000, 1.06699)),
        ((3.00000, 1.06699), (2.75000, 1.06699), (3.00000, 1.50000)),
        ((3.11602, 1.50000), (3.36602, 1.50000), (3.11602, 1.06699)),
        ((2.58253, 1.00898), (2.36602, 1.13398), (2.36602, 0.63397)),
        ((1.73205, 1.06699), (1.73205, 0.81699), (1.29904, 1.06699)),
        ((1.73205, 1.06699), (1.73205, 0.81699), (2.16506, 1.06699)),
        ((1.25000, 0.43301), (1.25000, 0.68301), (0.81699, 0.43301)),
        ((1.28349, 0.37500), (1.50000, 0.50000), (1.50000, 0.00000)),
        ((0.75000, 0.43301), (0.37500, 0.21651), (0.50000, 0.00000)),
        ((0.50000, 0.00000), (0.00000, 0.00000), (0.37500, 0.21651)),
        ((1.87500, -0.21651), (1.75000, -0.43301), (1.50000, 0.00000)),
        ((1.71651, -0.49103), (1.93301, -0.61603), (1.93301, -0.11603)),
        ((1.93301, -0.61603), (1.50000, -0.86603), (1.71651, -0.49103)),
    ],
    "small": [
        ((3.10825, 1.43750), (3.00000, 1.50000), (3.00000, 1.25000)),
        ((3.00770, 1.22100), (3.11595, 1.15850), (3.11595, 1.40850)),
        ((2.38285, 1.25450), (2.27459, 1.19200), (2.49110, 1.06700)),
        ((2.13390, 1.25000), (2.13390, 1.12500), (2.35041, 1.25000)),
        ((2.22770, 1.18360), (2.33595, 1.12110), (2.11945, 0.99610)),
        ((1.50001, 0.55800), (1.50001, 0.68300), (1.28350, 0.55800)),
        ((1.39175, 0.56250), (1.50000, 0.50000), (1.28349, 0.37500)),
        ((1.60825, -0.06250), (1.71650, 0.00000), (1.49999, 0.12500)),
        ((1.82480, -0.17850), (1.93305, -0.11600), (1.71655, 0.00900)),
        ((1.71650, 0.00000), (1.60825, -0.06250), (1.82475, -0.18750)),
    ],
    "trapezoid": [
        ((2.62500, 1.28350), (2.75000, 1.06699), (2.50000, 1.06699), (2.43750, 1.17525)),
    ],
}

NAMES = {"triangle": "Triangle", "half": "Half triangle", "small": "Small triangle", "trapezoid": "Trapezoid"}
COLOURS = {"triangle": "#4a7fe0", "half": "#f5a03a", "small": "#12a5a8", "trapezoid": "#9b59d0"}
H = R3 / 2   # height of the side-1/2 triangle
BASE = {"triangle": [(0, 0), (.5, 0), (.25, H)],
        "half": [(0, 0), (.25, 0), (0, H)],
        "small": [(0, 0), (.125, 0), (0, H / 2)],
        "trapezoid": [(0, 0), (.25, 0), (.125, H / 2), (0, H / 2)]}
NOTES = {"triangle": ("equilateral, side 1/2", "60° 60° 60°"),
         "half": ("sides 1/4, √3/4, 1/2", "30° 60° 90°  (triangle cut down the middle)"),
         "small": ("sides 1/8, √3/8, 1/4", "30° 60° 90°  (top half of the half triangle)"),
         "trapezoid": ("parallel sides 1/4 and 1/8, height √3/8, slant 1/4", "90° 90° 120° 60°  (bottom half of the half triangle)")}


# ---------- geometry ----------

def area(p):
    return abs(sum(p[k][0] * p[(k + 1) % len(p)][1] - p[(k + 1) % len(p)][0] * p[k][1] for k in range(len(p)))) / 2


def ccw(p):
    s = sum(p[k][0] * p[(k + 1) % len(p)][1] - p[(k + 1) % len(p)][0] * p[k][1] for k in range(len(p)))
    return list(p) if s > 0 else list(p)[::-1]


def overlap(subject, convex):
    """Area shared by a polygon and a convex polygon (Sutherland-Hodgman clipping)."""
    out, c = ccw(subject), ccw(convex)
    for k in range(len(c)):
        a, b = c[k], c[(k + 1) % len(c)]
        side = lambda q: (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            sp, sq = side(p), side(q)
            if sp >= 0:
                out.append(p)
            if (sp > 0 and sq < 0) or (sp < 0 and sq > 0):
                t = sp / (sp - sq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        if len(out) < 3:
            return 0.0
    return area(out)


def inside(poly, p):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1] - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def hexagon_outline():
    """The tile outline: a regular hexagon sits on every edge (the edge is its long diagonal).
    Going round, edges alternately take the half that bulges out and the half that cuts in.
    Also returns the seven cut-in halves (the notches)."""
    out, notches = [], []
    for i in range(14):
        a, b = SPECTRE[i], SPECTRE[(i + 1) % 14]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        t0 = math.atan2(a[1] - m[1], a[0] - m[0])
        for sgn in (1, -1):
            v = [(m[0] + .5 * math.cos(t0 + sgn * k * math.pi / 3), m[1] + .5 * math.sin(t0 + sgn * k * math.pi / 3)) for k in (1, 2)]
            probe = (m[0] + .25 * ((v[0][0] + v[1][0]) / 2 - m[0]), m[1] + .25 * ((v[0][1] + v[1][1]) / 2 - m[1]))
            if inside(SPECTRE, probe) == (i % 2 == 1):
                out += [a, v[0], v[1]]
                if i % 2 == 1:
                    notches.append([a, v[0], v[1], b])
    assert len(out) == 42 and len(notches) == 7
    return out, notches


# ---------- the Spectre tiling by substitution ----------
# A transform is (a, b, tx, c, d, ty):  x' = a x + b y + tx,  y' = c x + d y + ty.

IDENT = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)


def mul(t, u):
    a, b, tx, c, d, ty = t; A, B, TX, C, D, TY = u
    return (a * A + b * C, a * B + b * D, a * TX + b * TY + tx, c * A + d * C, c * B + d * D, c * TX + d * TY + ty)


def rot(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (c, -s, 0.0, s, c, 0.0)


def shift(x, y):
    return (1.0, 0.0, x, 0.0, 1.0, y)


def ap(t, p):
    return (t[0] * p[0] + t[1] * p[1] + t[2], t[3] * p[0] + t[4] * p[1] + t[5])


QUAD = [SPECTRE[k] for k in (3, 5, 7, 11)]
LABELS = ["Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Phi", "Psi"]
RULES = {"Gamma": ("Pi", "Delta", None, "Theta", "Sigma", "Xi", "Phi", "Gamma"),
         "Delta": ("Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
         "Theta": ("Psi", "Delta", "Pi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
         "Lambda": ("Psi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
         "Xi": ("Psi", "Delta", "Pi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
         "Pi": ("Psi", "Delta", "Xi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
         "Sigma": ("Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Lambda", "Gamma"),
         "Phi": ("Psi", "Delta", "Psi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
         "Psi": ("Psi", "Delta", "Psi", "Phi", "Sigma", "Psi", "Phi", "Gamma")}


def tiling(levels=2, root="Delta"):
    """Transforms of the tiles in a patch. A cluster is (list of (child, transform), quad);
    a single tile is (None, quad)."""
    tiles = {n: (None, QUAD) for n in LABELS}
    tiles["Gamma"] = ([((None, QUAD), IDENT), ((None, QUAD), mul(shift(*SPECTRE[8]), rot(30)))], QUAD)
    for _ in range(levels):
        quad = tiles["Delta"][1]
        total, r, trs = 0, IDENT, [IDENT]
        for ang, f, t in ((60, 3, 1), (0, 2, 0), (60, 3, 1), (60, 3, 1), (0, 2, 0), (60, 3, 1), (-120, 3, 3)):
            if ang:
                total += ang; r = rot(total)
            a, b = ap(trs[-1], quad[f]), ap(r, quad[t])
            trs.append(mul(shift(a[0] - b[0], a[1] - b[1]), r))
        flip = (-1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        trs = [mul(flip, t) for t in trs]
        sq = [ap(trs[6], quad[2]), ap(trs[5], quad[1]), ap(trs[3], quad[2]), ap(trs[0], quad[1])]
        tiles = {lab: ([(tiles[s], t) for s, t in zip(subs, trs) if s], sq) for lab, subs in RULES.items()}
    out = []

    def flat(node, t):
        if node[0] is None:
            out.append(t)
        else:
            for child, u in node[0]:
                flat(child, mul(t, u))

    flat(tiles[root], IDENT)
    return out


# ---------- checks ----------

def check(outline, notches):
    pieces = [(k, p) for k, ps in PIECES.items() for p in ps]
    worst = 0.0
    for i, (_, p) in enumerate(pieces):
        for _, q in pieces[i + 1:]:
            worst = max(worst, overlap(p, q))
        for n in notches:
            worst = max(worst, overlap(p, n))
        c = (sum(x for x, _ in p) / len(p), sum(y for _, y in p) / len(p))
        assert inside(outline, c), "a piece lies outside the tile"
    assert worst < 1e-4, "pieces overlap by %.6f" % worst
    covered = sum(area(p) for _, p in pieces) / area(outline)
    assert covered <= 1 + 1e-9
    return len(pieces), covered


# ---------- drawing ----------

def path(points, to):
    return "M " + " L ".join("%.3f %.3f" % to(p) for p in points) + " Z"


def shapes_sheet(outline, count, covered):
    px = 100.0                     # pixels per tile edge for the tile on the right
    ox, oy = 455 + 200, 95 + 350   # where the tile's first corner goes
    to = lambda p: (ox + px * p[0], oy - px * p[1])
    o = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="640" viewBox="0 0 1100 640">',
         '<rect x="0" y="0" width="1100" height="640" style="fill:#ffffff"/>',
         '<g style="font-family:sans-serif;fill:#222222">',
         '<text x="40" y="48" style="font-size:26px;font-weight:bold">A Spectre tile from four shapes</text>',
         '<text x="40" y="72" style="font-size:13px;fill:#555555">Lengths are in tile edges (the Spectre has 14 edges of length 1). '
         'The tile outline has a regular hexagon on every edge.</text>']
    y = 190
    for k in PIECES:
        o.append('<text x="170" y="%d" style="font-size:18px;font-weight:bold">%s  × %d</text>' % (y - 58, NAMES[k], len(PIECES[k])))
        o.append('<text x="170" y="%d" style="font-size:13px">%s</text>' % (y - 36, NOTES[k][0]))
        o.append('<text x="170" y="%d" style="font-size:13px;fill:#555555">%s</text>' % (y - 17, NOTES[k][1]))
        big = lambda p, y=y: (45 + 200 * p[0], y - 200 * p[1])
        o.append('<path d="%s" style="fill:%s;stroke:#222222;stroke-width:1.5;stroke-linejoin:round"/>' % (path(BASE[k], big), COLOURS[k]))
        y += 118
    o.append('<text x="575" y="610" style="font-size:14px">%d pieces cover %.1f%% of the tile; the pale slivers are still open.</text>' % (count, 100 * covered))
    o.append('</g>')
    o.append('<path d="%s" style="fill:#e9e9e9;stroke:none"/>' % path(outline, to))
    for k, ps in PIECES.items():
        for p in ps:
            o.append('<path d="%s" style="fill:%s;stroke:#ffffff;stroke-width:1;stroke-linejoin:round"/>' % (path(p, to), COLOURS[k]))
    o.append('<path d="%s" style="fill:none;stroke:#222222;stroke-width:3;stroke-linejoin:round"/>' % path(outline, to))
    o.append('</svg>')
    return "\n".join(o) + "\n"


def patch_picture(outline, tiles, width=1210.0, margin=15.0):
    pts = [ap(t, p) for t in tiles for p in outline]
    x0, x1 = min(x for x, _ in pts), max(x for x, _ in pts)
    y0, y1 = min(y for _, y in pts), max(y for _, y in pts)
    s = (width - 2 * margin) / (x1 - x0)
    height = s * (y1 - y0) + 2 * margin
    units = lambda poly: "M " + " L ".join("%.5f %.5f" % q for q in poly) + " Z"
    o = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.2f %.2f">' % (width, height, width, height),
         '<rect x="0" y="0" width="%.2f" height="%.2f" style="fill:#ffffff"/>' % (width, height),
         '<defs><g id="tile">',
         '<path d="%s"/>' % units(outline)]      # filled with the tile's tint
    for k, ps in PIECES.items():
        for p in ps:
            o.append('<path d="%s" style="fill:%s;stroke:#ffffff;stroke-width:0.02;stroke-linejoin:round"/>'
                     % (units(p), COLOURS[k]))
    o.append('<path d="%s" style="fill:none"/>' % units(outline))   # the outline, drawn on top
    o.append('</g></defs>')
    for a, b, tx, c, d, ty in tiles:
        turn = round(math.degrees(math.atan2(c, a)) / 30) % 12     # tint each tile by its orientation
        r, g, bl = colorsys.hls_to_rgb(turn / 12.0, 0.84, 0.62)
        o.append('<use href="#tile" transform="matrix(%.6f %.6f %.6f %.6f %.4f %.4f)" '
                 'style="fill:#%02x%02x%02x;stroke:#b00000;stroke-width:%.4f;stroke-linejoin:round"/>'
                 % (s * a, -s * c, s * b, -s * d, margin + s * (tx - x0), margin + s * (y1 - ty),
                    int(r * 255), int(g * 255), int(bl * 255), 1.6 / s))
    o.append('</svg>')
    return "\n".join(o) + "\n"


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    outline, notches = hexagon_outline()
    count, covered = check(outline, notches)
    tiles = tiling(2)
    assert len(tiles) == 71, len(tiles)
    assert all(abs(t[0] * t[4] - t[1] * t[3] - 1) < 1e-9 for t in tiles), "a tile is mirrored"
    for name, text in (("spectre-shapes.svg", shapes_sheet(outline, count, covered)),
                       ("spectre-patch.svg", patch_picture(outline, tiles))):
        with open(os.path.join(folder, name), "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote", os.path.join(folder, name))
    print("%d pieces per tile (%s), no overlaps, %.1f%% of the tile covered; %d tiles in the patch"
          % (count, ", ".join("%d %s" % (len(v), k) for k, v in PIECES.items()), 100 * covered, len(tiles)))


if __name__ == "__main__":
    main()
