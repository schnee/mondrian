## 1. Update server.py

- [x] 1.1 Add imports: `from fastmcp.tools.base import ToolResult` and `from fastmcp.utilities.types import Image`
- [x] 1.2 Remove `import base64`
- [x] 1.3 Replace the `dict` return with `ToolResult(content=[Image(data=png_bytes, format="png").to_image_content()], structured_content={"seed": used_seed, "width": resolved_w, "height": resolved_h})`
- [x] 1.4 Update the return type annotation from `-> dict` to `-> ToolResult`
- [x] 1.5 Update the tool docstring to reflect the new response shape

## 2. Update tests

- [x] 2.1 In `tests/test_server.py` (or equivalent), update assertions that check for `result["png_base64"]` to instead assert on `result.content[0].type == "image"` and `result.content[0].mimeType == "image/png"`
- [x] 2.2 Update assertions that check `result["seed"]`, `result["width"]`, `result["height"]` to use `result.structured_content["seed"]` etc.
- [x] 2.3 Add assertion that `result.structured_content` does not contain `"png_base64"`

## 3. Verify

- [x] 3.1 Run `uv run pytest` and confirm all tests pass
