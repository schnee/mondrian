## Context

Current `resolve_dimensions` behavior:

```
placement   width   height   result today
─────────   ─────   ──────   ────────────
"square"    -       -        400×400
"square"    800     -        800×400   (partial override)
"square"    -       300      400×300   (partial override)
"custom"    800     600      800×600   (explicit custom)
"custom"    -       -        ERROR     (custom needs dims)
"square"    800     600      800×600   (accidentally works —
                                        both dims override preset)
```

The accidental case ("square" + both dims) already resolves correctly because of how the preset fallback logic works. What's missing is:
1. Making this intentional and documented (not accidental)
2. Validation on the resolved values

## Goals / Non-Goals

**Goals:**
- When both `width` and `height` are provided, use them directly — placement is irrelevant
- `placement="custom"` continues to work (backward compat)
- Validate resolved dimensions: `100 ≤ w ≤ 4096`, `100 ≤ h ≤ 4096`
- Clear error messages: `"Width must be between 100 and 4096 pixels. Got: 50."`

**Non-Goals:**
- Changing the `Placement` type or removing `"custom"` from the literal
- Pixel budget / aspect ratio limits
- Changing any preset dimensions
- Touching `compose.py`

## Decision: Implicit inference lives in placements.py

**Chosen:** Add an early-return to `resolve_dimensions`: if both `width` and `height` are non-None, return them immediately regardless of `placement`.

**Rationale:** `resolve_dimensions` is the single place that interprets dimensions — it already handles the `custom` case explicitly. Adding implicit inference here keeps the logic co-located and means the server doesn't need to replicate dimension reasoning.

```python
# New early-return (before preset lookup):
if width is not None and height is not None:
    return width, height
```

This is a superset of the current `custom` behavior: `placement="custom"` with both dims provided hits this path and returns immediately (before the custom-specific error check). Backward compatible.

## Decision: Validation lives in server.py

**Chosen:** After `resolve_dimensions()` returns, validate in `generate_mondrian` before calling `compose()`.

**Rationale:** Validation is an MCP-layer concern — it's about what dimensions make sense for the tool's presentation-oriented use case, not about the art generation algorithm (which handles any positive integer). Keeping it in `server.py` means `compose.py` and `placements.py` remain general-purpose.

```python
MIN_DIM = 100
MAX_DIM = 4096

resolved_w, resolved_h = resolve_dimensions(placement, width, height)

if not (MIN_DIM <= resolved_w <= MAX_DIM):
    raise ValueError(
        f"Width must be between {MIN_DIM} and {MAX_DIM} pixels. Got: {resolved_w}."
    )
if not (MIN_DIM <= resolved_h <= MAX_DIM):
    raise ValueError(
        f"Height must be between {MIN_DIM} and {MAX_DIM} pixels. Got: {resolved_h}."
    )
```

FastMCP converts `ValueError` from a tool function into an MCP error response, so the message reaches the caller directly.

## Decision: MIN=100, MAX=4096

**MIN=100:**
- At 100px, `min_dist = round(100/20) = 5px`, `border_lwd = round(100/60) = 2px`
- Cells are visible and the composition reads as Mondrian
- Below 100px, cells become too small to distinguish from lines
- Excludes favicon/icon territory entirely
- All existing presets clear this floor (smallest preset dim = 120px on `header_band`)

**MAX=4096:**
- Covers 4K (3840×2160) with headroom
- At 4096×4096: ~0.4s generation, ~85KB PNG — well within MCP payload limits
- No presentation format legitimately needs more than 4K
- Keeps generation time under 1s for all valid inputs

## Behavior matrix after change

```
placement   width   height   result
─────────   ─────   ──────   ──────
"square"    -       -        400×400   (preset, unchanged)
"square"    800     -        800×400   (partial override, unchanged)
"square"    -       300      400×300   (partial override, unchanged)
"custom"    800     600      800×600   (explicit custom, unchanged)
"custom"    -       -        ERROR     (custom still needs dims)
any         800     600      800×600   (NEW: both provided → direct)
any         50      600      ERROR     (NEW: 50 < MIN_DIM)
any         800     5000     ERROR     (NEW: 5000 > MAX_DIM)
```

## Field description updates

The `width` and `height` field descriptions in `generate_mondrian` should be updated to:
- State the min/max bounds
- Make clear that providing both bypasses the preset entirely
