## Context

The existing R `mondrian` package has a single function `compose()` (~78 lines) that generates Piet Mondrian-style art using base R graphics. The goal is to port this to Python, expose it as an MCP tool, and preserve the original aesthetic — particularly the overlapping rectangle drawing order that gives the output its organic, painted feel.

The output will be consumed by AI agents (Devin, Claude) building Google Slides presentations. The agent calls the tool, receives a PNG, and handles Slides injection separately.

## Goals / Non-Goals

**Goals:**
- Faithful port of the R algorithm to Python (same aesthetic behavior)
- SVG as the intermediate format; PNG as final output via `cairosvg`
- MCP server with a single `generate_mondrian` tool
- Placement presets as dimension shortcuts for common slide use cases
- Density presets to control grid line count
- Seed-based reproducibility with seed returned in metadata

**Non-Goals:**
- Google Slides API integration (future change)
- Multiple color palettes (classic Mondrian only: `#c70000`, `#f4b600`, `#2d2bb4`, black, white)
- Image manipulation beyond generation (cropping, compositing, etc.)
- Streaming or async generation

## Decisions

### D1: SVG string construction over a graphics library

**Decision:** Generate SVG by constructing an XML string directly, not via matplotlib, PIL, or a drawing library.

**Rationale:** The Mondrian algorithm produces only rectangles. SVG `<rect>` elements map 1:1 to the algorithm's primitives. String construction has zero dependencies beyond stdlib, is fast, and produces clean, inspectable output. matplotlib would add significant weight and `plt.show()` / figure lifecycle complexity for no benefit.

**Alternatives considered:**
- `matplotlib` patches: heavier, stateful, harder to test
- `PIL/Pillow`: pixel-level drawing, no SVG output, harder to scale
- `svgwrite` library: unnecessary abstraction for this use case

### D2: Lines rendered as filled rectangles in SVG

**Decision:** Render grid lines as `<rect>` elements (filled black rectangles) rather than SVG `<line>` with `stroke-width`.

**Rationale:** The R code uses `lwd` (line width) on `abline`, which draws thick lines. SVG `stroke-width` on `<line>` clips differently at canvas edges and behaves inconsistently at intersections. Filled rectangles centered on the line position faithfully reproduce the thick-border aesthetic and give clean intersections.

**Alternative considered:** SVG `<line stroke-width>` — rejected due to edge clipping and intersection rendering differences.

### D3: `cairosvg` for SVG→PNG conversion

**Decision:** Use `cairosvg` for the SVG-to-PNG rasterization step.

**Rationale:** `cairosvg` is a well-maintained, pure-Python binding to Cairo. It handles SVG faithfully and is straightforward to use (`cairosvg.svg2png(bytestring=..., write_to=...)`). It is the simplest path to high-quality PNG output.

**Alternatives considered:**
- `svglib` + `reportlab`: more complex pipeline, less maintained
- Inkscape CLI: external process dependency, not suitable for a tool server
- `Pillow`: no SVG support natively

### D4: `fastmcp` over the official `mcp` SDK

**Decision:** Use `fastmcp` as the MCP server framework.

**Rationale:** `fastmcp` provides a cleaner, decorator-based API well-suited to small, single-tool servers. The official `mcp` SDK is more verbose for this use case. `fastmcp` is actively maintained and widely used.

**Alternative considered:** Official Anthropic `mcp` SDK — more boilerplate for equivalent functionality.

### D5: Placement presets as a thin dimension-mapping layer

**Decision:** `placement` is a parameter that maps to `(width, height)` defaults. If explicit `width`/`height` are provided, they take precedence. The generator itself is unaware of placement semantics.

**Rationale:** Keeps the core algorithm clean and reusable. The MCP tool layer handles the preset lookup. New presets can be added without touching the generator.

**Presets:**
```
header_band  →  960 × 120
left_panel   →  200 × 540
full_bleed   →  960 × 540
square       →  400 × 400
```

### D6: Preserve the overlapping rectangle drawing order

**Decision:** Port the R loop exactly — for each `(x[j], y[i])` grid intersection, sample a random *other* x and y line as the rectangle's opposite corner. Draw rectangles in loop order (later draws overwrite earlier ones).

**Rationale:** This is the core aesthetic property. It produces irregular, overlapping fills that look painted rather than tiled. A "clean" grid-fill approach would produce a fundamentally different visual style.

## Risks / Trade-offs

**[Risk] `cairosvg` requires system Cairo library** → On some systems `cairosvg` needs `libcairo` installed. Document in README; consider adding a check at server startup.

**[Risk] SVG viewBox vs pixel coordinates** → The algorithm works in pixel space. SVG output uses `viewBox="0 0 {width} {height}"` with matching `width`/`height` attributes. `cairosvg` respects this correctly; verify output dimensions in tests.

**[Risk] Line rectangle centering math** → Thick lines rendered as rectangles must be centered on the grid position (x - lw/2). Off-by-one errors here are visually obvious. Cover with snapshot tests.

**[Risk] R's `sample()` vs Python's `random.choices()`** → Seeds from R will not produce identical output in Python. This is expected and acceptable — seeds are for Python-side reproducibility only.

## Open Questions

- Should the tool return PNG as base64-encoded bytes in the JSON response, or write to a temp file and return the path? (Base64 is more portable for MCP tool responses; file path requires the caller to have filesystem access.)
- Should density presets (`sparse`/`normal`/`dense`) map to a multiplier on `minDistApart`, or to explicit line count ranges?
