import math, numpy as np
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = np.array([(200+100*x, 350-100*y) for x, y in P])
C = (Q + np.roll(Q, -1, axis=0)) / 2
H = 0.2                                              # grid step in px
xs, ys = np.meshgrid(np.arange(60, 640, H), np.arange(60, 490, H))
def in_poly(x, y, V):
    c = np.zeros(x.shape, bool)
    for i in range(len(V)):
        (x1, y1), (x2, y2) = V[i], V[(i+1) % len(V)]
        if y1 == y2: continue
        c ^= ((y1 > y) != (y2 > y)) & (x < x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    return c
def in_any_disc(x, y, ids=range(1, 15), shrink=0.0):
    m = np.zeros(x.shape, bool)
    for k in ids: m |= (x - C[k-1][0])**2 + (y - C[k-1][1])**2 < (50 - shrink)**2
    return m
def bay(x, y, ids):
    return in_poly(x, y, [C[k-1] for k in ids]) & ~in_any_disc(x, y, ids)
dist = lambda a, b: float(np.hypot(*(np.array(a) - np.array(b))))
area = lambda m: m.sum() * H * H

tile = in_poly(xs, ys, Q)
free = tile & ~in_any_disc(xs, ys)
print("unfilled area inside the tile: %.0f px^2" % area(free))
print("narrow passages between non-adjacent circles (under 40 px):")
for i in range(14):
    for j in range(i+2, 14):
        if (i, j) == (0, 13): continue
        g = dist(C[i], C[j]) - 100
        if g < 40: print("  circles %d-%d: %.1f px" % (i+1, j+1, g))
B = {}
for ids in ([2,3,4], [5,6,7,8], [11,12,13]):
    b = bay(xs, ys, ids); B[tuple(ids)] = b
    sides = [dist(C[ids[k]-1], C[ids[(k+1) % len(ids)]-1]) for k in range(len(ids))]
    print("gap %s: area %.0f px^2; centre distances %s; part outside the tile or under another circle: %.1f px^2"
          % (ids, area(b), ["%.1f" % s for s in sides], area(b & ~free)))

def placed(src, dst, mirror):
    """Membership grid of gap `src` moved rigidly so centres src[0],src[1] land on dst[0],dst[1]."""
    s = np.array([C[k-1] for k in src]); d = np.array([C[k-1] for k in dst])
    if mirror: s = s * [-1, 1]
    th = math.atan2(*(d[1]-d[0])[::-1]) - math.atan2(*(s[1]-s[0])[::-1])
    c, sn = math.cos(th), math.sin(th)
    # inverse map target point -> source frame
    dx, dy = xs - d[0][0], ys - d[0][1]
    u = c*dx + sn*dy + s[0][0]; v = -sn*dx + c*dy + s[0][1]
    if mirror: u = -u
    third = d[0] + np.array([c*(s[2]-s[0])[0] - sn*(s[2]-s[0])[1], sn*(s[2]-s[0])[0] + c*(s[2]-s[0])[1]])
    return bay(u, v, src), dist(third, d[2]), math.degrees(th) % 360
print()
for label, src, dst, mir, tgt in (
        ("2,3,4 flipped over, placed in 11,12,13", [2,3,4], [13,12,11], True, (11,12,13)),
        ("2,3,4 not flipped, placed in 11,12,13 ", [2,3,4], [13,12,11], False, (11,12,13)),
        ("2,3,4 not flipped, placed at 6,7,8    ", [2,3,4], [6,7,8], False, (5,6,7,8)),
        ("2,3,4 flipped over, placed at 7,6,5   ", [2,3,4], [7,6,5], True, (5,6,7,8))):
    g, err, rot = placed(src, dst, mir)
    print("%s: 3rd centre off by %.2f px, turn %.0f deg, piece %.0f px^2, overlapping circles %.1f px^2, outside tile %.1f px^2, gap left over %.0f px^2"
          % (label, err, rot, area(g), area(g & in_any_disc(xs, ys, shrink=0.3)), area(g & ~tile), area(B[tgt] & ~g)))
g1, _, _ = placed([2,3,4], [6,7,8], False); g2, _, _ = placed([2,3,4], [7,6,5], True)
print("in 5,6,7,8 the two placements overlap each other by %.0f px^2" % area(g1 & g2))
