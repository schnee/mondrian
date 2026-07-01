## Why

The `generate_mondrian` tool currently returns a plain `dict` containing a raw base64-encoded PNG string alongside metadata. This means:

- The LLM sees a large base64 blob as text rather than an image content block
- MCP clients that support `ImageContent` (e.g. Claude) cannot render the image inline — they receive it as a JSON string
- The manual `base64.b64encode` call is unnecessary boilerplate that FastMCP can handle automatically

FastMCP 3.x provides `Image` (in `fastmcp.utilities.types`) and `ToolResult` (in `fastmcp.tools.base`) that together allow a tool to return a proper MCP `ImageContent` block alongside machine-readable structured metadata. This is the idiomatic FastMCP way to return binary media.

## What Changes

- Replace the `dict` return in `generate_mondrian` with a `ToolResult` containing:
  - An `ImageContent` block (via `Image.to_image_content()`) — the image as a proper MCP content block
  - `structured_content` dict with `seed`, `width`, and `height` — machine-readable metadata preserved for programmatic clients
- Remove the manual `base64` import from `server.py`
- Update the tool's docstring to reflect the new response shape
- Update tests to assert on the new response structure

## Capabilities

### Modified Capabilities

- `mcp-server`: The `generate_mondrian` tool's return format changes. The PNG is now returned as an MCP `ImageContent` block rather than a base64 string in a JSON field. Structured metadata (`seed`, `width`, `height`) is preserved in `structured_content`.

## Impact

- `mondrian-mcp/server.py`: replace `dict` return + manual base64 with `ToolResult` + `Image`
- `mondrian-mcp/tests/`: update any tests that assert on `png_base64` key or dict structure
- No changes to `mondrian/compose.py`, `mondrian/placements.py`, or any spec outside `mcp-server`
- No new dependencies — `fastmcp.utilities.types.Image` and `fastmcp.tools.base.ToolResult` are already available in the installed FastMCP 3.4.2
