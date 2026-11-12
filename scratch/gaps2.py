import math, numpy as np, sys
sys.argv = sys.argv[:1]
exec(open(__file__.replace("gaps2.py", "gaps.py")).read().split("B = {}")[0])
QUAD = [5, 6, 7, 8]
def place(src_ids, pair_src, pair_dst, third=None):
    s0, s1 = C[pair_src[0]-1], C[pair_src[1]-1]; d0, d1 = C[pair_dst[0]-1], C[pair_dst[1]-1]
    th = math.atan2(d1[1]-d0[1], d1[0]-d0[0]) - math.atan2(s1[1]-s0[1], s1[0]-s0[0])
    c, sn = math.cos(th), math.sin(th)
    dx, dy = xs - d0[0], ys - d0[1]
    u = c*dx + sn*dy + s0[0]; v = -sn*dx + c*dy + s0[1]
    fwd = lambda p: (d0[0] + c*(p[0]-s0[0]) - sn*(p[1]-s0[1]), d0[1] + sn*(p[0]-s0[0]) + c*(p[1]-s0[1]))
    err = dist(fwd(C[third[0]-1]), C[third[1]-1]) if third else 0
    return bay(u, v, src_ids), err, math.degrees(th) % 360, fwd
chamber = bay(xs, ys, QUAD)
print("4-sided gap (5,6,7,8): %.0f px^2" % area(chamber))
for label, ps, pd, third in (("at 2,3,4   (6,7,8 -> 2,3,4)", (6, 7), (2, 3), (8, 4)),
                             ("at 11,12,13 (5,6,7 -> 11,12,13)", (5, 6), (11, 12), (7, 13))):
    g, err, rot, fwd = place(QUAD, ps, pd, third)
    lost = QUAD[0] if ps == (6, 7) else QUAD[3]
    print("%s: turn %.0f deg, 3rd centre off %.2f px, piece %.0f px^2, over other pieces/circles %.1f px^2, outside tile %.1f px^2; the extra circle (%d) would sit at (%.1f, %.1f)"
          % (label, rot, err, area(g), area(g & in_any_disc(xs, ys, shrink=0.3)), area(g & ~tile), lost, *fwd(C[lost-1])))
    # how close does the piece come to any other circle?
    yy, xx = np.nonzero(g)
    px, py = xs[yy, xx], ys[yy, xx]
    near = sorted((float(np.min(np.hypot(px - C[k][0], py - C[k][1]))) - 50, k+1) for k in range(14))[:5]
    print("    nearest circles (clearance px, circle):", [("%.1f" % a, b) for a, b in near])
