## 1. placements.py — implicit free-form inference

- [x] 1.1 Add early-return to `resolve_dimensions`: if both `width` and `height` are non-None, return `(width, height)` immediately (before preset lookup and before custom error check)

## 2. server.py — validation and field description updates

- [x] 2.1 Add constants `MIN_DIM = 100` and `MAX_DIM = 4096` near the top of `server.py`
- [x] 2.2 After `resolve_dimensions()`, validate `MIN_DIM <= resolved_w <= MAX_DIM` and `MIN_DIM <= resolved_h <= MAX_DIM`; raise `ValueError` with message `"Width must be between {MIN_DIM} and {MAX_DIM} pixels. Got: {resolved_w}."` (and equivalent for height)
- [x] 2.3 Update `width` field description to state bounds and note that providing both width and height bypasses the placement preset
- [x] 2.4 Update `height` field description to match

## 3. Tests

- [x] 3.1 In `tests/test_placements.py`: add tests for implicit inference — both dims with a named preset returns those dims; one dim still uses preset as fallback
- [x] 3.2 In `tests/test_server.py`: add tests for width below MIN_DIM, height above MAX_DIM, and boundary values (100 and 4096) being accepted
- [x] 3.3 In `tests/test_server.py`: add test that free-form `width=1200, height=628` (no `placement="custom"`) returns a PNG of the correct size

## 4. Verify

- [x] 4.1 Run `uv run pytest` and confirm all tests pass
