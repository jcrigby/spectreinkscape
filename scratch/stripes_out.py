import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
R, N = 50.0, 9                       # 9 bands across the diameter: red, white, ... red

def new(ident, d, style):
    ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
    ink.act("object-set-attribute", "d," + d)
    ink.act("object-set-attribute", "style," + style)
    ink.act("object-set-attribute", "id," + ident)

for i in range(0, 14, 2):            # even edges: the red curve bulges outward
    a, b = Q[i], Q[(i+1) % 14]
    m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    e = ((b[0]-a[0])/100, (b[1]-a[1])/100)
    n = ((a[1]-m[1])/R, -(a[0]-m[0])/R)              # outward normal (sweep=0 side)
    pt = lambda u, v: "%.4f %.4f" % (m[0]+u*e[0]+v*n[0], m[1]+u*e[1]+v*n[1])
    h = lambda u: math.sqrt(max(R*R - u*u, 0))
    new("tile%02dbg" % i, "M %s A 50 50 0 0 0 %s Z" % (pt(-R, 0), pt(R, 0)),
        "fill:#ffffff;stroke:#e00000;stroke-width:1.5;stroke-linejoin:round")
    bands = []
    for k in range(0, N, 2):
        u1, u2 = -R + k*2*R/N, -R + (k+1)*2*R/N
        bands.append("M %s L %s L %s A 50 50 0 0 1 %s Z" % (pt(u1, 0), pt(u2, 0), pt(u2, h(u2)), pt(u1, h(u1))))
    new("tile%02d" % i, " ".join(bands), "fill:#e00000;stroke:none")
    time.sleep(0.3)
reds = ",".join("arc%02d%s" % (i, "out" if i % 2 == 0 else "in") for i in range(14))
ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top"); ink.act("select-clear")
