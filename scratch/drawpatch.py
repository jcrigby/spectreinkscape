import math, sys, colorsys, importlib.util, numpy as np, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("tg", here + "/tiling.py"); tg = importlib.util.module_from_spec(spec); spec.loader.exec_module(tg)
tiles = tg.patch(2); H = tg.hex_outline()
assert all(abs(np.linalg.det(T[:2, :2]) - 1) < 1e-9 for _, T in tiles)
allp = np.vstack([np.array([tg.ap(T, p) for p in H]) for _, T in tiles])
lo, hi = allp.min(0), allp.max(0); W = 1260.0; margin = 40.0
s = (W - 2*margin) / (hi[0] - lo[0]); top = 590.0
ox = margin - s*lo[0]; oy = top + s*hi[1]; height = top + s*(hi[1]-lo[1]) + margin
NS = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd", "xlink": "http://www.w3.org/1999/xlink"}
for k, v in NS.items(): ET.register_namespace("" if k == "svg" else k, v)
SVG, INK, XL = "{%s}" % NS["svg"], "{%s}" % NS["inkscape"], "{%s}" % NS["xlink"]
tree = ET.parse("spectre.svg"); root = tree.getroot()
el = {e.get("id"): e for e in root.iter() if e.get("id")}
if "patch" in el: root.remove(el["patch"])
root.set("height", "%.0f" % height); root.set("viewBox", "0 0 1260 %.0f" % height)
layer = ET.SubElement(root, SVG + "g", {INK + "groupmode": "layer", INK + "label": "Tiling patch", "id": "patch"})
defs = ET.SubElement(layer, SVG + "defs", {"id": "patch_defs"})
ET.SubElement(defs, SVG + "path", {"id": "patchtile", "d": "M " + " L ".join("%.5f %.5f" % tuple(p) for p in H) + " Z"})
angles = {}
for n, (label, T) in enumerate(tiles):
    a, b, tx, c, d, ty = T[0, 0], T[0, 1], T[0, 2], T[1, 0], T[1, 1], T[1, 2]
    ang = round(math.degrees(math.atan2(c, a)) / 30) % 12; angles[ang] = angles.get(ang, 0) + 1
    r, g, bl = colorsys.hls_to_rgb(ang / 12.0, 0.84, 0.62)
    ET.SubElement(layer, SVG + "use", {"id": "patchtile%03d" % n, XL + "href": "#patchtile",
        "transform": "matrix(%.6f %.6f %.6f %.6f %.4f %.4f)" % (s*a, -s*c, s*b, -s*d, ox + s*tx, oy - s*ty),
        "style": "fill:#%02x%02x%02x;stroke:#b00000;stroke-width:%.4f;stroke-linejoin:round" % (int(r*255), int(g*255), int(bl*255), 1.6/s)})
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
print("%d tiles, %.1f px per edge, patch %.0f x %.0f px, page now 1260 x %.0f; tiles per orientation (x30 deg): %s" % (len(tiles), s, s*(hi[0]-lo[0]), s*(hi[1]-lo[1]), height, dict(sorted(angles.items()))))
