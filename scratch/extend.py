import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
dist = lambda a, b: math.hypot(a[0]-b[0], a[1]-b[1])
def hexagon(k):                                           # k = hexagon number 1..14 -> centre, {hour: corner}
    a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); t0 = math.atan2(a[1]-c[1], a[0]-c[0]); out = {}
    for j in range(6):
        p = (c[0]+50*math.cos(t0+j*math.pi/3), c[1]+50*math.sin(t0+j*math.pi/3))
        out[round((90 - math.degrees(math.atan2(-(p[1]-c[1]), p[0]-c[0]))) / 30) % 12 or 12] = p
    return c, out
def inside_hex(p, k):
    c, cs = hexagon(k); pts = [cs[h] for h in sorted(cs)]
    sgn = None
    for i in range(6):
        a, b = pts[i], pts[(i+1) % 6]; cr = (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])
        if abs(cr) < 1e-6: continue
        if sgn is None: sgn = cr > 0
        elif (cr > 0) != sgn: return False
    return True
jobs = []
for k in (int(x) for x in sys.argv[1].split(",")):
    ck, K = hexagon(k); nb = None
    for j in ((k - 2) % 14 + 1, k % 14 + 1):               # neighbours round the tile
        cj, J = hexagon(j)
        shared = [(hk, hj) for hk, pk in K.items() for hj, pj in J.items() if dist(pk, pj) < 1e-6]
        if len(shared) != 1: continue
        hk, hj = shared[0]; S = K[hk]
        for hn, N in J.items():                             # neighbour's corner next to S that sits strictly inside hexagon k
            if abs(dist(N, S) - 50) < 1e-6 and inside_hex(N, k) and dist(N, ck) < 49:
                for ht, T in K.items():
                    d1, d2 = (N[0]-S[0], N[1]-S[1]), (T[0]-S[0], T[1]-S[1])
                    if abs(d1[0]*d2[1] - d1[1]*d2[0]) < 1e-6 and d1[0]*d2[0] + d1[1]*d2[1] > 0 and dist(T, S) > 51:
                        nb = (j, hk, hj, hn, ht, S, N, T)
    assert nb, k
    j, hk, hj, hn, ht, S, N, T = nb
    print("hexagon %2d: segment from %d,%d (= %d,%d) to %d,%d extended %.1f px to %d,%d" % (k, k, hk, j, hj, j, hn, dist(N, T), k, ht))
    jobs.append((k, N, T))
if len(sys.argv) > 2 and sys.argv[2] == "draw":
    for k, N, T in jobs:
        ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
        ink.act("object-set-attribute", "d,M %.4f %.4f L %.4f %.4f" % (*N, *T))
        ink.act("object-set-attribute", "style,fill:none;stroke:#e00000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round")
        ink.act("object-set-attribute", "id,ext%02d" % k); time.sleep(0.5)
    for lay in ("layer-corners", "layer-numbers"):
        ink.act("select-clear"); ink.act("select-by-id", lay); ink.act("selection-top")
    ink.act("select-clear")
