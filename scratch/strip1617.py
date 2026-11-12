import math, sys, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load()
p16 = solid["cfive01"]; h17 = solid["chex03"]; c17 = (sum(p[0] for p in h17)/6, sum(p[1] for p in h17)/6)
at = lambda c, h: (c[0]+50*math.sin(math.radians(h*30)), c[1]-50*math.cos(math.radians(h*30)))
c16 = (ap.corner(4, 10)[0], ap.corner(4, 10)[1] - 50)
poly = [at(c16, 10), at(c16, 6), at(c17, 3), at(c17, 1)]
print("strip 16,10 / 16,6 / 17,3 / 17,1:", ap.describe(poly))
w = abs((poly[1][0]-poly[0][0])*(poly[3][1]-poly[0][1]) - (poly[1][1]-poly[0][1])*(poly[3][0]-poly[0][0])) / math.dist(poly[0], poly[1])
print("width between 16's cut edge and 17's side: %.1f px" % w)
cov = ap.add(tree, el, solid, notch, "cstrip01", "#f08a00", poly)
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("no overlaps; coverage %.1f%%" % cov)
