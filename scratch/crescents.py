import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
R, N, COL = 50.0, 9, "#f59a00"
def frame(i):
    a, b = Q[i], Q[(i+1) % 14]
    m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    return m, ((b[0]-a[0])/100, (b[1]-a[1])/100), (-(a[1]-m[1])/R, (a[0]-m[0])/R)
C = [frame(i)[0] for i in range(14)]
def arc(p, q, c):
    """SVG arc command from p to q (radius 50, short way) around centre c."""
    dx, dy = q[0]-p[0], q[1]-p[1]
    sweep = 1 if (c[0]-p[0])*(-dy) + (c[1]-p[1])*dx > 0 else 0
    for z in (p, q): assert abs(math.hypot(z[0]-c[0], z[1]-c[1]) - R) < 1e-6, (z, c)
    return "A 50 50 0 0 %d %.4f %.4f" % (sweep, *q)
f = lambda p: "%.4f %.4f" % p
shapes = {}
for i in (2, 4, 6, 8, 10):                       # circles 3, 5, 7, 9, 11: end-side quarter
    m, e, n = frame(i)
    XY = lambda w, v: (m[0]+w*e[0]+v*n[0], m[1]+w*e[1]+v*n[1])
    F, cn = XY(R, R), C[(i+1) % 14]              # fin's arc centre; neighbouring circle's centre
    lw, lv = (cn[0]-m[0])*e[0]+(cn[1]-m[1])*e[1], (cn[0]-m[0])*n[0]+(cn[1]-m[1])*n[1]
    assert abs(lw-75) < 1e-6 and abs(lv-R*r3) < 1e-6, (lw, lv)
    g = lambda w: R - math.sqrt(max(R*R-(R-w)**2, 0))                 # top of fin
    top = lambda w: math.sqrt(max(R*R-w*w, 0)) if w <= 25 else lv - math.sqrt(max(R*R-(w-lw)**2, 0))
    T, B, Y = XY(0, R), XY(R, 0), XY(25, lv)
    bg = "M %s %s %s %s Z" % (f(T), arc(T, B, F), arc(B, Y, cn), arc(Y, T, m))
    pieces = []
    for k in range(0, N, 2):
        u1, u2 = max(-R + k*2*R/N, 0.0), min(-R + (k+1)*2*R/N, R)
        if u2 <= u1: continue
        for w1, w2 in ([(u1, u2)] if not (u1 < 25 < u2) else [(u1, 25.0), (25.0, u2)]):
            p1, p2, p3, p4 = XY(w1, g(w1)), XY(w2, g(w2)), XY(w2, top(w2)), XY(w1, top(w1))
            tc = m if w2 <= 25 else cn
            pieces.append("M %s %s L %s %s Z" % (f(p1), arc(p1, p2, F), f(p3), arc(p3, p4, tc)))
    # sampled check: crescent overlaps no other circle and no fin
    bad = tot = 0
    for sw in range(1, 100):
        for sv in range(1, 100):
            w, v = sw/2, sv/2
            if not (g(w) < v < top(w)): continue
            tot += 1; x, y = XY(w, v)
            if any(math.hypot(x-C[j][0], y-C[j][1]) < R - 1e-6 for j in range(14) if j != i) or w*w+v*v > R*R: bad += 1
    print("circle %2d crescent: area ~%.0f px^2, overlapping samples %d of %d" % (i+1, tot/4, bad, tot))
    shapes[i] = (bg, " ".join(pieces), XY(38, 20))

if len(sys.argv) > 1 and sys.argv[1] == "draw":
    def new(ident, d, style):
        ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
        ink.act("object-set-attribute", "d," + d)
        ink.act("object-set-attribute", "style," + style)
        ink.act("object-set-attribute", "id," + ident)
    for i, (bg, stripes, numpos) in shapes.items():
        new("cres%02dbg" % (i+1), bg, "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % COL)
        new("cres%02d" % (i+1), stripes, "fill:%s;stroke:none" % COL)
        if i in (4, 8, 10):                      # 5, 9, 11: number was sitting where the crescent goes
            ink.act("select-clear"); ink.act("select-by-id", "num%02d" % (i+1))
            ink.act("object-set-attribute", "x,%.2f" % numpos[0]); ink.act("object-set-attribute", "y,%.2f" % (numpos[1]+7))
        time.sleep(0.3)
    reds = ",".join("arc%02d%s" % (i, "out" if i % 2 == 0 else "in") for i in range(14))
    ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
    ink.act("select-clear"); ink.act("select-by-id", "layer-numbers"); ink.act("selection-top"); ink.act("select-clear")
