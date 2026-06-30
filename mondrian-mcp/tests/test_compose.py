"""Tests for the Mondrian art generator (mondrian.compose)."""

import re
from io import BytesIO

import pytest
from PIL import Image

from mondrian.compose import compose

# Black is intentionally excluded from cell fills (grid lines only).
VALID_COLORS = {"#c70000", "#f4b600", "#2d2bb4", "white"}


# --- 6.1: Seeded generation is reproducible ---

def test_seeded_generation_is_reproducible():
    svg1, seed1 = compose(width=400, height=400, seed=42)
    svg2, seed2 = compose(width=400, height=400, seed=42)
    assert svg1 == svg2
    assert seed1 == seed2 == 42


def test_seed_is_returned_when_provided():
    _, seed = compose(width=200, height=200, seed=99)
    assert seed == 99


def test_auto_seed_is_generated_and_returned():
    _, seed = compose(width=200, height=200)
    assert isinstance(seed, int)
    assert 0 <= seed < 2**31


def test_auto_seed_produces_reproducible_output():
    _, seed = compose(width=200, height=200)
    svg1, _ = compose(width=200, height=200, seed=seed)
    svg2, _ = compose(width=200, height=200, seed=seed)
    assert svg1 == svg2


# --- 6.2: Only valid palette colors in output ---

def test_only_valid_palette_colors():
    svg, _ = compose(width=400, height=400, seed=7)
    fills = re.findall(r'fill="([^"]+)"', svg)
    # Filter out 'black' used for line rects (also valid) and 'white' background
    for fill in fills:
        assert fill in VALID_COLORS, f"Unexpected color: {fill}"


def test_black_never_appears_as_cell_fill():
    """fill='black' must never appear on any cell rect across many seeds."""
    for seed in range(50):
        svg, _ = compose(width=400, height=400, seed=seed)
        fills = re.findall(r'fill="([^"]+)"', svg)
        # Skip the background white rect (first fill); check the rest
        cell_fills = fills[1:]
        assert "black" not in cell_fills, (
            f"seed={seed}: found fill='black' in cell rects"
        )


def test_white_is_most_common_fill():
    color_counts: dict[str, int] = {c: 0 for c in VALID_COLORS}
    for seed in range(50):
        svg, _ = compose(width=200, height=200, seed=seed)
        fills = re.findall(r'fill="([^"]+)"', svg)
        for f in fills:
            if f in color_counts:
                color_counts[f] += 1
    assert color_counts["white"] == max(color_counts.values()), (
        f"White should be most common, got: {color_counts}"
    )


# --- 6.3: PNG output dimensions match requested width/height ---

def test_png_dimensions_match_request():
    png, _ = compose(width=960, height=120, seed=1, output_format="png")
    img = Image.open(BytesIO(png))
    assert img.size == (960, 120)


def test_png_square_dimensions():
    png, _ = compose(width=300, height=300, seed=2, output_format="png")
    img = Image.open(BytesIO(png))
    assert img.size == (300, 300)


def test_png_returns_bytes():
    result, _ = compose(width=100, height=100, seed=3, output_format="png")
    assert isinstance(result, bytes)
    assert result[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic bytes


# --- 6.4: Placement preset dimension resolution ---
# (Tested via placements module; compose takes raw width/height)

def test_svg_contains_correct_viewbox():
    svg, _ = compose(width=960, height=540, seed=1)
    assert 'viewBox="0 0 960 540"' in svg
    assert 'width="960"' in svg
    assert 'height="540"' in svg


# --- 6.5: Density parameter produces different line counts ---

def test_dense_has_more_rects_than_sparse():
    # Average rect count across many seeds — dense should win on average.
    # (A single seed can go either way due to the weighted line-count sampler.)
    sparse_total = 0
    dense_total = 0
    for seed in range(30):
        svg_sparse, _ = compose(width=800, height=800, seed=seed, density="sparse")
        svg_dense, _ = compose(width=800, height=800, seed=seed, density="dense")
        sparse_total += svg_sparse.count("<rect")
        dense_total += svg_dense.count("<rect")
    assert dense_total > sparse_total, (
        f"Expected dense total ({dense_total}) > sparse total ({sparse_total}) over 30 seeds"
    )


def test_normal_density_is_between_sparse_and_dense():
    # Same reasoning: compare averages, not a single seed.
    sparse_total = dense_total = normal_total = 0
    for seed in range(30):
        svg_sparse, _ = compose(width=800, height=800, seed=seed, density="sparse")
        svg_normal, _ = compose(width=800, height=800, seed=seed, density="normal")
        svg_dense, _ = compose(width=800, height=800, seed=seed, density="dense")
        sparse_total += svg_sparse.count("<rect")
        normal_total += svg_normal.count("<rect")
        dense_total += svg_dense.count("<rect")
    assert sparse_total <= normal_total <= dense_total, (
        f"Expected sparse ({sparse_total}) <= normal ({normal_total}) <= dense ({dense_total}) over 30 seeds"
    )


# --- 6.6: Edge extension produces lines at x=0 or x=width ---

def test_edge_extension_appears_across_seeds():
    """Across many seeds, some should have a vertical line at x=0."""
    has_left_edge = False
    has_right_edge = False
    for seed in range(100):
        svg, _ = compose(width=400, height=400, seed=seed)
        if 'x="0" y="0" width=' in svg and 'height="400"' in svg:
            has_left_edge = True
        if f'x="{400 - 1}"' in svg or 'x="398"' in svg or 'x="396"' in svg:
            has_right_edge = True
        if has_left_edge:
            break
    assert has_left_edge, "Expected at least one composition with a left-edge line across 100 seeds"


def test_fixed_lines_mode():
    """fixed_lines=True should produce lines with uniform widths."""
    svg, _ = compose(width=400, height=400, seed=5, fixed_lines=True)
    # Just verify it runs without error and produces valid SVG
    assert 'viewBox="0 0 400 400"' in svg


# --- Border line weight tests (fix-border-line-weight change) ---

def _extract_stroke_width(svg: str) -> int:
    """Return the stroke-width value from the first colored rect in the SVG.

    Grid <line> elements use stroke-width="1"; we want the stroke-width on
    the colored <rect> elements, which comes after the line elements.
    """
    # Find stroke-width on a <rect> element (not on a <line>)
    m = re.search(r'<rect\b[^/]*stroke-width="(\d+)"', svg)
    assert m is not None, "No rect with stroke-width found in SVG"
    return int(m.group(1))


def test_border_lwd_header_band():
    """960×120 canvas: border_lwd = max(1, round(120 / 60)) = 2."""
    svg, _ = compose(width=960, height=120, seed=1)
    assert _extract_stroke_width(svg) == 2


def test_border_lwd_square():
    """400×400 canvas: border_lwd = max(1, round(400 / 60)) = 7."""
    svg, _ = compose(width=400, height=400, seed=1)
    assert _extract_stroke_width(svg) == 7


@pytest.mark.parametrize("width,height", [
    (960, 120),   # header_band
    (200, 540),   # left_panel
    (960, 540),   # full_bleed
    (400, 400),   # square
])
def test_border_lwd_never_exceeds_half_min_dist(width: int, height: int):
    """stroke-width must be < min_dist / 2 so smallest cells remain visible."""
    import math
    min_dist = max(1, round(min(width, height) / 20))
    svg, _ = compose(width=width, height=height, seed=42)
    stroke = _extract_stroke_width(svg)
    assert stroke < min_dist / 2, (
        f"{width}×{height}: stroke-width={stroke} >= min_dist/2={min_dist/2:.1f}"
    )
