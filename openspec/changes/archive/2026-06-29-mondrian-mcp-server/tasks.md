## 1. Project Setup

- [x] 1.1 Create `mondrian-mcp/` directory structure: `mondrian/`, `tests/`, `pyproject.toml`
- [x] 1.2 Add dependencies to `pyproject.toml`: `fastmcp`, `cairosvg`
- [x] 1.3 Create `mondrian/__init__.py` and `mondrian/compose.py` stubs

## 2. Art Generator — Core Algorithm

- [x] 2.1 Implement grid line sampling: random number of lines weighted toward fewer, spaced by `minDistApart`
- [x] 2.2 Implement variable line widths (random range based on canvas size) and `fixedLines` mode
- [x] 2.3 Implement random edge extension (four independent coin flips for left/right/top/bottom)
- [x] 2.4 Implement overlapping cell fill loop: for each `(x[j], y[i])`, sample opposite corner from other grid lines, assign weighted color
- [x] 2.5 Implement density parameter: map `sparse`/`normal`/`dense` to `minDistApart` multipliers

## 3. Art Generator — SVG Output

- [x] 3.1 Build SVG `<rect>` elements for grid lines (centered filled rectangles, not `<line>` strokes)
- [x] 3.2 Build SVG `<rect>` elements for cell fills with correct colors and z-order (lines drawn last, on top)
- [x] 3.3 Assemble complete SVG string with correct `viewBox`, `width`, `height` attributes
- [x] 3.4 Integrate `cairosvg.svg2png()` to convert SVG string to PNG bytes
- [x] 3.5 Return PNG bytes and the seed used (auto-generate seed if none provided)

## 4. Placement Presets

- [x] 4.1 Implement `placements.py` mapping preset names to `(width, height)` tuples
- [x] 4.2 Validate that `placement="custom"` requires explicit `width` and `height`, raising a clear error otherwise

## 5. MCP Server

- [x] 5.1 Create `server.py` with `fastmcp` server instance
- [x] 5.2 Define `generate_mondrian` tool with typed parameters: `placement`, `width`, `height`, `seed`, `density`
- [x] 5.3 Wire tool to art generator: resolve placement → dimensions, call `compose()`, return base64 PNG + seed metadata
- [x] 5.4 Add tool description and parameter docstrings suitable for agent consumption

## 6. Tests

- [x] 6.1 Test seeded generation is reproducible (same seed → identical SVG)
- [x] 6.2 Test only valid palette colors appear in SVG fill attributes
- [x] 6.3 Test PNG output dimensions match requested width/height
- [x] 6.4 Test placement preset dimension resolution (including custom error case)
- [x] 6.5 Test density parameter produces different line counts (sparse < dense)
- [x] 6.6 Test edge extension produces lines at x=0 or x=width across multiple seeds

## 7. Documentation and Configuration

- [x] 7.1 Write `README.md` with installation instructions (including `libcairo` system dependency note)
- [x] 7.2 Add MCP client configuration example (Claude Desktop `mcp_servers` block, Devin MCP config)
- [x] 7.3 Add a usage example showing `generate_mondrian` call and sample output
