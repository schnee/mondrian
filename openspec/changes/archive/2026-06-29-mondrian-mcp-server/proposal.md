## Why

The existing R `mondrian` package generates Piet Mondrian-style generative art, but it is only usable within an R environment. Migrating the algorithm to Python and exposing it as an MCP tool enables AI agents (Devin, Claude) to programmatically generate and inject visual art into presentations — turning a standalone art script into a first-class agentic capability.

## What Changes

- Port the `compose()` algorithm from R to Python, preserving the original aesthetic behavior (weighted color sampling, overlapping/overwriting rectangles, variable line widths, random edge extension)
- Generate output as SVG (programmatic string construction) converted to PNG via `cairosvg`
- Expose the generator as an MCP server with a single `generate_mondrian` tool
- Support placement presets (`header_band`, `left_panel`, `full_bleed`, `square`, `custom`) as dimension shortcuts
- Support density presets (`sparse`, `normal`, `dense`) to control grid line count
- Return PNG bytes plus metadata (seed used) so callers can reproduce results

## Capabilities

### New Capabilities

- `art-generator`: Core Python port of the Mondrian composition algorithm — SVG construction from a random rectilinear grid with weighted color fills, variable-width lines, and overlapping rectangle drawing order
- `mcp-server`: MCP server wrapping the art generator as a callable tool, accepting parameters and returning PNG output with reproducibility metadata

### Modified Capabilities

## Impact

- New Python package (`mondrian-mcp/`) — no changes to existing R package
- New dependencies: `mcp` or `fastmcp`, `cairosvg`
- No Google Slides integration in this change (future work)
- Output is PNG bytes or file path; Slides injection is handled by the calling agent separately
