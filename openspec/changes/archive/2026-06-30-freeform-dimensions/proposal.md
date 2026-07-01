## Why

The `generate_mondrian` tool currently requires callers to set `placement="custom"` before explicit `width` and `height` values are respected as a free-form canvas size. This is redundant: providing both `width` and `height` already expresses clear intent. An LLM (or human) calling the tool with `width=1200, height=628` should not need to also know to pass `placement="custom"` — that is friction with no benefit.

Additionally, no validation exists on explicit pixel values. A caller can pass `width=1` or `height=50000`, producing output that is either aesthetically degenerate (too small for Mondrian cells to be visible) or impractically large for a presentation context. Guardrails should exist at the MCP tool boundary with clear, actionable error messages.

## What Changes

- **Implicit custom inference**: when both `width` and `height` are explicitly provided to `generate_mondrian`, the resolved dimensions are those values regardless of `placement`. `placement="custom"` continues to work but is no longer required.
- **Per-dimension validation**: the server enforces `100 ≤ width ≤ 4096` and `100 ≤ height ≤ 4096`. Values outside this range raise a `ValueError` with a clear message returned to the caller as an MCP tool error.
- **Scope**: presentation-oriented use cases. The floor (100px) excludes favicon/icon territory where Mondrian cells are not visible. The ceiling (4096px) covers 4K presentation formats with comfortable margin.

## Capabilities

### Modified Capabilities

- `mcp-server`: `generate_mondrian` tool gains implicit free-form dimension support and per-dimension validation.
- `placements`: `resolve_dimensions` gains implicit custom inference — when both `width` and `height` are provided, the preset is bypassed entirely (not just partially overridden).

## Impact

- `mondrian-mcp/server.py`: add `MIN_DIM`, `MAX_DIM` constants; validate resolved dimensions after `resolve_dimensions()`
- `mondrian-mcp/mondrian/placements.py`: update `resolve_dimensions()` to return `(width, height)` directly when both are provided, regardless of placement
- `mondrian-mcp/tests/test_placements.py`: add tests for implicit custom inference
- `mondrian-mcp/tests/test_server.py`: add tests for validation error messages
- No changes to `compose.py`, specs outside these two capabilities, or the `Placement` type literal
