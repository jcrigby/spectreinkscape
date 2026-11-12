import math, sys, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("rp", here + "/readplay.py"); rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),(3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
dist = math.dist
def hexagon(k):
    a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); t0 = math.atan2(a[1]-c[1], a[0]-c[0])
    return [(c[0]+50*math.cos(t0+j*math.pi/3), c[1]+50*math.sin(t0+j*math.pi/3)) for j in range(6)]
anchors = [p for k in range(1, 15) for p in hexagon(k)]
def ideal(n, centre, ang):
    Rc = {6: 50.0, 3: 50/math.sqrt(3)}[n]
    return [(centre[0]+Rc*math.cos(ang+2*math.pi*j/n), centre[1]+Rc*math.sin(ang+2*math.pi*j/n)) for j in range(n)]
pieces = []
for oid, tag, pts in rp.load():
    if pts is None: continue
    pts = [(x-560, y) for x, y in pts]; n = len(pts); assert n in (3, 6), (oid, n)
    c = (sum(p[0] for p in pts)/n, sum(p[1] for p in pts)/n)
    # orientation: mean vertex angle modulo 360/n, rounded to the nearest 30 degrees
    step = 2*math.pi/n
    offs = [(math.atan2(p[1]-c[1], p[0]-c[0]) % step) for p in pts]
    sx = sum(math.cos(o*n) for o in offs); sy = sum(math.sin(o*n) for o in offs); mean = (math.atan2(sy, sx)/n) % step
    snapped = round(mean / (math.pi/6)) * (math.pi/6)
    pieces.append(dict(id=oid, n=n, raw=pts, c=c, ang=snapped, turn=math.degrees(mean - snapped), placed=None))
todo = list(pieces); rounds = 0
while todo:
    rounds += 1; best = None
    for pc in todo:
        shape = ideal(pc["n"], pc["c"], pc["ang"])
        cands = {}
        for v in shape:
            for a in anchors:
                if dist(v, a) < 9:
                    t = (round(a[0]-v[0], 3), round(a[1]-v[1], 3)); cands[t] = cands.get(t, 0)
        for t in cands:
            moved = [(v[0]+t[0], v[1]+t[1]) for v in shape]
            cands[t] = sum(1 for v in moved if any(dist(v, a) < 0.02 for a in anchors))
        if cands:
            t = max(cands, key=lambda t: (cands[t], -math.hypot(*t)))
            score = (cands[t], -math.hypot(*t))
            if best is None or score > best[0]: best = (score, pc, t)
    if best is None: break
    _, pc, t = best
    pc["placed"] = [(v[0]+t[0], v[1]+t[1]) for v in ideal(pc["n"], pc["c"], pc["ang"])]; pc["shift"] = math.hypot(*t); pc["matched"] = best[0][0]
    anchors += pc["placed"]; todo.remove(pc)
for pc in todo: pc["placed"] = ideal(pc["n"], pc["c"], pc["ang"]); pc["shift"] = 0.0; pc["matched"] = 0
if __name__ == "__main__":
    for pc in pieces:
        print("%-8s %-8s moved %.2f px, turned %.2f deg, %d of %d corners on existing corners%s" % (pc["id"], "hexagon" if pc["n"] == 6 else "triangle", pc["shift"], pc["turn"], pc["matched"], pc["n"], "" if pc["matched"] else "  <-- no anchor found"))
