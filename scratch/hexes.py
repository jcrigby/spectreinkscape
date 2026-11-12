import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
def inside(p):
    c = False
    for i in range(14):
        (x1, y1), (x2, y2) = Q[i], Q[(i+1) % 14]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1]-y1)*(x2-x1)/(y2-y1): c = not c
    return c
BLACK = "fill:none;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round"
for i in range(14):
    a, b = Q[i], Q[(i+1) % 14]; m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    t0 = math.atan2(a[1]-m[1], a[0]-m[0])
    halves = {}
    for sgn in (1, -1):                                   # the two ways round from a to b
        v = [(m[0]+50*math.cos(t0+sgn*k*math.pi/3), m[1]+50*math.sin(t0+sgn*k*math.pi/3)) for k in (1, 2)]
        mid = ((v[0][0]+v[1][0])/2, (v[0][1]+v[1][1])/2)
        halves["in" if inside(((mid[0]+m[0])/2, (mid[1]+m[1])/2)) else "out"] = "M %.4f %.4f L %.4f %.4f L %.4f %.4f L %.4f %.4f" % (*a, *v[0], *v[1], *b)
    assert set(halves) == {"in", "out"}
    for side in ("out", "in"):
        ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
        ink.act("object-set-attribute", "d," + halves[side])
        ink.act("object-set-attribute", "style," + BLACK)
        ink.act("object-set-attribute", "id,hex%02d%s" % (i, side))
    ink.act("select-clear"); time.sleep(0.3)
