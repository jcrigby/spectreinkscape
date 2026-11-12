import math, sys, importlib.util, io, contextlib, numpy as np
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ce", here + "/centre.py"); ce = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(ce)
C, R, Q, dist = ce.C, ce.R, ce.Q, ce.dist
r3 = math.sqrt(3)/2
# --- push the half hpf round circle 8 until something stops it ---
c8 = C[8]
def h8_at(ang_deg):                                  # ang = direction of the cusp from circle 8's centre (screen degrees)
    a = math.radians(ang_deg); u = (math.cos(a), math.sin(a)); axis = (u[1], -u[0])
    if (C[6][0]-c8[0])*axis[0] + (C[6][1]-c8[1])*axis[1] < 0: axis = (-axis[0], -axis[1])
    return ce.half_hpf((c8[0]+R*u[0], c8[1]+R*u[1]), axis, c8, "h8")
xs, ys, A_ = ce.xs, ce.ys, ce.A_
D = ce.D
others = np.zeros(xs.shape, bool)
for j in C:
    if j != 8: others |= D(C[j], R-0.15)
for m in ce.existing.values(): others |= m
for p in ce.pieces:
    if p["name"] != "halfhpf08": others |= p["mask"]
cur = math.degrees(math.atan2(ce.h8["cusp"][1]-c8[1], ce.h8["cusp"][0]-c8[0]))
lo, hi = cur, cur - 40
for _ in range(22):
    mid = (lo+hi)/2
    if (h8_at(mid)["mask"] & others).sum()*A_ < 0.02: lo = mid
    else: hi = mid
push = round(cur - lo, 1); H8 = h8_at(cur - push)
def edge_clear(h, c):
    return abs((c[0]-h["cusp"][0])*(-h["axis"][1]) + (c[1]-h["cusp"][1])*h["axis"][0]) - R
pts8 = None
print("half hpf on 8 can turn a further %.1f deg round circle 8 (cusp at %.0f -> %.0f deg). Then: flat side to circle 5 %.2f px, to circle 4 %.2f px; cusp to long crescent's circle %.2f px; shoulder now %.1f px along circle 8 from the 8/9 corner"
      % (push, cur, cur-push, edge_clear(H8, C[5]), edge_clear(H8, C[4]), dist(H8["cusp"], ce.F5) - R, dist(H8["shoulder"], Q[8])))
OA = [p for p in ce.pieces if p["name"] == "varA0910"][0]["O"]; O8 = H8["O"]
print("dome centres: half hpf (%.1f, %.1f), A (%.1f, %.1f); gaps: dome-to-dome %.1f px, half-hpf dome to circle 9 %.1f px, A dome to circle 8 %.1f px" % (*O8, *OA, dist(O8, OA)-100, dist(O8, C[9])-100, dist(OA, c8)-100))
# --- the space between the pushed half hpf and the A ---
obs = np.zeros(xs.shape, bool)
for j in C: obs |= D(C[j], R-0.15)
for m in ce.existing.values(): obs |= m
for p in ce.pieces:
    if p["name"] != "halfhpf08": obs |= p["mask"]
obs |= H8["mask"]; obs |= ~ce.inpoly
def poly_mask(V):
    m = np.zeros(xs.shape, bool)
    for i in range(len(V)):
        (x1, y1), (x2, y2) = V[i], V[(i+1) % len(V)]
        if y1 != y2: m ^= ((y1 > ys) != (y2 > ys)) & (xs < x1 + (ys - y1) * (x2 - x1) / (y2 - y1))
    return m
bay = poly_mask([OA, C[9], c8, O8]) & ~obs
print("space between them (inside the four centres A-dome, circle 9, circle 8, half-hpf dome): %.0f px^2" % (bay.sum()*A_))
# --- candidate shapes as point sets in their own frames ---
def grid(test, lo=-115, hi=115, step=1.6):
    g = np.arange(lo, hi, step); X, Y = np.meshgrid(g, g); m = test(X, Y)
    return np.stack([X[m], Y[m]], 1), float(m.sum())*step*step
