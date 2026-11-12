import math, re, xml.etree.ElementTree as ET
def parse_path(d):
    toks = re.findall(r"[MmLlHhVvZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
    pts = []; i = 0; cmd = None; cur = (0.0, 0.0); start = None
    def num():
        nonlocal i; v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]): cmd = toks[i]; i += 1
        if cmd in "Zz": continue
        if cmd in "Mm":
            x, y = num(), num(); cur = (cur[0]+x, cur[1]+y) if (cmd == "m" and pts) or (cmd == "m" and False) else ((x, y) if cmd == "M" or not pts else (cur[0]+x, cur[1]+y))
            pts.append(cur); cmd = "L" if cmd == "M" else "l"
        elif cmd == "L": cur = (num(), num()); pts.append(cur)
        elif cmd == "l": x, y = num(), num(); cur = (cur[0]+x, cur[1]+y); pts.append(cur)
        elif cmd == "H": cur = (num(), cur[1]); pts.append(cur)
        elif cmd == "h": cur = (cur[0]+num(), cur[1]); pts.append(cur)
        elif cmd == "V": cur = (cur[0], num()); pts.append(cur)
        elif cmd == "v": cur = (cur[0], cur[1]+num()); pts.append(cur)
        else: raise ValueError(cmd)
    return pts
def parse_transform(t):
    M = [1, 0, 0, 1, 0, 0]
    def mul(A, B): return [A[0]*B[0]+A[2]*B[1], A[1]*B[0]+A[3]*B[1], A[0]*B[2]+A[2]*B[3], A[1]*B[2]+A[3]*B[3], A[0]*B[4]+A[2]*B[5]+A[4], A[1]*B[4]+A[3]*B[5]+A[5]]
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", t or ""):
        a = [float(x) for x in re.split(r"[ ,]+", args.strip()) if x]
        if name == "matrix": N = a
        elif name == "translate": N = [1, 0, 0, 1, a[0], a[1] if len(a) > 1 else 0]
        elif name == "scale": N = [a[0], 0, 0, a[1] if len(a) > 1 else a[0], 0, 0]
        elif name == "rotate":
            c, s = math.cos(math.radians(a[0])), math.sin(math.radians(a[0])); N = [c, s, -s, c, 0, 0]
            if len(a) == 3: N = mul(mul([1, 0, 0, 1, a[1], a[2]], N), [1, 0, 0, 1, -a[1], -a[2]])
        else: raise ValueError(name)
        M = mul(M, N)
    return M
def load(path="spectre.svg", layer="play"):
    r = ET.parse(path).getroot(); out = []
    g = [e for e in r.iter() if e.get("id") == layer][0]
    GM = parse_transform(g.get("transform"))
    for c in g:
        if not c.tag.endswith("}path"): out.append((c.get("id"), c.tag.split("}")[1], None)); continue
        M = parse_transform(c.get("transform")); pts = parse_path(c.get("d"))
        ap = lambda M, p: (M[0]*p[0]+M[2]*p[1]+M[4], M[1]*p[0]+M[3]*p[1]+M[5])
        out.append((c.get("id"), "path", [ap(GM, ap(M, p)) for p in pts]))
    return out
if __name__ == "__main__":
    from collections import Counter
    objs = load(); kinds = Counter()
    for oid, tag, pts in objs:
        if pts is None: print(oid, tag, "(not a path)"); continue
        n = len(pts); sides = [math.dist(pts[k], pts[(k+1) % n]) for k in range(n)]
        cx, cy = sum(p[0] for p in pts)/n, sum(p[1] for p in pts)/n
        kind = {6: "hexagon", 4: "half hexagon", 3: "triangle"}.get(n, "%d-gon" % n); kinds[kind] += 1
        print("%-10s %-12s centre (%.1f, %.1f) sides %s" % (oid, kind, cx, cy, " ".join("%.1f" % s for s in sides)))
    print(dict(kinds))
