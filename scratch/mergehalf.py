import math, re, sys, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load()
half, tri = solid["chalf01"], solid["ccorn01"]
pts = sorted(set((round(x, 3), round(y, 3)) for x, y in half + tri))
def hullf(ps):
    def side(ps):
        h = []
        for p in ps:
            while len(h) >= 2 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(p[0]-h[-2][0]) <= 0.5: h.pop()
            h.append(p)
        return h
    lo, up = side(ps), side(ps[::-1]); return lo[:-1] + up[:-1]
H = hullf(pts)
gap = ap.area(H) - ap.area(half) - ap.area(tri)
print("half hexagon %.0f + triangle %.0f + space between %.0f = %.0f px^2; outline has %d corners and is convex (it is the hull of the two pieces)" % (ap.area(half), ap.area(tri), gap, ap.area(H), len(H)))
print("new piece:", ap.describe(H))
layer, defs = el["centre"], el["centre_defs"]
for k in ("chalf01", "ccorn01"):
    layer.remove(el[k]); layer.remove(el[k + "bg"]); defs.remove(el[k + "pat"]); solid.pop(k)
if sum(H[j][0]*H[(j+1) % len(H)][1] - H[(j+1) % len(H)][0]*H[j][1] for j in range(len(H))) < 0: H = H[::-1]
# start the outline on the long slanted side so the stripes run across it as they did on the half hexagon
k = max(range(len(H)), key=lambda j: (round(math.dist(H[j], H[(j+1) % len(H)]), 1) if abs((H[(j+1) % len(H)][1]-H[j][1])) > 1 and abs((H[(j+1) % len(H)][0]-H[j][0])) > 1 else 0))
H = H[k:] + H[:k]
cov = ap.add(tree, el, solid, notch, "cbig01", "#0a9396", H)
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
for p in H: print("   corner (%.1f, %.1f)" % p)
print("no overlaps; coverage %.1f%%" % cov)
