import math, subprocess, sys, time
r3 = math.sqrt(3) / 2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
U, OX, OY = 100, 200, 350
Q = [(OX + U*x, OY - U*y) for x, y in P]          # SVG coords (y down)
PROJ = "."

def act(name, arg=None):
    param = "[<'%s'>]" % arg if arg is not None else "[]"
    subprocess.run(["gdbus","call","--session","--dest","org.inkscape.Inkscape",
        "--object-path","/org/inkscape/Inkscape","--method","org.gtk.Actions.Activate",
        name, param, "{}"], check=True, stdout=subprocess.DEVNULL)

def vee(k):                                        # k = 1..7 -> (start, middle, end)
    return Q[2*k-2], Q[2*k-1], Q[(2*k) % 14]

def bis(k):
    a, m, b = vee(k)
    return math.degrees(math.atan2(a[1]+b[1]-2*m[1], a[0]+b[0]-2*m[0]))

def step(k):
    if k == 1:
        a, m, b = vee(1)
        d = "M %.4f %.4f L %.4f %.4f L %.4f %.4f" % (*a, *m, *b)
        open(PROJ + "/spectre.svg", "w").write(
f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="700" height="550" viewBox="0 0 700 550">
  <path id="v1" d="{d}" style="fill:none;stroke:#000000;stroke-width:4;stroke-linecap:round;stroke-linejoin:round"/>
</svg>
''')
        act("file-open-window", PROJ + "/spectre.svg")
        return
    m1, mk = vee(1)[1], vee(k)[1]
    th = round((bis(k) - bis(1)) % 360)
    dx, dy = mk[0]-m1[0], mk[1]-m1[1]
    # check: transformed base V lands on the target V
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    got = sorted((round(m1[0]+c*(x-m1[0])-s*(y-m1[1])+dx, 2), round(m1[1]+s*(x-m1[0])+c*(y-m1[1])+dy, 2)) for x, y in vee(1))
    want = sorted((round(x, 2), round(y, 2)) for x, y in vee(k))
    assert got == want, (got, want)
    rot = "rotate(%d %.4f %.4f)" % (th, *m1)
    act("select-clear"); act("select-by-id", "v1"); act("duplicate"); time.sleep(1.0)
    act("object-set-attribute", "transform," + rot); time.sleep(1.0)
    act("object-set-attribute", "transform,translate(%.4f %.4f) %s" % (dx, dy, rot)); time.sleep(0.5)
    act("select-clear")
    print("step", k, "rotate", th, "move", round(dx, 2), round(dy, 2))

def snap():
    act("export-type", "png"); act("export-area-page"); act("export-filename", PROJ + "/preview.png"); act("export-do")

if sys.argv[1] == "check":
    for k in range(2, 8): 
        m1 = vee(1)[1]; print(k, round((bis(k)-bis(1)) % 360))
elif sys.argv[1] == "snap": snap()
else: step(int(sys.argv[1]))
