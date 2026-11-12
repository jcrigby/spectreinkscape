import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]

def inside(p):
    x, y = p; c = False
    for i in range(14):
        (x1, y1), (x2, y2) = Q[i], Q[(i+1) % 14]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c

BLACK = "fill:none;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round"
arcs = {}
for i in range(14):
    a, b = Q[i], Q[(i+1) % 14]
    m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    # sweep=1 bulges toward rot90(a-m) = (-(ay-my), ax-mx)
    bulge = (-(a[1]-m[1]), a[0]-m[0])
    probe = (m[0] + 0.1*bulge[0], m[1] + 0.1*bulge[1])
    sweep_in = 1 if inside(probe) else 0
    for side, sw in (("in", sweep_in), ("out", 1 - sweep_in)):
        arcs[(i, side)] = "M %.4f %.4f A 50 50 0 0 %d %.4f %.4f" % (*a, sw, *b)

if sys.argv[1] == "circles":
    for i in range(14):
        for side in ("out", "in"):
            ink.add = None
            ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
            ink.act("object-set-attribute", "d," + arcs[(i, side)])
            ink.act("object-set-attribute", "style," + BLACK)
            ink.act("object-set-attribute", "id,arc%02d%s" % (i, side))
        ink.act("select-clear")
elif sys.argv[1] == "red":
    ids = []
    for i in range(14):
        ident = "arc%02d%s" % (i, "out" if i % 2 == 0 else "in")
        ids.append(ident)
        ink.act("select-clear"); ink.act("select-by-id", ident)
        ink.act("object-set-property", "stroke,#e00000")
        time.sleep(0.25)
    ink.act("select-clear"); ink.act("select-by-id", ",".join(ids)); ink.act("selection-top"); ink.act("select-clear")
