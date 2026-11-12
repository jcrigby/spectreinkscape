import math, sys, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load()
at = lambda c, h: (c[0]+50*math.sin(math.radians(h*30)), c[1]-50*math.cos(math.radians(h*30)))
cen = lambda p: (sum(q[0] for q in p)/len(p), sum(q[1] for q in p)/len(p))
c15 = cen(solid["chex01"]); c16 = (ap.corner(4, 10)[0], ap.corner(4, 10)[1] - 50); half = solid["chalf01"]
# gap between 16, 9 and 15
gapB = [at(c15, 3), ap.corner(8, 8), at(c15, 5)]
col = lambda a, b, c: abs((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])) < 1e-6
print("8,8 / 16,12 / 16,10 / 15,5 in one straight line:", col(ap.corner(8, 8), at(c16, 12), at(c16, 10)) and col(ap.corner(8, 8), at(c16, 12), at(c15, 5)))
print("triangle 15,3 / 8,8 / 15,5:", ap.describe(gapB))
# gap between the half hexagon, 15 and the blue row: the same triangle mirrored about 15's upright axis
gapA = [(2*c15[0]-p[0], p[1]) for p in gapB]
blue = [p for k, v in solid.items() if k.startswith("ctri") for p in v]
print("mirror image on the other side of 15: corners", [("%.1f" % p[0], "%.1f" % p[1]) for p in gapA], "| first corner is a blue-triangle corner:", any(math.dist(gapA[1], q) < 0.05 for q in blue), "| others are 15,9 and 15,7:", math.dist(gapA[0], at(c15, 9)) < 1e-6, math.dist(gapA[2], at(c15, 7)) < 1e-6)
whole = [ap.corner(13, 2), at(c15, 9), at(c15, 7), max(half, key=lambda p: p[0])]
print("whole gap on that side (13,2 / 15,9 / 15,7 / half hexagon's far corner): area %.0f; the triangle takes %.0f, leaving %.0f as a sliver along the half hexagon (%.1f px wide)" % (ap.area(whole), ap.area(gapA), ap.area(whole) - ap.area(gapA),
      abs((half[0][0]-half[3][0])*(gapA[1][1]-half[3][1]) - (half[0][1]-half[3][1])*(gapA[1][0]-half[3][0])) / math.dist(half[0], half[3])))
ap.add(tree, el, solid, notch, "ccorn01", "#c79a00", [gapA[1], gapA[0], gapA[2]])
cov = ap.add(tree, el, solid, notch, "ccorn02", "#c79a00", [gapB[1], gapB[0], gapB[2]])
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("both drawn, no overlaps; coverage %.1f%%" % cov)
