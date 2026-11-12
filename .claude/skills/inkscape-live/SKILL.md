---
name: inkscape-live
description: Draw or edit in the user's running Inkscape window so they can watch it happen, by sending Inkscape actions over D-Bus. Use when the user asks to do something "in Inkscape" live, step by step, or while they watch. Not needed for just producing an SVG file.
---

# Driving a running Inkscape live

Inkscape 1.x (tested: 1.4.4 snap on Linux) exposes its actions on the session D-Bus as
`org.inkscape.Inkscape`. The helper `ink.py` in this folder wraps everything below (the skill
may be installed per user in `~/.claude/skills/inkscape-live/` or per project in
`.claude/skills/inkscape-live/`; use whichever folder this file is in):

```
I="python3 <this folder>/ink.py"
$I status                        # running? which window/N and document/N exist
$I new  ~/proj/drawing.svg --size 700x550    # new SVG with a hidden seed path, opened live
$I open ~/proj/existing.svg
$I add  tile1 "M 10 10 L 90 10 L 90 90 Z" --style "fill:#fc0;stroke:#000;stroke-width:3"
$I act  select-by-id tile1
$I act  transform-rotate 30      # argument types are converted automatically
$I act  select-clear
$I snap ~/proj/preview.png       # then Read the PNG to check the result
$I dump ~/proj/readback.svg      # full document as SVG: ids, d, transforms
$I actions app|win|doc [-n N]    # list available action names
$I zoom ~/proj/zz.png 620 40 1180 480 --dpi 144   # close-up of a rectangle; resets export after
$I changed ~/proj/drawing.svg [--rev HEAD] [--under LAYER_ID]   # the user's hand edits vs git
$I overlaps ~/proj/drawing.svg --under LAYER_ID --match '^pc_'  # exit 1 if pieces overlap
```