dd = lambda X, Y, c: (X-c[0])**2 + (Y-c[1])**2
m11, e11, n11 = ce.frame(11); c13 = C[13]
cut = ((c13[0]-m11[0])*e11[0]+(c13[1]-m11[1])*e11[1], (c13[0]-m11[0])*n11[0]+(c13[1]-m11[1])*n11[1])
s5 = [C[k] for k in (5, 6, 7, 8)]; sc = (sum(p[0] for p in s5)/4, sum(p[1] for p in s5)/4)
def star(X, Y):
    x, y = X + sc[0], Y + sc[1]; m = np.zeros(X.shape, bool)
    for i in range(4):
        (x1, y1), (x2, y2) = s5[i], s5[(i+1) % 4]
        if y1 != y2: m ^= ((y1 > y) != (y2 > y)) & (x < x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    for c in s5: m &= dd(x, y, c) >= 2500
    return m
SHAPES = {
    "fin":                 lambda X, Y: (X >= 0) & (X <= 50) & (Y >= 0) & (Y <= 50) & (dd(X, Y, (50, 50)) >= 2500),
    "short crescent":      lambda X, Y: (dd(X, Y, (50, 50)) <= 2500) & (dd(X, Y, (0, 0)) <= 2500) & (dd(X, Y, (75, 50*r3)) >= 2500),
    "star":                star,
    "long crescent":       lambda X, Y: (dd(X, Y, (50, 50)) <= 2500) & (dd(X, Y, (75, 50*r3)) >= 2500) & (dd(X, Y, cut) >= 2500),
    "long crescent, flipped": lambda X, Y: (dd(X, -Y, (50, 50)) <= 2500) & (dd(X, -Y, (75, 50*r3)) >= 2500) & (dd(X, -Y, cut) >= 2500),
    "half hpf":            lambda X, Y: (dd(X, Y, (0, 0)) <= 2500) & (dd(X, Y, (50, 50)) >= 2500) & (Y >= 0),
    "half hpf, flipped":   lambda X, Y: (dd(X, Y, (0, 0)) <= 2500) & (dd(X, Y, (50, -50)) >= 2500) & (Y <= 0),
    "hpf":                 lambda X, Y: (dd(X, Y, (0, 0)) <= 2500) & (dd(X, Y, (50, 50)) >= 2500) & (dd(X, Y, (50, -50)) >= 2500),
}
x0, y0, Hh = float(xs[0, 0]), float(ys[0, 0]), 0.25
bx, by = np.nonzero(bay.any(0))[0], np.nonzero(bay.any(1))[0]
X0, X1, Y0, Y1 = x0+bx[0]*Hh-40, x0+bx[-1]*Hh+40, y0+by[0]*Hh-40, y0+by[-1]*Hh+40
def evaluate(P, ox, oy, angles):
    best = None; nfree = 0
    for th in angles:
        c, s = math.cos(th), math.sin(th)
        px = c*P[:, 0] - s*P[:, 1]; py = s*P[:, 0] + c*P[:, 1]
        Xp = ox[:, None] + px[None, :]; Yp = oy[:, None] + py[None, :]
        ix = np.clip(((Xp-x0)/Hh).round().astype(int), 0, xs.shape[1]-1); iy = np.clip(((Yp-y0)/Hh).round().astype(int), 0, xs.shape[0]-1)
        ok = ~obs[iy, ix].any(1)
        if ok.any():
            nfree += int(ok.sum())
            inb = bay[iy[ok], ix[ok]].mean(1); k = int(np.argmax(inb))
            if best is None or inb[k] > best[0]: best = (float(inb[k]), float(ox[ok][k]), float(oy[ok][k]), th)
    return best, nfree
print("\nshape | area | fits anywhere near? | best placement: share of the piece lying in that space, share of the space it fills")
for name, test in SHAPES.items():
    P, area = grid(test)
    P = P - P.mean(0)
    ox, oy = np.meshgrid(np.arange(X0, X1, 2.0), np.arange(Y0, Y1, 2.0)); ox, oy = ox.ravel(), oy.ravel()
    best, nfree = evaluate(P, ox, oy, np.radians(np.arange(0, 360, 4.0)))
    if best is None: print("%-24s | %5.0f | no" % (name, area)); continue
    fx, fy = np.meshgrid(np.arange(best[1]-2, best[1]+2.01, 0.5), np.arange(best[2]-2, best[2]+2.01, 0.5))
    b2, _ = evaluate(P, fx.ravel(), fy.ravel(), best[3] + np.radians(np.arange(-4, 4.01, 1.0)))
    best = b2 or best
    print("%-24s | %5.0f | yes (%d clear placements) | %3.0f%% of piece in the space, fills %3.0f%% of it; centre (%.1f, %.1f), turned %.0f deg"
          % (name, area, nfree, 100*best[0], 100*best[0]*area/(bay.sum()*A_), best[1], best[2], math.degrees(best[3]) % 360))
