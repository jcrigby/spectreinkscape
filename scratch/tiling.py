"""Build a patch of the real Spectre tiling by substitution, then test the hexagon-edged tile in it."""
import math, sys, numpy as np
r3 = math.sqrt(3)/2
PTS = np.array([(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
                (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)], float)
QUAD = PTS[[3, 5, 7, 11]]
I3 = np.eye(3)
def trot(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def ttrans(x, y): return np.array([[1, 0, x], [0, 1, y], [0, 0, 1.0]])
def ap(T, p): return (T @ np.array([p[0], p[1], 1.0]))[:2]
class Tile:
    def __init__(self, label): self.label, self.quad = label, QUAD
    def flat(self, T, out): out.append((self.label, T))
class Meta:
    def __init__(self, tiles, trs, quad): self.tiles, self.trs, self.quad = tiles, trs, quad
    def flat(self, T, out):
        for t, tr in zip(self.tiles, self.trs): t.flat(T @ tr, out)
NAMES = ["Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Phi", "Psi"]
def base():
    t = {n: Tile(n) for n in NAMES if n != "Gamma"}
    t["Gamma"] = Meta([Tile("Gamma1"), Tile("Gamma2")], [I3.copy(), ttrans(*PTS[8]) @ trot(30)], QUAD)
    return t
RULES = {"Gamma": ("Pi", "Delta", None, "Theta", "Sigma", "Xi", "Phi", "Gamma"),
         "Delta": ("Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
         "Theta": ("Psi", "Delta", "Pi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
         "Lambda": ("Psi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
         "Xi": ("Psi", "Delta", "Pi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
         "Pi": ("Psi", "Delta", "Xi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
         "Sigma": ("Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Lambda", "Gamma"),
         "Phi": ("Psi", "Delta", "Psi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
         "Psi": ("Psi", "Delta", "Psi", "Phi", "Sigma", "Psi", "Phi", "Gamma")}
def supers(tiles):
    quad = tiles["Delta"].quad; total = 0; rot = I3.copy(); trs = [I3.copy()]
    for ang, f, t in ((60, 3, 1), (0, 2, 0), (60, 3, 1), (60, 3, 1), (0, 2, 0), (60, 3, 1), (-120, 3, 3)):
        if ang: total += ang; rot = trot(total)
        a, b = ap(trs[-1], quad[f]), ap(rot, quad[t])
        trs.append(ttrans(a[0]-b[0], a[1]-b[1]) @ rot)
    Rf = np.diag([-1.0, 1.0, 1.0]); trs = [Rf @ T for T in trs]
    sq = np.array([ap(trs[6], quad[2]), ap(trs[5], quad[1]), ap(trs[3], quad[2]), ap(trs[0], quad[1])])
    return {lab: Meta([tiles[s] for s in subs if s], [T for s, T in zip(subs, trs) if s], sq) for lab, subs in RULES.items()}
def patch(level, root="Delta"):
    t = base()
    for _ in range(level): t = supers(t)
    out = []; t[root].flat(I3.copy(), out); return out

def hex_outline():
    """Edge i (0-based): even -> outward half hexagon, odd -> inward, as in the drawing."""
    def inside(p):
        c = False
        for i in range(14):
            (x1, y1), (x2, y2) = PTS[i], PTS[(i+1) % 14]
            if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1]-y1)*(x2-x1)/(y2-y1): c = not c
        return c
    out = []
    for i in range(14):
        a, b = PTS[i], PTS[(i+1) % 14]; m = (a+b)/2; t0 = math.atan2(a[1]-m[1], a[0]-m[0])
        for sgn in (1, -1):
            v = [m + 0.5*np.array([math.cos(t0+sgn*k*math.pi/3), math.sin(t0+sgn*k*math.pi/3)]) for k in (1, 2)]
            if inside(m + 0.25*((v[0]+v[1])/2 - m)) == (i % 2 == 1): out += [a, v[0], v[1]]
    assert len(out) == 42
    return np.array(out)
def poly_area(p): return abs(np.sum(p[:, 0]*np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1)*p[:, 1])) / 2
def raster_cover(polys, h):
    allp = np.vstack(polys); lo, hi = allp.min(0) - 0.1, allp.max(0) + 0.1
    nx, ny = int((hi[0]-lo[0])/h)+1, int((hi[1]-lo[1])/h)+1
    cover = np.zeros((ny, nx), np.int16)
    for p in polys:
        pl, ph = p.min(0), p.max(0)
        i0, i1 = max(int((pl[0]-lo[0])/h), 0), min(int((ph[0]-lo[0])/h)+2, nx); j0, j1 = max(int((pl[1]-lo[1])/h), 0), min(int((ph[1]-lo[1])/h)+2, ny)
        X, Y = np.meshgrid(lo[0] + (np.arange(i0, i1)+0.5)*h, lo[1] + (np.arange(j0, j1)+0.5)*h)
        c = np.zeros(X.shape, bool)
        for k in range(len(p)):
            (x1, y1), (x2, y2) = p[k], p[(k+1) % len(p)]
            if y1 == y2: continue
            c ^= ((y1 > Y) != (y2 > Y)) & (X < x1 + (Y - y1) * (x2 - x1) / (y2 - y1))
        cover[j0:j1, i0:i1] += c
    return cover
if __name__ == "__main__":
    level = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    tiles = patch(level); n = len(tiles)
    plain = [np.array([ap(T, p) for p in PTS]) for _, T in tiles]
    H = hex_outline(); hexed = [np.array([ap(T, p) for p in H]) for _, T in tiles]
    h = 0.02
    print("level %d patch: %d tiles; plain tile area %.4f, hexagon-edged tile area %.4f" % (level, n, poly_area(PTS), poly_area(H)))
    for name, polys in (("plain straight-sided", plain), ("hexagon-edged", hexed)):
        cov = raster_cover(polys, h)
        print("  %-20s covered area %.1f (sum of tiles %.1f); doubly-covered area %.3f; max layers %d"
              % (name, (cov > 0).sum()*h*h, sum(poly_area(p) for p in polys), (cov > 1).sum()*h*h, cov.max()))
    # holes: cells not covered but surrounded (flood fill from the border)
    for name, polys in (("plain straight-sided", plain), ("hexagon-edged", hexed)):
        cov = raster_cover(polys, h) > 0
        from collections import deque
        ny, nx = cov.shape; seen = np.zeros(cov.shape, bool); dq = deque()
        for i in range(nx):
            for j in (0, ny-1):
                if not cov[j, i] and not seen[j, i]: seen[j, i] = True; dq.append((j, i))
        for j in range(ny):
            for i in (0, nx-1):
                if not cov[j, i] and not seen[j, i]: seen[j, i] = True; dq.append((j, i))
        while dq:
            j, i = dq.popleft()
            for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = j+dj, i+di
                if 0 <= a < ny and 0 <= b < nx and not cov[a, b] and not seen[a, b]: seen[a, b] = True; dq.append((a, b))
        print("  %-20s enclosed uncovered area (holes) %.3f" % (name, (~cov & ~seen).sum()*h*h))
    # which edge meets which
    key = lambda p: (round(p[0], 4), round(p[1], 4)); edges = {}
    for ti, p in enumerate(plain):
        for i in range(14): edges[(key(p[i]), key(p[(i+1) % 14]))] = (ti, i)
    same = opp = 0
    for (a, b), (ti, i) in edges.items():
        if (b, a) in edges:
            tj, j = edges[(b, a)]
            if ti < tj:
                if (i + j) % 2: opp += 1
                else: same += 1
    print("  shared edges: %d pair an outward edge with an inward edge, %d pair like with like" % (opp, same))
    dets = {round(float(np.linalg.det(T[:2, :2])), 3) for _, T in tiles}
    print("  handedness of all tiles (determinants):", dets)
