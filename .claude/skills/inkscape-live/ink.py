#!/usr/bin/env python3
"""Drive a running Inkscape over D-Bus. See SKILL.md next to this file.

  ink.py status                         is Inkscape reachable; which windows/documents exist
  ink.py actions [app|win|doc] [-n N]   list action names (extension/filter noise removed)
  ink.py act NAME [ARG] [--win N | --doc N]   send one action (default target: the app);
                                        ARG is converted to the type the action declares
  ink.py new FILE [--size WxH]          write an SVG holding a hidden seed path and open it
  ink.py open FILE                      open an existing SVG in the running Inkscape
  ink.py add ID D [--style CSS] [--from SEED_ID]   new path: duplicate seed, set d/id/style
  ink.py snap OUT.png                   export the active document's page to PNG (to look at)
  ink.py dump OUT.svg                   export the active document as SVG (to read ids/attrs)
  ink.py zoom OUT.png X0 Y0 X1 Y1 [--dpi 192]   export a close-up of that rectangle, then
                                        put the export settings back to the whole page
  ink.py changed FILE [--rev HEAD] [--under ID]   what differs from the git revision: moved,
                                        new and deleted objects, with resolved coordinates
  ink.py overlaps FILE [--under ID] [--match REGEX] [--min 0.5]   pairwise overlap areas of
                                        the straight-sided closed paths (stacked copies of the
                                        same shape count as one piece)

The file commands (changed, overlaps) read the SVG on disk: run `act document-save --win N`
first. Their helpers can be imported: sys.path.insert(0, <this folder>); import ink, then
ink.parse_path(d), ink.load_polys(file), ink.overlap(p, q), ink.area(p).

FILE/OUT paths must be under the home directory and not hidden or in /tmp:
the snap build of Inkscape cannot see /tmp.
"""
import argparse, os, re, subprocess, sys, time

DEST = "org.inkscape.Inkscape"
ROOT = "/org/inkscape/Inkscape"
DEFAULT_STYLE = "fill:none;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"


def gdbus(*args):
    return subprocess.run(["gdbus", *args], capture_output=True, text=True)


