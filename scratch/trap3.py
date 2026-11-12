import math, re, sys, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("sf", here + "/shapefit.py"); sf = importlib.util.module_from_spec(spec); spec.loader.exec_module(sf)
dist, corner, name, clip, area = sf.dist, sf.corner, sf.name, sf.clip, sf.area
V = [corner(8, 4), corner(5, 1), corner(5, 11), corner(8, 6)]
T1 = [corner(8, 4), corner(6, 9), corner(6, 11)]
def angle_at(T, i):
    a, b, c = T[i], T[(i+1) % 3], T[(i+2) % 3]
    return round(math.degrees(math.acos(((b[0]-a[0])*(c[0]-a[0]) + (b[1]-a[1])*(c[1]-a[1])) / (dist(a, b)*dist(a, c)))))
def mapped(T):
    src = {angle_at(T1, i): T1[i] for i in range(3)}; dst = {angle_at(T, i): T[i] for i in range(3)}
    s0, s1, d0, d1 = src[75], src[45], dst[75], dst[45]
    th = math.atan2(d1[1]-d0[1], d1[0]-d0[0]) - math.atan2(s1[1]-s0[1], s1[0]-s0[0]); c, s = math.cos(th), math.sin(th)
    return [(d0[0] + c*(p[0]-s0[0]) - s*(p[1]-s0[1]), d0[1] + s*(p[0]-s0[0]) + c*(p[1]-s0[1])) for p in V]
labels = {}
for e in sf.el["centre"]:
    i = e.get("id") or ""
    if re.fullmatch(r"(chex|ctri|cscal|ctrap)\d\d", i): labels[i] = sf.ft.nums(e.get("d"))
for k in (5, 9, 11): labels["whole hexagon %d" % k] = sf.ft.hexagon(k)
for k in (1, 3, 7, 13): labels["5/6 hex %d (half)" % k] = sf.ft.nums(sf.el["htile%02d" % k].get("d")); labels["5/6 hex %d (triangle)" % k] = sf.ft.nums(sf.el["htri%02d" % k].get("d"))
for k in range(2, 15, 2): labels["notch %d" % k] = sf.ft.nums(sf.el["hex%02din" % (k-1)].get("d"))
for nm, T in (("beside the triangle at 1,1 / 14,2 / 14,4", [corner(1, 1), corner(14, 2), corner(14, 4)]),
              ("at the 12/13 corner (triangle 13,2 / 12,3 / 12,5 would be its partner)", [corner(13, 2), corner(12, 3), corner(12, 5)])):
    W = mapped(T)
    hits = {k: round(clip(W, v)) for k, v in labels.items() if clip(W, v) > 0.5}
    print("trapezoid %s: corners %s" % (nm, " / ".join(name(p) for p in W)))
    print("    inside outline %.0f of %.0f px^2; overlaps %s" % (clip(sf.Q, W), area(W), hits or "none"))
