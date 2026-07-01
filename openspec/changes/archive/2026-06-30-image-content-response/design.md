## Context

Current `generate_mondrian` return path in `server.py`:

```python
import base64
...
return {
    "png_base64": base64.b64encode(png_bytes).decode("ascii"),
    "seed": used_seed,
    "width": resolved_w,
    "height": resolved_h,
}
```

FastMCP serializes a `dict` return into both `content` (JSON text block) and `structured_content`. The PNG arrives at the client as a base64 string inside a JSON object — not as an MCP `ImageContent` block. Claude and other MCP clients that support inline image rendering cannot use it directly.

Empirically verified (FastMCP 3.4.2) that `ToolResult` with `ImageContent` + `structured_content` produces:

```json
{
  "content": [
    { "type": "image", "data": "<base64>", "mimeType": "image/png" }
  ],
  "structuredContent": {
    "seed": 42,
    "width": 400,
    "height": 400
  }
}
```

This is exactly what we want: the image is a first-class MCP content block, and the metadata is machine-readable.

## Goals / Non-Goals

**Goals:**
- Return the PNG as an MCP `ImageContent` block
- Preserve `seed`, `width`, `height` as structured metadata in `structured_content`
- Remove the manual `base64` import
- Keep the public tool signature (parameters) identical — this is a response shape change only

**Non-Goals:**
- Changing the `list[Image | str]` pattern suggested in the exploration (loses `structured_content`)
- Adding new parameters or presets
- Changing `compose.py` or `placements.py`

## Decision: ToolResult over list[Image | str]

**Chosen:** `ToolResult(content=[image.to_image_content()], structured_content={...})`

**Rationale:** The `list[Image | str]` pattern explored during investigation produces `structured_content: None` — the metadata becomes a freeform text string that clients must parse. `ToolResult` gives us both the `ImageContent` block and properly typed structured metadata simultaneously. It is also the explicit, fully-controlled form that FastMCP docs recommend when you need both content types in one response.

**New return shape:**

```python
from fastmcp.tools.base import ToolResult
from fastmcp.utilities.types import Image

mondrian_image = Image(data=png_bytes, format="png")
return ToolResult(
    content=[mondrian_image.to_image_content()],
    structured_content={
        "seed": used_seed,
        "width": resolved_w,
        "height": resolved_h,
    },
)
```

## Import changes

Remove:
```python
import base64
```

Add:
```python
from fastmcp.tools.base import ToolResult
from fastmcp.utilities.types import Image
```

## Test impact

Tests that currently assert on `result["png_base64"]`, `result["seed"]`, etc. will break. The new assertions are:

- `result.content[0].type == "image"`
- `result.content[0].mimeType == "image/png"`
- `result.structured_content["seed"]` is an int
- `result.structured_content["width"]` and `["height"]` match the requested dimensions
- `"png_base64"` key no longer present

## Risks

- **Client compatibility:** Any client that was reading `png_base64` from the JSON dict will break. This is intentional — the old response shape was not idiomatic MCP. The new shape is.
- **No new dependencies:** `Image` and `ToolResult` are already in FastMCP 3.4.2.
