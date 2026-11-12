"""Generic: find placements of a polygon on the left tile with corners on existing corners."""
import math, re, sys, importlib.util, io, contextlib, itertools
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ft", here + "/filltri.py"); ft = importlib.util.module_from_spec(spec)
_argv = sys.argv; sys.argv = _argv[:1]
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(ft)
sys.argv = _argv
Q, dist, clip, area, uniq, el, tree = ft.Q, ft.dist, ft.clip, ft.area, ft.uniq, ft.el, ft.tree
blocked, notches = list(ft.blocked), ft.notches
for e in el["centre"]:                                   # pieces added after filltri.py was written
    i = e.get("id") or ""
    if re.fullmatch(r"(cscal|ctrap|cpc)\d\d", i): blocked.append(ft.nums(e.get("d")))
anchors = uniq(ft.anchors + [p for b in blocked for p in b])
def corner(k, hour):
    a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); th = math.radians(hour*30)
    p = (c[0]+50*math.sin(th), c[1]-50*math.cos(th)); assert any(dist(p, q) < 1e-6 for q in ft.hexagon(k)), (k, hour); return p
NAMES = {}
for k in range(1, 15):
    odd = k in (1, 2, 5, 6, 9, 10, 11, 12)
    for h in ((1, 3, 5, 7, 9, 11) if odd else (12, 2, 4, 6, 8, 10)):
        p = corner(k, h); NAMES.setdefault((round(p[0], 1), round(p[1], 1)), []).append("%d,%d" % (k, h))
def name(p): return "=".join(NAMES.get((round(p[0], 1), round(p[1], 1)), ["(%.1f, %.1f)" % p]))
def fits(poly, A):
    if clip(Q, poly) < A - 0.5: return False
    return all(clip(poly, b) < 0.5 for b in blocked + notches)
def placements(V, min_on=3):
    A = area(V); out = {}; n = len(V)
    for mirror in (False, True):
        W = [(-x, y) for x, y in V] if mirror else list(V)
        for i, j in itertools.permutations(range(n), 2):
            L = dist(W[i], W[j])
            if L < 15: continue
            for a in anchors:
                for b in anchors:
                    if abs(dist(a, b) - L) > 0.05: continue
                    th = math.atan2(b[1]-a[1], b[0]-a[0]) - math.atan2(W[j][1]-W[i][1], W[j][0]-W[i][0]); c, s = math.cos(th), math.sin(th)
                    poly = [(a[0] + c*(p[0]-W[i][0]) - s*(p[1]-W[i][1]), a[1] + s*(p[0]-W[i][0]) + c*(p[1]-W[i][1])) for p in W]
                    key = tuple(sorted((round(p[0], 1), round(p[1], 1)) for p in poly))
                    if key in out: continue
                    on = sum(1 for v in poly if any(dist(v, q) < 0.05 for q in anchors))
                    if on >= min_on and fits(poly, A): out[key] = dict(poly=poly, on=on, flipped=mirror, turn=round(math.degrees(th)) % 360)
    return list(out.values())
