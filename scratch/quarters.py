import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
R, N = 50.0, 9
def frame(i):
    a, b = Q[i], Q[(i+1) % 14]
    m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    e = ((b[0]-a[0])/100, (b[1]-a[1])/100)
    n = (-(a[1]-m[1])/R, (a[0]-m[0])/R)            # inward normal
    return m, e, n
C = [frame(i)[0] for i in range(14)]

def overlap(i, side):
    """Fraction of inner quarter (side -1 = start end, +1 = finish end) of circle i lying inside any other circle."""
    m, e, n = frame(i); hit = tot = 0; who = set()
    for su in range(1, 50):
        for sv in range(1, 50):
            u, v = side*su, sv
            if u*u + v*v >= R*R: continue
            x, y = m[0]+u*e[0]+v*n[0], m[1]+u*e[1]+v*n[1]
            tot += 1
            js = [j for j in range(14) if j != i and (x-C[j][0])**2 + (y-C[j][1])**2 < R*R]
            if js: hit += 1; who.update(j+1 for j in js)
    return hit/tot, sorted(who)

free = {}
for i in range(0, 14, 2):
    for side in (-1, 1):
        f, who = overlap(i, side)
        print("circle %2d %s quarter: %4.1f%% overlapped by circles %s" % (i+1, "start" if side < 0 else "end  ", 100*f, who))
        if f == 0: free[i] = side
print("free:", {i+1: ("start" if s < 0 else "end") for i, s in free.items()})

if len(sys.argv) > 1 and sys.argv[1] == "draw":
    def new(ident, d, style):
        ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
        ink.act("object-set-attribute", "d," + d)
        ink.act("object-set-attribute", "style," + style)
        ink.act("object-set-attribute", "id," + ident)
    for i, side in sorted(free.items()):
        m, e, n = frame(i)
        pt = lambda u, v: "%.4f %.4f" % (m[0]+u*e[0]+v*n[0], m[1]+u*e[1]+v*n[1])
        h = lambda u: math.sqrt(max(R*R - u*u, 0))
        lo, hi = (-R, 0.0) if side < 0 else (0.0, R)
        if side < 0: bg = "M %s L %s A 50 50 0 0 1 %s Z" % (pt(0, 0), pt(-R, 0), pt(0, R))
        else:        bg = "M %s L %s A 50 50 0 0 1 %s Z" % (pt(0, 0), pt(0, R), pt(R, 0))
        new("quart%02dbg" % (i+1), bg, "fill:#ffffff;stroke:#e00000;stroke-width:1.5;stroke-linejoin:round")
        bands = []
        for k in range(0, N, 2):
            u1, u2 = max(-R + k*2*R/N, lo), min(-R + (k+1)*2*R/N, hi)
            if u2 <= u1: continue
            bands.append("M %s L %s L %s A 50 50 0 0 0 %s Z" % (pt(u1, 0), pt(u2, 0), pt(u2, h(u2)), pt(u1, h(u1))))
        new("quart%02d" % (i+1), " ".join(bands), "fill:#e00000;stroke:none")
        # move the number into the quarter that stays empty
        x, y = m[0] - side*22*e[0] + 22*n[0], m[1] - side*22*e[1] + 22*n[1] + 7
        ink.act("select-clear"); ink.act("select-by-id", "num%02d" % (i+1))
        ink.act("object-set-attribute", "x,%.2f" % x); ink.act("object-set-attribute", "y,%.2f" % y)
        time.sleep(0.3)
    reds = ",".join("arc%02d%s" % (i, "out" if i % 2 == 0 else "in") for i in range(14))
    ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top"); ink.act("select-clear")
