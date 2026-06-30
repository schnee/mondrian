## 1. Fix border_lwd formula

- [x] 1.1 In `mondrian-mcp/mondrian/compose.py`, change `border_lwd = max(1, round(min(width, height) / 20))` to `border_lwd = max(1, round(min(width, height) / 60))`

## 2. Update tests

- [x] 2.1 Update any existing test that asserts a specific `stroke-width` value to match the new formula (divisor 60)
- [x] 2.2 Add a test asserting that `stroke-width` equals `max(1, round(120 / 60)) = 2` for a 960×120 canvas
- [x] 2.3 Add a test asserting that `stroke-width` equals `max(1, round(400 / 60)) = 7` for a 400×400 canvas
- [x] 2.4 Add a parameterized test asserting that `stroke-width < min_dist / 2` for all placement preset dimensions at normal density

## 3. Verify output

- [x] 3.1 Run the full test suite (`uv run pytest`) and confirm all tests pass
- [x] 3.2 Manually generate a `header_band` PNG and visually confirm colored cells are visible (not a black band)
