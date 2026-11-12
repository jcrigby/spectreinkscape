import math, sys, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load()
at = lambda c, h: (c[0]+50*math.sin(math.radians(h*30)), c[1]-50*math.cos(math.radians(h*30)))
c16 = (ap.corner(4, 10)[0], ap.corner(4, 10)[1] - 50)
D, E, C, B = ap.corner(5, 9), at(c16, 2), ap.corner(5, 11), ap.corner(8, 6)
assert math.dist(D, at(c16, 4)) < 1e-6
pocket = [D, E, B, C]
print("pocket 5,9=16,4 / 16,2 / 8,6 / 5,11:", ap.describe(pocket))
rh = [D, E, (E[0]+C[0]-D[0], E[1]+C[1]-D[1]), C]
hits = {k: round(ap.clip(rh, v)) for k, v in {**solid, **notch}.items() if ap.clip(rh, v) > 0.5}
print("true rhombus on 16's side 2-4 and 5's side 9-11:", ap.describe(rh), "| overlaps", hits)
cov = ap.add(tree, el, solid, notch, "cdiam01", "#d63a8c", pocket)
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("pocket piece drawn, no overlaps; coverage %.1f%%" % cov)
