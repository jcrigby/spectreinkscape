# Scratch scripts

These are the throwaway scripts written while the drawing was being built, kept for the
record. They are not a tool: most did one step against `spectre.svg` as it was at that
moment, and will fail or do the wrong thing against the file as it is now. To rebuild the
finished result use [`make_spectre.py`](../make_spectre.py) in the repo root instead.

The only changes from the originals are that temporary-folder paths were made relative, so
anything here is meant to be run from the repo root (`python3 scratch/NAME.py`), and that
`rfix.py` tolerates a missing `scratch/prev.svg`. Many need `numpy`; `more3r.py` also needs
`scipy` and `Pillow`. Scripts that send actions to Inkscape need it running.

## Still useful

| Script | What it does |
|---|---|
| `tiling.py` | Builds a patch of the Spectre tiling by substitution and checks that the hexagon-edged tile leaves no overlaps or holes (71 tiles, 406 shared edges, all bump-to-notch). Runs on its own. |
| `quarter.py` | The gap-filling search: tries the small triangle and trapezoid in every rotation and flip against the working tile and picks the best non-overlapping set. |
| `more3.py`, `more3r.py` | The same kind of search for hexagons, truncated hexagons and triangles, plus a raster sweep of every position. |
| `rfix.py` | Helpers for snapping hand-placed pieces on the working tile: path reader, set/add/delete a piece, overlap check. |
| `r2l.py` | Refreshes the tiling patch from the working tile and copies the working tile onto the locked one. **Rewrites `spectre.svg`.** |
| `whatchanged.py` | Lists what differs from a saved copy of the drawing (superseded by `ink.py changed` in the skill). |

## The rest, roughly in the order written

**Circle version** (half circles on the edges; later deleted from the drawing):
`spectre.py`, `circles.py`, `stripes.py`, `stripes_out.py`, `quarters.py`, `spandrel.py`,
`fins.py`, `crescents.py`, `q3pf.py`, `hpf.py`, `gaps.py`, `gaps2.py`, `gapfill.py`,
`longcres.py`, `longcres3.py`, `horns.py`, `fliplong.py`, `fliplong_slide.py`,
`candidates.py`, `hpfsearch.py`, `centre.py`, `mirror5.py`, `bay.py`

**Hexagon version, first fill** (whole and truncated hexagons, then custom pieces; the result
is the git tag `full-fill-17-pieces`):
`hexes.py`, `extend.py`, `drawpatch.py`, `alignplay.py`, `readplay.py`, `placeleft.py`,
`patchpieces.py`, `filltri.py`, `gapscan.py`, `gapscan2.py`, `scalene.py`, `shapefit.py`,
`trap3.py`, `trapezoid.py`, `trap3write.py`, `halfhex.py`, `move16.py`, `strip1617.py`,
`diamond.py`, `strip1715.py`, `corners2.py`, `convex16.py`, `merge16tri.py`, `mergehalf.py`,
`elong11.py`, `move16c.py`

**Hexagon version, second fill** (triangles and half triangles; tags `two-shape-victory` and
`four-shape-97`):
`addpiece.py`, `sync.py`, `fixhalf.py`, and the scripts in the table above. `sync.py` copies
left to right and is stale: the working tile is now the right-hand one (`r2l.py`).

Many steps were also done as one-off inline snippets that were never saved as files, so this
folder is not a complete replay of the session.