def gv(s):
    """Quote a string as a GVariant text literal."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def act(name, arg=None, win=None, doc=None):
    """Send one action. The argument is converted to the type the action declares."""
    path = ROOT + (f"/window/{win}" if win else f"/document/{doc}" if doc else "")
    base = ["call", "--session", "--dest", DEST, "--object-path", path, "--method"]
    r = gdbus(*base, "org.gtk.Actions.Describe", name)
    if r.returncode:
        sys.exit(f"no action {name!r} at {path}: {r.stderr.strip()}")
    m = re.search(r"signature '([^']*)'", r.stdout)
    sig = m.group(1) if m else ""
    if sig == "":
        param = "[]"
    elif arg is None and sig == "b":
        param = "[<true>]"
    elif arg is None:
        sys.exit(f"action {name!r} needs an argument of type {sig!r}")
    elif sig == "d":
        param = f"[<double {float(arg)!r}>]"
    elif sig == "i":
        param = f"[<int32 {int(arg)}>]"
    elif sig == "b":
        param = "[<true>]" if str(arg).lower() in ("1", "true", "yes", "on") else "[<false>]"
    else:
        param = f"[<{gv(str(arg))}>]"
    r = gdbus(*base, "org.gtk.Actions.Activate", name, param, "{}")
    if r.returncode:
        sys.exit(f"action {name!r} failed: {r.stderr.strip()}")


def nodes():
    r = gdbus("introspect", "--session", "--dest", DEST, "--object-path", ROOT, "--recurse")
    if r.returncode:
        return None
    return sorted(set(re.findall(r"node /org/inkscape/Inkscape/((?:window|document)/\d+)", r.stdout)))


def usable(path):
    p = os.path.abspath(os.path.expanduser(path))
    home = os.path.expanduser("~")
    rel = os.path.relpath(p, home)
    if rel.startswith("..") or any(part.startswith(".") for part in rel.split(os.sep)):
        sys.exit(f"{p}: Inkscape (snap) can only use non-hidden paths under {home}")
    return p


def wait_for(path, since, secs=5.0):
    end = time.time() + secs
    while time.time() < end:
        if os.path.exists(path) and os.path.getmtime(path) >= since:
            return True
        time.sleep(0.1)
    return False


def export(out, kind):
    out = usable(out)
    t0 = time.time() - 1
    act("export-type", kind)
    if kind == "png":
        act("export-area-page")
    act("export-filename", out)
    act("export-do")
    if not wait_for(out, t0):
        sys.exit(f"no file appeared at {out}: is an Inkscape document window active?")
    print(out)


# ---------- reading geometry from the SVG file ----------

SVGNS = "{http://www.w3.org/2000/svg}"


def parse_path(d):
    """Vertices of a straight-sided path (M L H V Z, absolute or relative), first subpath only.

    Inkscape rewrites any path it touches in relative form (`m 338,243 v 50 l 43,-25 z`), so
    never read coordinates by grabbing number pairs. Returns None if the path has curves."""
    tk = re.findall(r"[A-Za-z]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d or "")
    pts, x, y, i, cmd = [], 0.0, 0.0, 0, None
    while i < len(tk):
        if tk[i].isalpha():
            cmd = tk[i]; i += 1
            if cmd in "zZ":
                break
            if cmd not in "mMlLhHvV":
                return None
            continue
        if cmd in "mMlL":
            a, b = float(tk[i]), float(tk[i + 1]); i += 2
            if cmd.islower() and pts:
                x, y = x + a, y + b
            else:
                x, y = a, b
            if cmd in "mM":
                if pts:
                    break
                cmd = "l" if cmd == "m" else "L"
        elif cmd in "hH":
            v = float(tk[i]); i += 1; x = x + v if cmd == "h" else v
        elif cmd in "vV":
            v = float(tk[i]); i += 1; y = y + v if cmd == "v" else v
        else:
            return None
        pts.append((x, y))
    if len(pts) > 1 and abs(pts[0][0] - pts[-1][0]) < 1e-6 and abs(pts[0][1] - pts[-1][1]) < 1e-6:
        pts.pop()
    return pts


def _mul(m, n):
    a, b, c, d, e, f = m; A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f)


def parse_transform(t):
    """An SVG transform attribute as a matrix (a b c d e f)."""
    import math
    m = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", t or ""):
        v = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if name == "translate":
            n = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            n = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == "rotate":
            c, s = math.cos(math.radians(v[0])), math.sin(math.radians(v[0]))
            n = (c, s, -s, c, 0, 0)
            if len(v) == 3:
                n = _mul(_mul((1, 0, 0, 1, v[1], v[2]), n), (1, 0, 0, 1, -v[1], -v[2]))
        elif name == "matrix":
            n = tuple(v)
        else:
            sys.exit(f"transform {name!r} is not supported")
        m = _mul(m, n)
    return m


def load_polys(file, under=None, closed_only=False):
    """{id: (vertices in page coordinates, parent id)} for every straight-sided path with an id.

    Transforms on the path and on all its ancestors are applied. With `under`, only paths
    inside the element with that id are returned; with
    `closed_only`, open polylines (paths not ending in z) are left out."""
    import xml.etree.ElementTree as ET
    root = ET.parse(file).getroot()
    out = {}

    def walk(e, m, inside, parent):
        m = _mul(m, parse_transform(e.get("transform")))
        inside = inside or under is None or e.get("id") == under
        if e.tag == SVGNS + "defs":
            return
        if e.tag == SVGNS + "path" and inside and e.get("id") and (not closed_only or re.search(r"[zZ]\s*$", e.get("d") or "")):
            pts = parse_path(e.get("d"))
            if pts and len(pts) >= 3:
                out[e.get("id")] = ([(m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]) for x, y in pts], parent)
        for c in e:
            walk(c, m, inside, e.get("id"))

    walk(root, (1, 0, 0, 1, 0, 0), False, None)
    return out


def area(p):
    return abs(sum(p[k][0] * p[(k + 1) % len(p)][1] - p[(k + 1) % len(p)][0] * p[k][1] for k in range(len(p)))) / 2


def _ccw(p):
    s = sum(p[k][0] * p[(k + 1) % len(p)][1] - p[(k + 1) % len(p)][0] * p[k][1] for k in range(len(p)))
    return p if s > 0 else p[::-1]


def is_convex(p):
    p = _ccw(p); n = len(p)
    for k in range(n):
        a, b, c = p[k], p[(k + 1) % n], p[(k + 2) % n]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) < -1e-7:
            return False
    return True


def overlap(subject, convex):
    """Area shared by two polygons (Sutherland-Hodgman). `convex` must be convex; if only
    `subject` is, the two are swapped. Returns None when neither is convex."""
    if not is_convex(convex):
        if not is_convex(subject):
            return None
        subject, convex = convex, subject
    out, c = _ccw(subject), _ccw(convex)
    for k in range(len(c)):
        a, b = c[k], c[(k + 1) % len(c)]
        side = lambda q: (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            sp, sq = side(p), side(q)
            if sp >= 0:
                out.append(p)
            if (sp > 0 and sq < 0) or (sp < 0 and sq > 0):
                t = sp / (sp - sq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        if len(out) < 3:
            return 0.0
    return area(out)


def _fmt(p):
    return " ".join("(%.1f,%.1f)" % q for q in p)


def cmd_changed(file, rev, under):
    import tempfile
    top = subprocess.run(["git", "-C", os.path.dirname(os.path.abspath(file)) or ".", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode:
        sys.exit(f"{file} is not in a git repository")
    rel = os.path.relpath(os.path.abspath(file), top.stdout.strip())
    old = subprocess.run(["git", "-C", top.stdout.strip(), "show", f"{rev}:{rel}"], capture_output=True, text=True)
    if old.returncode:
        sys.exit(old.stderr.strip())
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as fh:
        fh.write(old.stdout)
    try:
        a, b = load_polys(fh.name, under), load_polys(file, under)
    finally:
        os.unlink(fh.name)
    same = lambda p, q: len(p) == len(q) and all(abs(u[0] - v[0]) < 0.01 and abs(u[1] - v[1]) < 0.01 for u, v in zip(p, q))
    n = 0
    for i, (p, par) in b.items():
        if i not in a:
            print(f"NEW   {i} (in {par}): {_fmt(p)}"); n += 1
        elif not same(a[i][0], p):
            q = a[i][0]
            if len(q) == len(p):
                d = [(u[0] - v[0], u[1] - v[1]) for u, v in zip(p, q)]
                rigid = all(abs(x[0] - d[0][0]) < 0.01 and abs(x[1] - d[0][1]) < 0.01 for x in d)
                how = "moved by (%.2f, %.2f)" % d[0] if rigid else "reshaped or rotated"
            else:
                how = "vertex count changed"
            print(f"MOVED {i} (in {par}): {how}\n        now {_fmt(p)}\n        was {_fmt(q)}"); n += 1
    for i, (p, par) in a.items():
        if i not in b:
            print(f"GONE  {i} (was in {par}): {_fmt(p)}"); n += 1
    print(f"{n} difference(s) from {rev}" + (f" under {under}" if under else ""))


def cmd_overlaps(file, under, match, minimum):
    polys = {i: v for i, v in load_polys(file, under, closed_only=True).items() if re.search(match, i)}
    pieces = {}   # stacked copies of one shape (outline + fill) are one piece
    for i, (p, par) in polys.items():
        key = tuple(sorted((round(x, 1), round(y, 1)) for x, y in p))
        pieces.setdefault(key, (i, p))
    items = list(pieces.values())
    found = skipped = 0
    for k, (i, p) in enumerate(items):
        bx = (min(x for x, _ in p), max(x for x, _ in p), min(y for _, y in p), max(y for _, y in p))
        for j, q in items[k + 1:]:
            if bx[1] < min(x for x, _ in q) or bx[0] > max(x for x, _ in q) or bx[3] < min(y for _, y in q) or bx[2] > max(y for _, y in q):
                continue
            o = overlap(p, q)
            if o is None:
                skipped += 1
            elif o > minimum:
                print(f"{i} x {j}: {o:.1f} px2"); found += 1
    print(f"{len(items)} pieces, {found} overlap(s) above {minimum} px2" + (f", {skipped} pair(s) skipped (both non-convex)" if skipped else ""))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("actions"); s.add_argument("scope", nargs="?", default="app", choices=["app", "win", "doc"]); s.add_argument("-n", type=int, default=1)
    s = sub.add_parser("act"); s.add_argument("name"); s.add_argument("arg", nargs="?"); s.add_argument("--win", type=int); s.add_argument("--doc", type=int)
    s = sub.add_parser("new"); s.add_argument("file"); s.add_argument("--size", default="800x600")
    s = sub.add_parser("open"); s.add_argument("file")
    s = sub.add_parser("add"); s.add_argument("id"); s.add_argument("d"); s.add_argument("--style", default=DEFAULT_STYLE); s.add_argument("--from", dest="seed", default="seed")
    s = sub.add_parser("snap"); s.add_argument("out")
    s = sub.add_parser("dump"); s.add_argument("out")
    s = sub.add_parser("zoom"); s.add_argument("out"); s.add_argument("box", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1")); s.add_argument("--dpi", type=float, default=192)
    s = sub.add_parser("changed"); s.add_argument("file"); s.add_argument("--rev", default="HEAD"); s.add_argument("--under")
    s = sub.add_parser("overlaps"); s.add_argument("file"); s.add_argument("--under"); s.add_argument("--match", default=""); s.add_argument("--min", dest="minimum", type=float, default=0.5)
    a = ap.parse_args()

    if a.cmd == "status":
        n = nodes()
        if n is None:
            sys.exit("Inkscape is not on the session bus: ask the user to start it")
        print("Inkscape is running;", ", ".join(n) or "no windows")
    elif a.cmd == "actions":
        path = ROOT + {"app": "", "win": f"/window/{a.n}", "doc": f"/document/{a.n}"}[a.scope]
        r = gdbus("call", "--session", "--dest", DEST, "--object-path", path, "--method", "org.gtk.Actions.List")
        if r.returncode:
            sys.exit(r.stderr.strip())
        names = sorted(x for x in re.findall(r"'([^']+)'", r.stdout)
                       if not re.match(r"(org|effect|jessyink|ru|se|com|math|mcepl)\.", x))
        print(" ".join(names))
    elif a.cmd == "act":
        act(a.name, a.arg, a.win, a.doc)
    elif a.cmd == "new":
        f = usable(a.file)
        w, h = a.size.lower().split("x")
        with open(f, "w") as fh:
            fh.write(f'<?xml version="1.0" encoding="UTF-8"?>\n'
                     f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
                     f'  <path id="seed" d="M 0 0" style="{DEFAULT_STYLE}"/>\n</svg>\n')
        act("file-open-window", f)
        time.sleep(1.5)
        print(f, "opened;", ", ".join(nodes() or []))
    elif a.cmd == "open":
        act("file-open-window", usable(a.file))
        time.sleep(1.5)
        print(", ".join(nodes() or []))
    elif a.cmd == "add":
        act("select-clear"); act("select-by-id", a.seed); act("duplicate")
        act("object-set-attribute", "d," + a.d)
        act("object-set-attribute", "style," + a.style)
        act("object-set-attribute", "id," + a.id)
        act("select-clear")
    elif a.cmd == "snap":
        export(a.out, "png")
    elif a.cmd == "dump":
        export(a.out, "svg")
    elif a.cmd == "zoom":
        out = usable(a.out)
        t0 = time.time() - 1
        act("export-type", "png")
        act("export-area", ":".join("%g" % v for v in a.box))
        act("export-dpi", a.dpi)
        act("export-filename", out)
        act("export-do")
        ok = wait_for(out, t0)
        act("export-dpi", 96)
        act("export-area-page")
        if not ok:
            sys.exit(f"no file appeared at {out}: is an Inkscape document window active?")
        print(out)
    elif a.cmd == "changed":
        cmd_changed(a.file, a.rev, a.under)
    elif a.cmd == "overlaps":
        sys.exit(1 if cmd_overlaps(a.file, a.under, a.match, a.minimum) else 0)


if __name__ == "__main__":
    main()
