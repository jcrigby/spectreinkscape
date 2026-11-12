import math, sys, importlib.util, io, contextlib, numpy as np
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ft", here + "/filltri.py"); ft = importlib.util.module_from_spec(spec)
sys.argv = sys.argv[:1]
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(ft)
H = 0.5
xs, ys = np.meshgrid(np.arange(80, 620, H), np.arange(60, 470, H))
def pm(V):
    m = np.zeros(xs.shape, bool)
    for i in range(len(V)):
        (x1, y1), (x2, y2) = V[i], V[(i+1) % len(V)]
        if y1 != y2: m ^= ((y1 > ys) != (y2 > ys)) & (xs < x1 + (ys - y1) * (x2 - x1) / (y2 - y1))
    return m
gap = pm(ft.Q)
for b in ft.blocked + ft.notches: gap &= ~pm(b)
print("open area inside the tile: %.0f px^2" % (gap.sum()*H*H))
# connected regions
lab = np.zeros(gap.shape, int); n = 0; regions = []
ny, nx = gap.shape
for j0, i0 in zip(*np.nonzero(gap)):
    if lab[j0, i0]: continue
    n += 1; stack = [(j0, i0)]; lab[j0, i0] = n; cells = []
    while stack:
        j, i = stack.pop(); cells.append((j, i))
        for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = j+dj, i+di
            if 0 <= a < ny and 0 <= b < nx and gap[a, b] and not lab[a, b]: lab[a, b] = n; stack.append((a, b))
    cells = np.array(cells); regions.append((len(cells)*H*H, xs[0, cells[:, 1]].mean(), ys[cells[:, 0], 0].mean(), np.ptp(cells[:, 1])*H, np.ptp(cells[:, 0])*H, n))
regions.sort(reverse=True)
# widest disc that fits in each region (distance to the nearest non-gap cell), brute force on a coarse sample
from math import hypot
solid = ~gap
sy, sx = np.nonzero(solid[::2, ::2]); sy, sx = sy*2, sx*2
print("regions bigger than 20 px^2 (area, centre, bounding box, widest inscribed circle):")
for a, cx, cy, w, h, k in regions:
    if a < 20: continue
    jj, ii = np.nonzero(lab == k); best = 0
    step = max(1, len(jj)//400)
    for j, i in zip(jj[::step], ii[::step]):
        d = np.min((sy - j)**2 + (sx - i)**2) ** 0.5 * H
        best = max(best, d)
    print("  %6.0f px^2 at (%.0f, %.0f), box %.0f x %.0f, inscribed circle diameter ~%.0f px" % (a, cx, cy, w, h, 2*best))
# can a 50px equilateral triangle sit anywhere, at any of the four lattice orientations?
found = 0
for ang in (0, 30, 60, 90):
    V = [(50/math.sqrt(3)*math.cos(math.radians(ang + 120*j)), 50/math.sqrt(3)*math.sin(math.radians(ang + 120*j))) for j in range(3)]
    pts = []
    for j in range(3):
        a, b = V[j], V[(j+1) % 3]
        for t in np.linspace(0, 1, 12, endpoint=False): pts.append((0.96*(a[0]+t*(b[0]-a[0])), 0.96*(a[1]+t*(b[1]-a[1]))))
    pts.append((0, 0))
    ok = np.ones(gap.shape, bool)
    for dx, dy in pts:
        sh = np.zeros(gap.shape, bool); di, dj = int(round(dx/H)), int(round(dy/H))
        src = gap[max(dj, 0):ny+min(dj, 0), max(di, 0):nx+min(di, 0)]
        sh[max(-dj, 0):ny+min(-dj, 0), max(-di, 0):nx+min(-di, 0)] = src
        ok &= sh
    found += int(ok.sum())
    if ok.any():
        j, i = np.argwhere(ok)[0]; print("  a triangle turned %d deg fits with its centre near (%.0f, %.0f) (%d grid positions)" % (ang, xs[0, i], ys[j, 0], ok.sum()))
print("triangle placements found:", found)

def placements(side, ang, shrink=0.96):
    Rc = side/math.sqrt(3)
    V = [(Rc*math.cos(math.radians(ang + 120*j)), Rc*math.sin(math.radians(ang + 120*j))) for j in range(3)]
    pts = [(0, 0)]
    for j in range(3):
        a, b = V[j], V[(j+1) % 3]
        for t in np.linspace(0, 1, 12, endpoint=False): pts.append((shrink*(a[0]+t*(b[0]-a[0])), shrink*(a[1]+t*(b[1]-a[1]))))
    ok = np.ones(gap.shape, bool)
    for dx, dy in pts:
        sh = np.zeros(gap.shape, bool); di, dj = int(round(dx/H)), int(round(dy/H))
        sh[max(-dj, 0):ny+min(-dj, 0), max(-di, 0):nx+min(-di, 0)] = gap[max(dj, 0):ny+min(dj, 0), max(di, 0):nx+min(di, 0)]
        ok &= sh
    return ok
print("\n50px triangle at any angle (5-degree steps):", {a: int(placements(50, a).sum()) for a in range(0, 120, 5) if placements(50, a).any()} or "fits nowhere")
for side in (43.3, 40, 36.6, 30, 25):
    res = {a: int(placements(side, a).sum()) for a in (0, 30, 60, 90)}
    print("triangle of side %.1f px: grid positions that fit by orientation %s" % (side, res))
# widths of the gaps: how the open area splits by local width