`changed` and `overlaps` read the file on disk, so `act document-save --win N` first. Their
helpers import cleanly for scripts: `sys.path.insert(0, "<this folder>"); import ink`, then
`ink.parse_path(d)` (handles Inkscape's relative `m … v … l … z`; returns None for curves),
`ink.load_polys(file, under=ID)` (page coordinates, ancestor transforms applied),
`ink.overlap(p, q)`, `ink.area(p)`, `ink.is_convex(p)`.

Inkscape must already be running; if `status` fails, ask the user to start it.

## How it works, and its limits

- **Three action groups.** App actions (`/org/inkscape/Inkscape`) do selection, duplicate,
  transforms, object attributes, path booleans, export. Window actions (`--win N`) do zoom,
  save, paste, layers, tool switching. Document actions (`--doc N`) do `undo` / `redo`.
- **App actions hit the active document**: whichever window the user focused last. Tell the
  user to keep the target window as the last one they clicked in.
- **No action creates a shape.** Create by duplicating an existing path and overwriting its
  `d`, `style` and `id` (`ink.py add` does this from the path with id `seed`). A document not
  made by `ink.py new` has no seed: pass `--from <id of any existing path>`.
- **Text, layers, patterns, anything that is not a path:** cannot be made by duplication.
  With the document saved and unmodified, edit the SVG file on disk (e.g. append a
  `<g inkscape:groupmode="layer" inkscape:label="...">` holding `<text>` elements), then
  `ink.py act document-revert --win N` reloads it in place with no prompt (verified).
  `document-save --win N` saves without a dialog when the document already has a filename.
- **Stacking:** `selection-top` on root-level objects lifts them above layer groups too, and
  later duplicates can land above a layer. If a labels layer must stay on top, finish with
  `select-by-id <layer id>` + `selection-top`, and check the order with `dump`.
- **Moving text:** setting `x`/`y` on a `<text>` changes the attribute but the canvas and
  exports keep the old position until the document is saved and reloaded
  (`document-save` then `document-revert`).
- **Toggle actions have readable state** (snapping etc.): `gdbus call --session --dest
  org.inkscape.Inkscape --object-path /org/inkscape/Inkscape/window/N --method
  org.gtk.Actions.Describe snap-global-toggle` returns `(enabled, signature, [<state>])`.
  Read the state first and activate the toggle only if it differs. Snap toggles
  (`snap-global-toggle`, `snap-node-category`, `snap-node-cusp`, `snap-bbox`,
  `snap-alignment`, `simple-snap-*`) are application preferences, not saved in the SVG.
- **Locking a layer:** `sodipodi:insensitive="true"` on the layer `<g>` (file edit + reload).
- **The user may be editing while you work.** A `document-save` also saves their unsaved
  moves; a `document-revert` after a file edit discards anything they changed since the last
  save. Save first if they have been working in the window.
- **Actions return nothing.** The only readback is exporting: `snap` (PNG, look at it) and
  `dump` (SVG, read ids and attributes). Always snap after a step before claiming it worked.
  A wrongly typed argument is silently ignored, which is why `ink.py act` looks up the type.
- **Useful actions:** `select-by-id`, `select-clear`, `duplicate` (selection moves to the
  copy), `object-set-attribute "name,value"`, `object-set-property "cssprop,value"`,
  `transform-rotate DEG`, `transform-translate "dx,dy"`, `transform-scale`, `delete-selection`,
  `path-union`, `path-combine`, `object-to-path`, `selection-group`.
- **Exact placement:** `transform-rotate` turns about the bounding-box centre and bakes the
  result into `d`. For exact geometry set the transform yourself:
  `object-set-attribute "transform,translate(dx dy) rotate(deg cx cy)"`.
- **Paths the snap can use:** only non-hidden paths under the home directory. `/tmp` is
  private to the snap (verified: exports there vanish), so put SVGs and preview PNGs in the
  project directory and tell the user they are there.
- **Opening a file** reuses the window if its document is blank and untouched, otherwise it
  opens another window. Window and document numbers keep counting up and closed documents
  stay listed, so run `status` instead of assuming numbers.

## Preferred workflow for anything beyond a few actions: edit the file, then reload

Driving shapes one D-Bus action at a time is slow and cannot make groups, patterns, text or
layers. For real drawing work this loop is faster and exact, and the user still sees every
step appear in the window:

```
$I act document-save --win 1          # 1. always first: captures the user's unsaved hand edits
python3 edit.py                       # 2. change the SVG with xml.etree.ElementTree
$I act document-revert --win 1        # 3. reload in place, no prompt
$I snap $PWD/preview.png              # 4. look at it before claiming anything
```

- Register the namespaces before parsing or ElementTree rewrites every prefix as `ns0:`:
  `svg`, `inkscape` (`http://www.inkscape.org/namespaces/inkscape`), `sodipodi`
  (`http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd`), `xlink`.
- Before writing, assert ids are unique and every `url(#id)` in a style resolves. A dangling
  pattern reference renders as no fill, silently.
- **Close-up exports** (page-sized snaps are too coarse to check a fit): `ink.py zoom`. It
  sets `export-area`, `export-dpi`, exports, then restores 96 dpi and the page area. Give an
  absolute path with the shell's `$PWD` expanded; a literal `$PWD` exports nowhere, silently.
- If a script fails after `document-save` but before writing, the window still shows the old
  state and any preview on disk is stale. Check the exit code before reading the PNG.

## Reading what the user did by hand

When the user drags, duplicates or deletes things and says "fix them up":

- `document-save`, then `ink.py changed FILE` (add `--under LAYER_ID` to cut noise). It
  lists MOVED / NEW / GONE paths against the last commit with resolved page coordinates and
  the move vector. That diff is the user's edit. Coordinates are page coordinates: subtract a
  layer's own translate if you work in layer-local coordinates.
- **Inkscape rewrites the `d` of anything it touches in relative form**, e.g.
  `m 338.4,243.3 v 50 l 43.3,-25 z`. A regex that grabs number pairs reads this as garbage
  (it produced polygons flying across the page here). Use a real parser for `m/l/h/v/z` in
  both cases, tracking the current point.
- A dragged **group** gets `transform="translate(dx,dy)"` and its children keep their old
  `d`; a dragged plain path gets a rewritten `d`. Handle both, and remove the transform when
  you write the exact position back.
- Objects Inkscape creates (duplicates, and any element you wrote without an id) get ids like
  `path35`, `rect91`. Do not assume every id follows your naming scheme when copying layers.
- Infer intent from the geometry: a piece dragged far outside the work area was discarded;
  a duplicate still sitting on the parking spot is clutter. Say which you assumed.
- Snap by rebuilding the shape exactly from known corner points, not by nudging the user's
  coordinates. Check the result with `ink.py overlaps` (or `ink.overlap` in the script,
  before writing) and refuse overlaps rather than draw them; if a piece cannot fit, say by
  how many pixels and leave it out. `overlaps` needs at least one polygon of each pair to be
  convex, treats stacked copies of one shape as one piece, and ignores open polylines; use
  `--match` to keep guide shapes and outlines out of the comparison.
- Keep reusable fix-up helpers in one scratchpad module (parse, set piece, new piece, delete,
  re-park, overlap check + write) instead of re-typing them in each heredoc.

## "Does it fit?" and "fill what's left": answer by search, not by eye

Questions like "can another triangle go in here", "how much more can these shapes cover" or
"fill the gaps with this new shape" are cheap to settle exactly, and guessing from a preview
is how overlaps get drawn. The method that worked:

1. **Free space** = the outline minus every existing piece and cut-out. Report its area first;
   it bounds any answer.
2. **Candidates:** each shape in every allowed rotation (use the drawing's own angle step) and
   both mirror images, translated so one of its vertices lands on an anchor. Anchors are the
   vertices of existing pieces plus the midpoints of their sides; midpoints matter as soon as a
   shape is half the size of its neighbours. Keep a candidate only if it lies inside the
   outline and `ink.overlap` with every piece is below a small tolerance (0.3–0.5 px²).
3. **Grow once or twice:** add the kept candidates' own vertices and midpoints as anchors and
   repeat, so pieces can stack off each other. Two or three rounds is enough; the count grows
   fast (124 → 861 → 4544 here).
4. **Choose:** build the conflict graph (pairs that overlap), split it into connected
   components (separate gaps), and solve each for maximum covered area by branch and bound
   with a time cap. Gaps are small, so this is exact in practice.
5. **Cross-check feasibility with a raster sweep** when the answer is "nothing fits": rasterise
   the free space at 4 px per unit, and for each shape and rotation (5° steps) convolve to find
   every translation where it fits (`scipy.signal.fftconvolve` of the blocked mask with the
   shape mask). This catches placements that are not anchored to any corner. Treat fits that
   exist only at odd angles with zero clearance as "can be jammed in", not as real fits.
6. **Report** counts per shape, coverage before and after, what stays open and why, and by how
   much the nearest miss fails ("3.1 px too long"). Then draw only what passed the checks.

Also from this kind of work:

- When the user describes a new shape loosely ("cut it in half: a trapezoid and a triangle"),
  pick the most natural reading, **state the exact cut and dimensions you used**, and carry on;
  the drawing makes a wrong guess obvious and cheap to redo.
- When a hand placement almost fits, say so with the number and leave it out. The user found
  their own fix (removing a neighbour) once told the pocket was 3 px short.
- Give each shape its own colour and keep it consistent between the working drawing and any
  overview (patch, legend). Stripe patterns turn to blobs on pieces under ~25 px; that is fine
  for telling shapes apart, not for reading orientation.
- If an operation recurs ("copy the working side to the reference and refresh the overview"),
  put it in one script the first time it is asked for, and make the script assert its own
  invariants (unique ids, resolvable `url(#…)`, no leftover group transforms, known shape
  kinds) before it writes.

## Making a drawing the user can play with

- **One visible piece = one object.** A piece drawn as two stacked paths (outline + pattern
  fill) gets pulled apart when the user drags it. Wrap them in a `<g>`.
- **Movable pieces:** keep a separate layer of semi-transparent pieces
  (`fill-opacity:0.5`) parked beside the work, in every rotation/flip the user might need.
  After transcribing a placement, put the piece back on its parking spot.
- **Lock what must not move:** `sodipodi:insensitive="true"` on that layer. A locked
  reference copy next to an unlocked working copy works well; copying one to the other is a
  deep copy with ids re-suffixed (and `url(#…)` references renamed to match).
- **Striped fills:** an SVG `<pattern patternUnits="userSpaceOnUse">` with one rect, placed
  with `patternTransform="translate(cx cy) rotate(deg) translate(-w/2 0)"`. When you move a
  piece, move its pattern's translate too.
- **Rotation snapping** for the user is a preference, not an action: Edit > Preferences >
  Behavior > Steps > "Rotation snaps every". Tell them to hold Ctrl while rotating.
- Commit after every accepted change and tag milestones; it makes "go back to how it was at
  X" a file restore plus `document-revert`. Restore with `git show REV:file > file` or by
  re-applying known values; a bare `git checkout -- file` may be refused as destructive.

## Derived pictures, more than one window, publishing

- **Standalone pictures from a working drawing** (a legend sheet, one layer on its own for a
  README): generate a separate SVG with a script instead of exporting by hand. Read geometry
  with `ink.load_polys(file, under=LAYER_ID)`; for a layer of `<use>` clones, apply each
  clone's `ink.parse_transform(...)` to the source group's points to get the bounding box, then
  write a new `<svg>` whose `viewBox` is that box plus a margin, holding a deep copy of the
  layer and a white background rect. Such files are snapshots: say so, and regenerate them
  when the source changes.
- **Check a generated SVG without Inkscape:** `google-chrome --headless=new --disable-gpu
  --hide-scrollbars --window-size=W,H --screenshot=OUT.png file:///abs/path.svg`, then Read the
  PNG. It can write anywhere (it is not the snap), opens no window in the user's Inkscape and
  does not change which document is active. Look for it with `which google-chrome chromium`.
- **A second window changes the target of app actions.** `ink.py open` on another file gives
  window/2 and document/2 and makes it the active document, so `snap`, `zoom` and every export
  now hit that file, while `--win 1` actions still hit the first. There is no action to switch
  focus: tell the user to click in the window you need, and check a `snap` before trusting it.
  Windows cannot be closed over D-Bus (see Safety); ask the user to close extras.
- **GitHub:** a README can show a repo SVG directly (`![alt](picture.svg)`); plain shapes,
  `<use>` clones and generic `sans-serif` text render. Keep preview PNGs out of the repo
  (`.gitignore`). Creating a repo and pushing are outward-facing: do them when asked, default
  to private if visibility was not stated and say so, and push tags (`git push origin --tags`)
  if milestones were tagged. Local commit-after-each-change does not imply pushing.

## Freezing the result into a generator script

When the user calls a hand-built drawing finished and wants it reproducible ("a script that
creates the final"), write one standalone script rather than shipping the session's scratch
scripts:

- **Split data from rules.** Whatever was placed by hand or found by search (piece corners) is
  data: read it once from the working SVG with `ink.load_polys` and embed it as a literal
  table. Whatever follows from a rule (an outline built from the edges, a tiling built by
  substitution, colours, layout) is computed. Say in a comment which is which.
- **Use the drawing's natural units** in the table (here: tile edge = 1, y up), not page
  pixels; convert at output time. It makes the data readable and the picture rescalable.
- **Standard library only**, no numpy: 2×3 affine tuples and Sutherland–Hodgman are a few
  lines, and the script then runs anywhere the repo is cloned.
- **Assert before writing:** no two pieces overlap, every piece is inside the outline, counts
  are what the README claims. A generator that silently draws a broken tile is worse than none.
- **Make the committed pictures the script's output.** Run it into a scratch folder, render
  with headless Chrome and compare by eye with the hand-built version, then run it in the repo
  and `cmp` against the checked files before committing. From then on the README can say the
  pictures are generated, and it stays true.
- **State what it does not rebuild** (the interactive working file with labels, locked copies
  and loose pieces) and that the embedded table must be refreshed if the drawing changes.
- Running Python inside the repo leaves `__pycache__/` next to imported helpers; put it in
  `.gitignore` before `git add -A`.

When this skill is kept both per user and inside a project repo, edit one copy, copy it over
the other, and commit; `diff -r` the two folders to confirm they match.

## Safety: this can crash Inkscape

Inkscape crashed once here: a scratch window was closed over D-Bus (`document-close --win N`
after a run of `undo`), and the next `export-do` timed out and took the app down. The same
sequence had worked a few minutes earlier, so the trigger is not pinned down.

- Do not close windows or documents over D-Bus. Ask the user to close them.
- Do not experiment in the instance holding the user's unsaved work. Get the user to save
  (Ctrl+S) before a long live session, and remind them at milestones.
- After a crash Inkscape writes an emergency copy next to the file, named like
  `drawing.svg.2026_11_11_15_26_03.0.svg`. Check it and restore from it.

## Step-by-step sessions the user watches

For "do one step, then wait for me": do exactly one step per turn, snap and look, report what
changed in a sentence, and stop. Put short sleeps (about 1 s) between the sub-actions of a
step (duplicate, rotate, move) so the motion is visible. Keep geometry in a small script in
the scratchpad that takes the step number, and have it assert the computed positions before
sending anything.
