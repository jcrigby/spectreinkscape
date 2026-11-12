import sys, importlib.util, io, contextlib
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ce", here + "/centre.py"); ce = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(ce)
C, R, Q, D, A_ = ce.C, ce.R, ce.Q, ce.D, ce.A_
c5, P4 = C[5], Q[4]
axis5 = ((c5[0]-P4[0])/R, (c5[1]-P4[1])/R); u = (-axis5[1], axis5[0])
if ce.dist((c5[0]+R*u[0], c5[1]+R*u[1]), C[8]) > ce.dist((c5[0]-R*u[0], c5[1]-R*u[1]), C[8]): u = (-u[0], -u[1])
h5 = ce.half_hpf((c5[0]+R*u[0], c5[1]+R*u[1]), axis5, c5, "halfhpf05")
hits = {("circle %d" % j): round(float((h5["mask"] & D(C[j], R-0.2)).sum()*A_), 1) for j in C if (h5["mask"] & D(C[j], R-0.2)).sum()*A_ > 0.5}
hits.update({nm: round(float((h5["mask"] & m).sum()*A_), 1) for nm, m in ce.existing.items() if (h5["mask"] & m).sum()*A_ > 0.5})
hits.update({q["name"]: round(float((h5["mask"] & q["mask"]).sum()*A_), 1) for q in ce.pieces if (h5["mask"] & q["mask"]).sum()*A_ > 0.5})
print("mirror-image half hpf hugging circle 5 from the 4/5 corner: hand %s, overlaps %s" % (h5["hand"], hits or "none"))
