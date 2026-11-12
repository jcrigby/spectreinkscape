# Spectre mosaic

A [Spectre](https://en.wikipedia.org/wiki/Einstein_problem) tile drawn as a mosaic: the
14-sided tile is filled with a handful of simple shapes instead of being one solid piece.

![The four base shapes and the Spectre tile built from them](spectre-shapes.svg)

## The idea

- Start from the straight-sided Spectre (14 edges of equal length).
- Put a regular hexagon on every edge, with the edge as its long diagonal. Going round the
  tile, take the outer half of the first hexagon, the inner half of the next, and so on.
  Those alternating halves become the tile's outline, so every edge is either a bump or a
  matching notch.
- Fill the inside with as few different shapes as possible, with no overlaps.

The tile above uses four shapes, all cut from the same triangle:

| Shape | Size (tile edge = 1) | Per tile |
|---|---|---|
| Triangle | equilateral, side 1/2 | 61 |
| Half triangle | 30-60-90, sides 1/4, √3/4, 1/2 | 23 |
| Small triangle | 30-60-90, sides 1/8, √3/8, 1/4 | 10 |
| Trapezoid | parallel sides 1/4 and 1/8, height √3/8 | 1 |

These 95 pieces cover 97.9% of the tile. The rest is thin slivers where the two triangle
grids, turned 30° from each other, meet.

The hexagon-edged tile was checked to fit together with copies of itself: `spectre.svg`
includes a 71-tile patch built by the Spectre substitution rules, with no overlaps and no
holes. The edge shape is not claimed to force aperiodicity.

## Files

- `spectre.svg` is the working drawing: a locked reference tile, an editable working tile
  with numbered hexagons and corner labels, loose pieces to drag around, and the 71-tile
  patch showing the pieces inside every tile.
- `spectre-shapes.svg` is the summary sheet shown above.

## Earlier versions

The drawing went through several piece sets on the way here. Git tags mark the milestones:

- `full-fill-17-pieces`: 17 larger pieces per tile, including custom shapes (99.9%).
- `two-shape-victory`: only triangles and half triangles (95.8%).
- `four-shape-97`: the four shapes above (97.9%).

## How it was made

Drawn in Inkscape, with [Claude Code](https://claude.com/claude-code) driving the running
Inkscape window step by step and checking each piece for overlaps before placing it.
