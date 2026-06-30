## Why

On narrow-aspect-ratio canvases (e.g., the `header_band` preset at 960×120), the SVG border stroke-width is large enough to completely obliterate the smallest colored cells, producing a mostly-black image instead of a Mondrian-style composition. The root cause is that `border_lwd` is derived from `min(width, height) / 20` — the same formula used for grid spacing — meaning the border can be as thick as the smallest possible cell.

## What Changes

- Replace the `border_lwd` formula: decouple it from `min_dist` by dividing by 60 instead of 20, reducing line thickness to ~1.7% of the minimum canvas dimension (consistent with actual Mondrian painting proportions and visually correct across all aspect ratios).
- Update the spec for the `art-generator` capability to reflect the corrected line-weight behavior.
- Update or add tests to assert that the border stroke-width never exceeds a safe fraction of the minimum cell size.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `art-generator`: The requirement for how grid line / border stroke thickness is computed is changing. The behavior that `border_lwd = round(min(W,H) / 20)` produces visually consistent output is being corrected — the divisor changes to 60 and the requirement now specifies that line weight must remain visible (non-obliterating) across all placement presets, including extreme aspect ratios.

## Impact

- `mondrian-mcp/mondrian/compose.py`: single-line change to `border_lwd` formula
- `mondrian-mcp/tests/test_compose.py`: existing and new tests for line weight behavior
- `openspec/specs/art-generator/spec.md`: updated requirement and scenario for border line weight
- No API changes; no new dependencies; output format unchanged
