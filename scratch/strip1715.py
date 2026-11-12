import math, sys, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load()
at = lambda c, h: (c[0]+50*math.sin(math.radians(h*30)), c[1]-50*math.cos(math.radians(h*30)))
cen = lambda p: (sum(q[0] for q in p)/len(p), sum(q[1] for q in p)/len(p))
c15, c17 = cen(solid["chex01"]), cen(solid["chex03"])
poly = [at(c15, 7), at(c15, 5), at(c17, 1), at(c17, 11)]
print("strip 15,7 / 15,5 / 17,1 / 17,11:", ap.describe(poly))
def hand(p):                       # +1 / -1: which way the short side leans from the long side at the 60-degree corner
    n = len(p)
    for i in range(n):
        a, b, c = p[i], p[(i+1) % n], p[i-1]
        ang = math.degrees(math.acos(((b[0]-a[0])*(c[0]-a[0]) + (b[1]-a[1])*(c[1]-a[1])) / (math.dist(a, b)*math.dist(a, c))))
        if abs(ang - 60) < 0.5:
            lng, sht = (b, c) if math.dist(a, b) > math.dist(a, c) else (c, b)
            return 1 if (lng[0]-a[0])*(sht[1]-a[1]) - (lng[1]-a[1])*(sht[0]-a[0]) > 0 else -1
print("hand of this strip %+d; hand of the strip between 16 and 8 %+d" % (hand(poly), hand(solid["cpara01"])))
cov = ap.add(tree, el, solid, notch, "cpara02", "#f08a00", poly)
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("no overlaps; coverage %.1f%%" % cov)
c16 = (ap.corner(4, 10)[0], ap.corner(4, 10)[1] - 50)
r = [at(c15, 5), at(c16, 10), at(c17, 1)]; print("leftover at the right end (15,5 / 16,10 / 17,1): area %.0f" % ap.area(r))
half = solid["chalf01"]; far = max(half, key=lambda p: p[0])
l = [at(c15, 7), at(c17, 11), far]; print("leftover at the left end (15,7 / 17,11 / half hexagon's corner (%.1f, %.1f)): area %.0f" % (*far, ap.area(l)))
