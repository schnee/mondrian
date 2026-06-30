## Context

The current palette in `compose.py`:

```python
_COLORS  = ["#c70000", "#f4b600", "#2d2bb4", "black", "white"]
_WEIGHTS = [0.15,       0.15,      0.15,      0.05,    0.50]
```

`fill="black"` has a 5% draw probability. Because the algorithm draws rectangles in grid iteration order with later rects overwriting earlier ones, a black rect drawn late in the sequence can cover a large portion of the canvas — producing images that are predominantly black. This is particularly visible on the narrow `header_band` (960×120) preset where fewer total rects are drawn, so any single late rect has outsized visual impact.

Real Mondrian paintings (e.g., *Composition II in Red, Blue, and Yellow*, 1930) use black exclusively for grid lines. Cell fills are red, yellow, blue, and white only.

## Goals / Non-Goals

**Goals:**
- Remove `fill="black"` from the color palette entirely
- Redistribute its 5% weight to white (historically the dominant non-primary color in Mondrian's work)
- Keep all other weights unchanged

**Non-Goals:**
- Changing the grid line color (black lines stay black)
- Adjusting red/yellow/blue weights
- Any change to the drawing algorithm, grid sampling, or SVG structure

## Decisions

### Decision: Redistribute black's weight to white

**Chosen:** white weight increases from 0.50 → 0.55; red/yellow/blue unchanged at 0.15 each.

**Rationale:** White is the natural absorber — it's already the dominant fill in Mondrian's work and in our output. Spreading the 5% equally across all three primaries (0.167 each) would slightly increase color saturation, which is a separate aesthetic choice not requested here. Keeping it simple.

**New palette:**
```python
_COLORS  = ["#c70000", "#f4b600", "#2d2bb4", "white"]
_WEIGHTS = [0.15,       0.15,      0.15,      0.55]
```

Weights sum to 1.0. ✓

### Decision: No fallback/compatibility mode

There is no need to preserve `fill="black"` as an option behind a flag. It was never documented as an intentional feature, and its removal improves output quality across all usage.

## Risks / Trade-offs

- **Seeded reproducibility**: Any existing seed that previously produced a black-fill rect will now produce a different color there. This is intentional — it's a palette correction. → _Acceptable._
- **Slightly more white**: White probability increases 5pp. The visual change is minor and consistent with real Mondrian proportions. → _Acceptable._
- **No migration needed**: Pure Python change, no stored state, no database, no API contract on specific fill colors.
