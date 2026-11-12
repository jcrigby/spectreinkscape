import math, numpy as np
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = np.array([(200+100*x, 350-100*y) for x, y in P])
C = {k+1: tuple((Q[k] + Q[(k+1) % 14]) / 2) for k in range(14)}
R, H = 50.0, 0.25
dist = lambda a, b: math.hypot(a[0]-b[0], a[1]-b[1])
def in_poly(x, y):
    c = np.zeros(x.shape, bool)
    for i in range(14):
        (x1, y1), (x2, y2) = Q[i], Q[(i+1) % 14]
        if y1 == y2: continue
        c ^= ((y1 > y) != (y2 > y)) & (x < x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    return c
disc = lambda x, y, c, r=R: (x-c[0])**2 + (y-c[1])**2 < r*r
def site(a, b):
    ca, cb = C[a], C[b]; d = dist(ca, cb); mid = ((ca[0]+cb[0])/2, (ca[1]+cb[1])/2)
    h = math.sqrt(max(R*R - d*d/4, 0)); px, py = -(cb[1]-ca[1])/d, (cb[0]-ca[0])/d
    best = None
    for sgn in (1, -1):
        apex = (mid[0]+sgn*h*px, mid[1]+sgn*h*py); axis = (sgn*px, sgn*py)
        if h < 1e-6:                                   # tangent circles: point the piece into the tile
            axis = (px, py) if in_poly(np.array([mid[0]+5*px]), np.array([mid[1]+5*py]))[0] else (-px, -py)
        probe = (apex[0]+3*axis[0], apex[1]+3*axis[1])
        free = in_poly(np.array([probe[0]]), np.array([probe[1]]))[0] and all(dist(probe, C[j]) > R for j in C)
        if free: best = (apex, axis)
    apex, axis = best
    O = (apex[0]+R*axis[0], apex[1]+R*axis[1])
    perp = (-axis[1], axis[0])
    xs, ys = np.meshgrid(np.arange(O[0]-R-1, O[0]+R+1, H), np.arange(O[1]-R-1, O[1]+R+1, H))
    dome = disc(xs, ys, O)
    exact = dome & ~disc(xs, ys, ca) & ~disc(xs, ys, cb)
    n1 = (apex[0]+R*perp[0], apex[1]+R*perp[1]); n2 = (apex[0]-R*perp[0], apex[1]-R*perp[1])
    hpf = dome & ~disc(xs, ys, n1) & ~disc(xs, ys, n2)
    tile = in_poly(xs, ys)
    def clash(m, skip):
        out = {}
        for j in C:
            if j in skip: continue
            v = (m & disc(xs, ys, C[j], R - 0.3)).sum() * H * H
            if v > 0.5: out[j] = round(float(v))
        return out
    ar = lambda m: float(m.sum()) * H * H
    gamma = math.degrees(2*math.asin(min(d/2/R, 1)))            # angle between the two radii at the apex
    return dict(pair=(a, b), d=d, opening=180-gamma, apex=apex, centre=O,
                exact_area=ar(exact), exact_clash=clash(exact, (a, b)), exact_outside=ar(exact & ~tile),
                hpf_area=ar(hpf), hpf_clash=clash(hpf, ()), hpf_outside=ar(hpf & ~tile), hpf_gap=ar(exact & ~hpf),
                nearest=sorted((round(dist(O, C[j]) - 2*R, 1), j) for j in C if j not in (a, b))[:3])
for pr in ((1, 2), (4, 5), (8, 9), (9, 10), (10, 11), (13, 14)):
    s = site(*pr)
    print("%-6s centres %.1f apart, opening %3.0f deg | piece centre (%.1f, %.1f)" % ("%d,%d" % s["pair"], s["d"], s["opening"], *s["centre"]))
    print("       exact-fit variant: %.0f px^2, clashes %s, outside tile %.0f | standard hpf: %.0f px^2, clashes %s, outside tile %.0f, gaps beside it %.0f"
          % (s["exact_area"], s["exact_clash"] or "none", s["exact_outside"], s["hpf_area"], s["hpf_clash"] or "none", s["hpf_outside"], s["hpf_gap"]))
    print("       clearance from piece's circle to nearest other circles (px, circle; negative = overlap):", s["nearest"])

print("\n--- do the exact-fit pieces collide with each other, or with pieces already drawn? ---")
xs, ys = np.meshgrid(np.arange(60, 640, 0.5), np.arange(40, 480, 0.5)); A = 0.25
S_ = {pr: site(*pr) for pr in ((1, 2), (4, 5), (8, 9), (9, 10), (10, 11), (13, 14))}
piece = {pr: disc(xs, ys, s["centre"]) & ~disc(xs, ys, C[pr[0]]) & ~disc(xs, ys, C[pr[1]]) for pr, s in S_.items()}
keys = list(piece)
for i in range(len(keys)):
    for j in range(i+1, len(keys)):
        v = (piece[keys[i]] & piece[keys[j]]).sum() * A
        if v > 1: print("  %s and %s overlap by %.0f px^2 (centres %.1f apart)" % (keys[i], keys[j], v, dist(S_[keys[i]]["centre"], S_[keys[j]]["centre"])))
def tri(ids):
    m = np.zeros(xs.shape, bool); V = [C[k] for k in ids]
    for i in range(len(V)):
        (x1, y1), (x2, y2) = V[i], V[(i+1) % len(V)]
        if y1 != y2: m ^= ((y1 > ys) != (y2 > ys)) & (xs < x1 + (ys - y1) * (x2 - x1) / (y2 - y1))
    return m
def moved_star(src_pair, dst_pair):
    s0, s1, d0, d1 = C[src_pair[0]], C[src_pair[1]], C[dst_pair[0]], C[dst_pair[1]]
    th = math.atan2(d1[1]-d0[1], d1[0]-d0[0]) - math.atan2(s1[1]-s0[1], s1[0]-s0[0]); c, sn = math.cos(th), math.sin(th)
    dx, dy = xs - d0[0], ys - d0[1]; u = c*dx + sn*dy + s0[0]; v = -sn*dx + c*dy + s0[1]
    m = np.zeros(xs.shape, bool); V = [C[k] for k in (5, 6, 7, 8)]
    for i in range(4):
        (x1, y1), (x2, y2) = V[i], V[(i+1) % 4]
        if y1 != y2: m ^= ((y1 > v) != (y2 > v)) & (u < x1 + (v - y1) * (x2 - x1) / (y2 - y1))
    for k in (5, 6, 7, 8): m &= ~disc(u, v, C[k])
    return m
stars = {"star at 2-3-4": moved_star((6, 7), (2, 3)), "star at 5-6-7-8": moved_star((5, 6), (5, 6)), "star at 11-12-13": moved_star((5, 6), (11, 12))}
def frame(k):
    a, b = Q[k-1], Q[k % 14]; m = C[k]
    return m, ((b[0]-a[0])/100, (b[1]-a[1])/100), (-(a[1]-m[1])/R, (a[0]-m[0])/R)
def longc(k):
    m, e, n = frame(k); F = (m[0]+R*e[0]+R*n[0], m[1]+R*e[1]+R*n[1])
    return disc(xs, ys, F) & ~disc(xs, ys, C[k+1]) & ~disc(xs, ys, C[k+2]) & ~(disc(xs, ys, m) & ~(((xs-m[0])*e[0]+(ys-m[1])*e[1] > 0) & ((xs-m[0])*n[0]+(ys-m[1])*n[1] > 0)))
longs = {"long crescent at 5-6-7": longc(5), "long crescent at 11-12-13": longc(11)}
for pr in keys:
    hits = ["%s %.0f" % (nm, (piece[pr] & m).sum() * A) for nm, m in {**stars, **longs}.items() if (piece[pr] & m).sum() * A > 1]
    print("  piece at %s vs drawn pieces: %s" % (pr, ", ".join(hits) or "no overlap"))
both = piece[(4, 5)] & piece[(8, 9)]
alld = np.zeros(xs.shape, bool)
for j in C: alld |= disc(xs, ys, C[j])
print("  4,5 and 8,9: shared part clear of all circles %.0f px^2" % ((both & ~alld).sum() * A))
free = np.zeros(xs.shape, bool)
for i in range(14):
    (x1, y1), (x2, y2) = Q[i], Q[(i+1) % 14]
    if y1 != y2: free ^= ((y1 > ys) != (y2 > ys)) & (xs < x1 + (ys - y1) * (x2 - x1) / (y2 - y1))
free &= ~alld
u = np.zeros(xs.shape, bool)
for pr in keys: u |= piece[pr]
print("  open middle of the tile: %.0f px^2; covered by the six pieces together: %.0f px^2; left uncovered: %.0f px^2" % (free.sum()*A, (u & free).sum()*A, (free & ~u).sum()*A))
