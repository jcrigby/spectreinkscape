import math, sys, importlib.util, io, contextlib, numpy as np
sys.argv = sys.argv[:1]
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("cd", here + "/candidates.py"); cd = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(cd)
C, R, dist = cd.C, cd.R, cd.dist
H = 0.25; x0, y0 = 250.0, 100.0
gx, gy = np.meshgrid(np.arange(x0, 600, H), np.arange(y0, 420, H))
G = lambda c, r=R: (gx-c[0])**2 + (gy-c[1])**2 < r*r
def obstacles(with_A, shrink=0.25):
    m = np.zeros(gx.shape, bool)
    for j in C: m |= G(C[j], R-shrink)
    # long crescent at 5-6-7
    mm, e, n = cd.frame(5); F = (mm[0]+R*e[0]+R*n[0], mm[1]+R*e[1]+R*n[1])
    m |= G(F, R-shrink) & ~G(C[6], R+shrink) & ~G(C[7], R+shrink)
    if with_A:
        for c in cd.cands:
            if c["kind"] == "A": m |= G(c["O"], R-shrink) & ~G(c["ca"], R+shrink) & ~G(c["cb"], R+shrink)
    return m
# hpf sample points in its own frame: dome centre at origin, spike along +x (cusp at (50, 0))
pts = [(x, y) for x in np.arange(-50, 50.01, 1.5) for y in np.arange(-50, 50.01, 1.5)
       if x*x+y*y <= 2500 and (x-50)**2+(y-50)**2 >= 2500 and (x-50)**2+(y+50)**2 >= 2500]
for t in np.linspace(0, 2*math.pi, 240, endpoint=False):
    x, y = 50*math.cos(t), 50*math.sin(t)
    if (x-50)**2+(y-50)**2 >= 2500 and (x-50)**2+(y+50)**2 >= 2500: pts.append((x, y))
for t in np.linspace(0, math.pi/2, 60):
    pts.append((50-50*math.sin(t), 50-50*math.cos(t))); pts.append((50-50*math.sin(t), -50+50*math.cos(t)))
pts = np.array(pts)
c5, c8 = C[5], C[8]; mid = np.array([(c5[0]+c8[0])/2, (c5[1]+c8[1])/2]); axis = np.array(cd.axis)
ox, oy = np.meshgrid(np.arange(370, 480, 1.0), np.arange(190, 300, 1.0)); ox, oy = ox.ravel(), oy.ravel()
base_ang = math.atan2(axis[1], axis[0])
def search(with_A):
    obs = obstacles(with_A); best = None; count = 0
    for dth in np.arange(-60, 60.1, 2.0):
        th = base_ang + math.radians(dth); c, s = math.cos(th), math.sin(th)
        px = c*pts[:, 0] - s*pts[:, 1]; py = s*pts[:, 0] + c*pts[:, 1]
        X = ox[:, None] + px[None, :]; Y = oy[:, None] + py[None, :]
        ix = np.clip(((X - x0)/H).round().astype(int), 0, gx.shape[1]-1); iy = np.clip(((Y - y0)/H).round().astype(int), 0, gx.shape[0]-1)
        ok = ~obs[iy, ix].any(axis=1)
        if ok.any():
            count += int(ok.sum())
            cx, cy = ox[ok] + 50*c, oy[ok] + 50*s                      # cusp positions
            depth = (cx - mid[0])*axis[0] + (cy - mid[1])*axis[1]
            k = int(np.argmax(depth))
            if best is None or depth[k] > best[0]: best = (float(depth[k]), float(ox[ok][k]), float(oy[ok][k]), float(dth))
    return best, count
for with_A in (True, False):
    best, count = search(with_A)
    print("keeping the A candidates as obstacles: %s -> %d clear placements; deepest: %s" % (with_A, count,
          "cusp %.1f px relative to the 5-8 neck, dome centre (%.0f, %.0f), turned %.0f deg from straight-on" % best if best else "none"))
