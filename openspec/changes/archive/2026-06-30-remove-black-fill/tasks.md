## 1. Update palette

- [x] 1.1 In `mondrian-mcp/mondrian/compose.py`, remove `"black"` from `_COLORS` and update `_WEIGHTS` to `[0.15, 0.15, 0.15, 0.55]`

## 2. Update tests

- [x] 2.1 Update `VALID_COLORS` constant in `tests/test_compose.py` to remove `"black"` (keep `{"#c70000", "#f4b600", "#2d2bb4", "white"}`)
- [x] 2.2 Add a test asserting that `fill="black"` never appears on any cell `<rect>` across 50 sequential seeds

## 3. Verify output

- [x] 3.1 Run the full test suite (`uv run pytest`) and confirm all tests pass
- [x] 3.2 Regenerate the `mgmt-preso` images for the previously-broken seeds (1504381685, 1873178581, 73168152) and visually confirm they no longer appear predominantly black
