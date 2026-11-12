import math, sys, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("sf", here + "/shapefit.py"); sf = importlib.util.module_from_spec(spec); spec.loader.exec_module(sf)
dist, corner, name = sf.dist, sf.corner, sf.name
V = [corner(8, 4), corner(5, 1), corner(5, 11), corner(8, 6)]
sides = [dist(V[i], V[(i+1) % 4]) for i in range(4)]
ang = []
for i in range(4):
    a, b, c = V[i], V[(i+1) % 4], V[i-1]
    ang.append(math.degrees(math.acos(((b[0]-a[0])*(c[0]-a[0]) + (b[1]-a[1])*(c[1]-a[1])) / (dist(a, b)*dist(a, c)))))
print("your trapezoid: corners", [("%.1f" % p[0], "%.1f" % p[1]) for p in V]); print("  sides %s, angles %s, area %.0f px^2" % (["%.2f" % s for s in sides], ["%.0f" % a for a in ang], sf.area(V)))
print("  fits as given:", sf.fits(V, sf.area(V)), "| overlaps:", {i: round(sf.clip(V, b)) for i, b in enumerate(sf.blocked + sf.notches) if sf.clip(V, b) > 0.5} or "none")
found = sf.placements(V, min_on=3)
print("placements with at least 3 corners on existing corners:", len(found))
for f in sorted(found, key=lambda f: (-f["on"], f["poly"][0][1])):
    print("   %d on corners, %s, turned %3d: %s" % (f["on"], "flipped" if f["flipped"] else "same hand", f["turn"], " / ".join(name(p) for p in f["poly"])))

p134 = corner(13, 4)
loose = [f for f in sf.placements(V, min_on=2) if any(dist(v, p134) < 0.05 for v in f["poly"])]
print("placements touching 13,4 (%s) with only 2 corners on existing corners: %d" % (name(p134), len(loose)))
for f in loose: print("   %s, turned %3d: %s" % ("flipped" if f["flipped"] else "same hand", f["turn"], " / ".join(name(p) for p in f["poly"])))
# how much room is there at 13,4?  area of the trapezoid that would be free if one side lay on 14's notch side from 13,4
near = [f for f in sf.placements(V, min_on=2) if min(dist(v, p134) for v in f["poly"]) < 45]
print("any 2-corner placement within 45 px of 13,4:", len(near))
if len(sys.argv) > 1 and sys.argv[1] == "write":
    import xml.etree.ElementTree as ET
    SVG = "{http://www.w3.org/2000/svg}"; layer, defs = sf.el["centre"], sf.el["centre_defs"]; W = 100/9
    for n, f in enumerate(sorted(found, key=lambda f: f["turn"]), 1):
        poly = f["poly"]; nm = "ctrap%02d" % n; c = (sum(p[0] for p in poly)/4, sum(p[1] for p in poly)/4)
        j = max(range(4), key=lambda j: (round(dist(poly[j], poly[(j+1) % 4]), 1), -j))
        th = math.degrees(math.atan2(poly[(j+1) % 4][1]-poly[j][1], poly[(j+1) % 4][0]-poly[j][0])) % 180
        pat = ET.SubElement(defs, SVG + "pattern", {"id": nm + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
              "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*c, th, -W/2)})
        ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:#8a3fc0;stroke:none"})
        d = "M " + " L ".join("%.4f %.4f" % p for p in poly) + " Z"
        ET.SubElement(layer, SVG + "path", {"id": nm + "bg", "d": d, "style": "fill:#ffffff;stroke:#8a3fc0;stroke-width:1.5;stroke-linejoin:round"})
        ET.SubElement(layer, SVG + "path", {"id": nm, "d": d, "style": "fill:url(#%spat);stroke:none" % nm})
    sf.tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("wrote", len(found))
