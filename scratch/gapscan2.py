import math, sys, importlib.util, io, contextlib, numpy as np
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("gs", here + "/gapscan.py"); gs = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(gs)
gap, H, ny, nx, xs, ys = gs.gap, gs.H, gs.ny, gs.nx, gs.xs, gs.ys
def fits(V, shrink=0.96):
    c = (sum(p[0] for p in V)/len(V), sum(p[1] for p in V)/len(V)); pts = [(0.0, 0.0)]
    for j in range(len(V)):
        a, b = V[j], V[(j+1) % len(V)]
        for t in np.linspace(0, 1, 14, endpoint=False): pts.append((shrink*(a[0]+t*(b[0]-a[0])-c[0]), shrink*(a[1]+t*(b[1]-a[1])-c[1])))
    ok = np.ones(gap.shape, bool)
    for dx, dy in pts:
        sh = np.zeros(gap.shape, bool); di, dj = int(round(dx/H)), int(round(dy/H))
        sh[max(-dj, 0):ny+min(-dj, 0), max(-di, 0):nx+min(-di, 0)] = gap[max(dj, 0):ny+min(dj, 0), max(di, 0):nx+min(di, 0)]
        ok &= sh
    return ok
rot = lambda V, a: [(x*math.cos(math.radians(a)) - y*math.sin(math.radians(a)), x*math.sin(math.radians(a)) + y*math.cos(math.radians(a))) for x, y in V]
shapes = {"corner triangle 50-50-86.6 (cut off a 5/6 hex), 1083 px^2": [(0, 0), (86.6025, 0), (43.30127, 25)],
          "right triangle 50-86.6-100 (half of a 5/6 hex's triangle... the htri), 2165 px^2": [(0, 0), (86.6025, 0), (0, 50)],
          "thin rhombus side 50, 30-degree corners, 1250 px^2": [(0, 0), (50, 0), (50+43.30127, 25), (43.30127, 25)],
          "small right triangle 25-43.3-50 (half an equilateral), 541 px^2": [(0, 0), (43.30127, 0), (0, 25)],
          "square 36.6 px, 1340 px^2": [(0, 0), (36.6025, 0), (36.6025, 36.6025), (0, 36.6025)]}
for name, V in shapes.items():
    res = {a: int(fits(rot(V, a)).sum()) for a in range(0, 360, 30)}
    res = {a: n for a, n in res.items() if n}
    print("%s: %s" % (name, ("fits, orientations with room: %s" % res) if res else "fits nowhere"))
