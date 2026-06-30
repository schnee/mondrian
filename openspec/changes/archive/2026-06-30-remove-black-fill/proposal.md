## Why

Several generated header band images are aesthetically broken: a large `fill="black"` rectangle drawn late in the overwriting sequence buries all the colored cells beneath it, producing images that look predominantly black rather than Mondrian-style. Black as a fill color is also historically inaccurate — in Piet Mondrian's actual paintings, black appears only as grid lines, never as cell fills. Removing it from the fill palette eliminates the failure mode entirely and improves historical fidelity.

## What Changes

- Remove `"black"` from `_COLORS` and its corresponding weight from `_WEIGHTS` in `mondrian/compose.py`.
- Redistribute the freed 5% weight (previously assigned to black fill) to white, bringing white's weight from 0.50 to 0.55.
- Update the spec for the `art-generator` capability to reflect the corrected palette.
- Update tests that reference the old palette or weight distribution.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `art-generator`: The requirement for cell fill palette is changing. `fill="black"` is removed; the palette becomes red, yellow, blue, and white only. White's weight increases slightly to absorb the removed probability mass.

## Impact

- `mondrian-mcp/mondrian/compose.py`: remove `"black"` from `_COLORS` and adjust `_WEIGHTS`
- `mondrian-mcp/tests/test_compose.py`: update palette constant and any weight-related assertions
- `openspec/specs/art-generator/spec.md`: updated palette requirement
- No API changes; no new dependencies; output format unchanged
- Seeded outputs will look different (fewer/no black fill cells) — acceptable as a bug fix
