import math, re, sys, importlib.util, io, contextlib, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ft", here + "/filltri.py"); ft = importlib.util.module_from_spec(spec)
argv = sys.argv; sys.argv = argv[:1]
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(ft)
Q, dist, clip, area, el, tree, nums = ft.Q, ft.dist, ft.clip, ft.area, ft.el, ft.tree, ft.nums
SVG = "{http://www.w3.org/2000/svg}"
def corner(k, hour):
    a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); th = math.radians(hour*30)
    return (c[0]+50*math.sin(th), c[1]-50*math.cos(th))
def hexat(c, hours): return {h: (c[0]+50*math.sin(math.radians(h*30)), c[1]-50*math.cos(math.radians(h*30))) for h in hours}
labels = {}
for e in el["centre"]:
    i = e.get("id") or ""
    if re.fullmatch(r"(chex|ctri|ccomb|chalf)\d\d", i): labels[i] = nums(e.get("d"))
for k in (5, 9, 11): labels["whole hexagon %d" % k] = ft.hexagon(k)
for k in (1, 3, 7, 13): labels["5/6 hex %d" % k] = nums(el["htile%02d" % k].get("d")); labels["5/6 hex %d triangle" % k] = nums(el["htri%02d" % k].get("d"))
for k in range(2, 15, 2): labels["notch %d" % k] = nums(el["hex%02din" % (k-1)].get("d"))
old16, old17 = labels["chex02"], labels["chex03"]
c16 = (sum(p[0] for p in old16)/6, sum(p[1] for p in old16)/6); c17 = (sum(p[0] for p in old17)/6, sum(p[1] for p in old17)/6)
target = corner(4, 10)
new_c = (target[0], target[1] - 50)                       # pointed hexagon whose bottom corner is 4,10
N16 = hexat(new_c, (12, 2, 4, 6, 8, 10)); new16 = [N16[h] for h in (12, 2, 4, 6, 8, 10)]
H17 = hexat(c17, (1, 3, 5, 7, 9, 11))
print("hexagon 16: centre (%.1f, %.1f) -> (%.1f, %.1f), moved %.1f px, turned 30 deg; old corner 7 (%.1f, %.1f) -> new corner 6 (%.1f, %.1f) = 4,10" % (*c16, *new_c, dist(c16, new_c), *hexat(c16, (7,))[7], *N16[6]))
rest = {k: v for k, v in labels.items() if k not in ("chex02", "chex03")}
hits = {k: round(clip(new16, v), 1) for k, v in rest.items() if clip(new16, v) > 0.5}
print("  new 16 against everything except 17: overlaps %s; inside outline %.0f of %.0f; overlap with old 17: %.0f" % (hits or "none", clip(Q, new16), area(new16), clip(new16, old17)))
halves = {"lower half (corners 9,7,5,3)": (9, 7, 5, 3), "upper half (9,11,1,3)": (9, 11, 1, 3), "left half (11,9,7,5)": (11, 9, 7, 5), "right half (11,1,3,5)": (11, 1, 3, 5),
          "upper-left half (1,11,9,7)": (1, 11, 9, 7), "lower-right half (1,3,5,7)": (1, 3, 5, 7)}
for nm, hs in halves.items(): print("  17 as %-28s overlap with new 16: %6.1f px^2" % (nm, clip([H17[h] for h in hs], new16)))
if len(argv) > 1 and argv[1] == "write":
    assert not hits
    keep = (9, 7, 5, 3); half = [H17[h] for h in keep]; assert clip(half, new16) < 0.5
    layer, defs = el["centre"], el["centre_defs"]; W = 100/9
    d16 = "M " + " L ".join("%.4f %.4f" % p for p in new16) + " Z"
    el["chex02"].set("d", d16); el["chex02bg"].set("d", d16)
    el["chex02pat"].set("patternTransform", "translate(%.4f %.4f) rotate(30) translate(%.5f 0)" % (*new_c, -W/2))
    for i in ("chex03", "chex03bg"): layer.remove(el[i])
    defs.remove(el["chex03pat"])
    n = 1 + max(int(i[5:]) for i in el if re.fullmatch(r"chalf\d\d", i)); nm = "chalf%02d" % n
    a, b = half[0], half[3]; m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    pat = ET.SubElement(defs, SVG + "pattern", {"id": nm + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
          "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*m, math.degrees(math.atan2(b[1]-a[1], b[0]-a[0])) % 180, -W/2)})
    ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:#0a9396;stroke:none"})
    dh = "M " + " L ".join("%.4f %.4f" % p for p in half) + " Z"
    ET.SubElement(layer, SVG + "path", {"id": nm + "bg", "d": dh, "style": "fill:#ffffff;stroke:#0a9396;stroke-width:1.5;stroke-linejoin:round"})
    ET.SubElement(layer, SVG + "path", {"id": nm, "d": dh, "style": "fill:url(#%spat);stroke:none" % nm})
    # labels
    cl = el["layer-corners"]; style = [e for e in cl][0].get("style")
    for e in list(cl):
        i = e.get("id") or ""
        if i.startswith("corner16_") or i in ("corner17_11", "corner17_01"): cl.remove(e)
    for h, p in N16.items():
        t = ET.SubElement(cl, SVG + "text", {"id": "corner16_%02d" % h, "x": "%.2f" % (new_c[0] + 0.76*(p[0]-new_c[0])), "y": "%.2f" % (new_c[1] + 0.76*(p[1]-new_c[1]) + 3.2), "style": style}); t.text = str(h)
    el["num16"].set("x", "%.2f" % new_c[0]); el["num16"].set("y", "%.2f" % (new_c[1] + 7))
    el["num17"].set("x", "%.2f" % c17[0]); el["num17"].set("y", "%.2f" % (c17[1] + 28))
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
    after = {k: v for k, v in rest.items() if not k.startswith("notch")}
    print("coverage: %.1f%% -> %.1f%%" % (100*sum(area(v) for k, v in labels.items() if not k.startswith("notch"))/area(Q), 100*(sum(area(v) for v in after.values()) + area(new16) + area(half))/area(Q)))
