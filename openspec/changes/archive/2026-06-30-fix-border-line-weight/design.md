## Context

The `compose()` function in `mondrian-mcp/mondrian/compose.py` computes two values from the same base formula:

```python
min_dist   = max(1, round(min(width, height) / 20 * multiplier))  # grid spacing
border_lwd = max(1, round(min(width, height) / 20))               # SVG stroke-width
```

Because SVG `stroke-width` is centered on a rect's edge (half inside, half outside), a `border_lwd` of N eats N/2 px into the fill on each side. When `border_lwd == min_dist` (which always holds for normal density), the smallest possible cell has zero visible fill — it renders as a solid black rectangle. This is catastrophic on narrow canvases like `header_band` (960×120) where many cells approach the minimum size.

Actual Mondrian paintings have lines that are roughly 0.5–1% of the canvas dimension. The current divisor of 20 produces lines that are 5% of `min(W, H)` — five to ten times too thick proportionally.

## Goals / Non-Goals

**Goals:**
- Fix visually broken output on all placement presets, especially `header_band` (960×120) and `left_panel` (200×540)
- Produce line weights proportionally consistent with real Mondrian compositions (~1–2% of `min(W,H)`)
- Maintain the organic variation already present (line thickness still varies with canvas size)
- Keep the fix as a single-line change with no structural refactoring

**Non-Goals:**
- Per-line randomized width variation (the previous approach that was already removed)
- Matching the exact pixel-for-pixel line thickness of any specific R output
- Changing the grid density, color palette, or drawing order

## Decisions

### Decision: Change the divisor from 20 to 60

**Chosen:** `border_lwd = max(1, round(min(width, height) / 60))`

**Rationale:**
- Divisor 60 yields ~1.7% of `min(W, H)`, close to real Mondrian proportions
- At 960×120: `border_lwd = 2px` — clearly visible but non-obliterating against a 6px minimum cell
- At 400×400: `border_lwd = 7px` — visually similar to current output on square canvases
- At 960×540: `border_lwd = 9px` — proportionally appropriate for a large canvas

**Alternatives considered:**

| Approach | Result at 120px min | Result at 400px min | Notes |
|---|---|---|---|
| Divisor 20 (current) | 6px (breaks header) | 20px (too thick) | Bug |
| Cap at `min_dist // 3` | 2px | 6px | Fixes bug, but ties thickness to density |
| Fixed 2px constant | 2px | 2px | No variation; looks thin on large canvases |
| Divisor 60 (chosen) | 2px | 7px | Best proportional scaling; independent of density |

The divisor-60 approach is preferred over capping at `min_dist // 3` because it keeps `border_lwd` independent of the density multiplier — line weight should be a property of the canvas size, not the grid density setting.

### Decision: No change to `min_dist` formula

`min_dist` drives grid density, which is already correct and user-controllable via the `density` parameter. It must remain at `min(W,H) / 20` (with multiplier). Only `border_lwd` changes.

## Risks / Trade-offs

- **Appearance change on existing square/large canvases**: Lines will be visibly thinner on 400×400 and 960×540 outputs (20px → 7px, 27px → 9px). This is intentional and matches real Mondrian proportions, but outputs will not be pixel-identical to prior versions for the same seed. → _Acceptable: the prior thickness was incorrect._
- **Very small canvases** (e.g., custom 50×50): divisor 60 gives `border_lwd = 1`, which is fine. → _No regression._
- **Reproducibility**: Seeded outputs will look different after this change. Any stored seeds will produce different-looking images. → _Acceptable: this is a bug fix, not a behavioral change contract._

## Migration Plan

1. Change one line in `compose.py`
2. Update the spec requirement and scenario for border line weight
3. Update/add tests to assert the new invariant: `border_lwd <= min_dist // 2`
4. Regenerate sample images (if any are checked in) — none currently are
5. No deployment steps needed; no external API changes
