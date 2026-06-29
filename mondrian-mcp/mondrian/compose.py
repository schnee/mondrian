"""
Mondrian-style generative art generator.

Faithful Python port of the R compose() function from the mondrian package.
Generates rectilinear compositions in the style of Piet Mondrian's
"Composition in Red, Blue, and Yellow".

Key aesthetic property preserved: cell rectangles are drawn with a randomly
sampled *other* grid line as the opposite corner, causing overlapping and
overwriting that gives the output an organic, painted feel.
"""

import random
from typing import Literal

# Classic Mondrian palette: red, yellow, blue, black, white
_COLORS = ["#c70000", "#f4b600", "#2d2bb4", "black", "white"]
# Matching weights: white most likely (0.50), black least likely (0.05)
_WEIGHTS = [0.15, 0.15, 0.15, 0.05, 0.50]

# Density multipliers applied to minDistApart
_DENSITY_MULTIPLIERS: dict[str, float] = {
    "sparse": 2.0,
    "normal": 1.0,
    "dense": 0.5,
}

Density = Literal["sparse", "normal", "dense"]
OutputFormat = Literal["svg", "png"]


def compose(
    width: int = 100,
    height: int = 100,
    fixed_lines: bool = False,
    seed: int | None = None,
    density: Density = "normal",
    output_format: OutputFormat = "svg",
) -> tuple[str | bytes, int]:
    """Generate a Mondrian-style composition.

    Args:
        width: Canvas width in pixels.
        height: Canvas height in pixels.
        fixed_lines: If True, all lines have the same width.
        seed: Random seed for reproducibility. If None, a seed is chosen
            randomly and returned in the result tuple.
        density: Grid line density — 'sparse', 'normal', or 'dense'.
        output_format: 'svg' returns an SVG string; 'png' returns PNG bytes.

    Returns:
        A tuple of (output, seed_used) where output is either an SVG string
        or PNG bytes depending on output_format, and seed_used is the integer
        seed that was used (useful when seed=None so the caller can reproduce).
    """
    if seed is None:
        seed = random.randint(0, 2**31 - 1)

    rng = random.Random(seed)

    multiplier = _DENSITY_MULTIPLIERS[density]
    min_dist = max(1, round(min(width, height) / 20 * multiplier))

    # --- Grid line sampling (faithful to R algorithm) ---
    # Number of lines: weighted toward fewer (prob ∝ 1/n)
    max_lines_x = max(2, width // min_dist)
    max_lines_y = max(2, height // min_dist)

    n_lines_x = _weighted_sample_count(rng, 2, max_lines_x)
    n_lines_y = _weighted_sample_count(rng, 2, max_lines_y)

    # Place lines at multiples of min_dist, no repeats
    x_positions = sorted(rng.sample(range(1, max_lines_x + 1), n_lines_x))
    x = [xi * min_dist for xi in x_positions]

    y_positions = sorted(rng.sample(range(1, max_lines_y + 1), n_lines_y))
    y = [yi * min_dist for yi in y_positions]

    # --- Line widths ---
    lw_min = round(min(width, height) / 20)
    lw_max = round(min(width, height) / 5)
    lw_min = max(1, lw_min)
    lw_max = max(lw_min, lw_max)

    if fixed_lines:
        line_width_x = [lw_min] * n_lines_x
        line_width_y = [lw_min] * n_lines_y
    else:
        line_width_x = [rng.randint(lw_min, lw_max) for _ in range(n_lines_x)]
        line_width_y = [rng.randint(lw_min, lw_max) for _ in range(n_lines_y)]

    # --- Random edge extension (four independent coin flips) ---
    if rng.random() < 0.5:
        x = [0] + x
        line_width_x = [0] + line_width_x
    if rng.random() < 0.5:
        x = x + [width]
        line_width_x = line_width_x + [0]
    if rng.random() < 0.5:
        y = [0] + y
        line_width_y = [0] + line_width_y
    if rng.random() < 0.5:
        y = y + [height]
        line_width_y = line_width_y + [0]

    # --- Build SVG ---
    svg = _build_svg(width, height, x, y, line_width_x, line_width_y, rng)

    if output_format == "png":
        import cairosvg  # lazy import — requires libcairo system library
        png_bytes = cairosvg.svg2png(bytestring=svg.encode("utf-8"))
        return png_bytes, seed

    return svg, seed


def _weighted_sample_count(rng: random.Random, lo: int, hi: int) -> int:
    """Sample an integer in [lo, hi] with probability ∝ 1/n (fewer is more likely)."""
    choices = list(range(lo, hi + 1))
    weights = [1.0 / n for n in choices]
    return rng.choices(choices, weights=weights, k=1)[0]


def _build_svg(
    width: int,
    height: int,
    x: list[int],
    y: list[int],
    line_width_x: list[int],
    line_width_y: list[int],
    rng: random.Random,
) -> str:
    """Construct the SVG string for a Mondrian composition.

    Drawing order:
    1. White background rect
    2. Cell fill rectangles (overlapping, in grid iteration order)
    3. Grid line rectangles (drawn on top of fills)
    """
    rects: list[str] = []

    # Background
    rects.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>')

    # --- Cell fills (overlapping draw order — the key aesthetic property) ---
    # For each (x[j], y[i]) pair, sample a random *other* x and y position
    # as the opposite corner. Later rects overwrite earlier ones.
    for i in range(len(y)):
        for j in range(len(x)):
            color = rng.choices(_COLORS, weights=_WEIGHTS, k=1)[0]

            # Sample opposite corner from other grid lines (excluding current)
            other_x_choices = [xk for k, xk in enumerate(x) if k != j]
            other_y_choices = [yk for k, yk in enumerate(y) if k != i]

            # Need at least one other line; if grid is degenerate, use edge
            x2 = rng.choice(other_x_choices) if other_x_choices else width
            y2 = rng.choice(other_y_choices) if other_y_choices else height

            rx = min(x[j], x2)
            ry = min(y[i], y2)
            rw = abs(x2 - x[j])
            rh = abs(y2 - y[i])

            if rw > 0 and rh > 0:
                rects.append(
                    f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" '
                    f'fill="{color}" stroke="black" stroke-width="1"/>'
                )

    # --- Grid lines as filled rectangles (centered on grid position) ---
    # Vertical lines
    for xi, lw in zip(x, line_width_x):
        if lw <= 0:
            continue
        rx = xi - lw // 2
        rects.append(
            f'<rect x="{rx}" y="0" width="{lw}" height="{height}" fill="black"/>'
        )

    # Horizontal lines
    for yi, lw in zip(y, line_width_y):
        if lw <= 0:
            continue
        ry = yi - lw // 2
        rects.append(
            f'<rect x="0" y="{ry}" width="{width}" height="{lw}" fill="black"/>'
        )

    elements = "\n  ".join(rects)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">\n  '
        f"{elements}\n</svg>"
    )
