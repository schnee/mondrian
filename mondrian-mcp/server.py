"""
Mondrian MCP Server

Exposes a single MCP tool, generate_mondrian, that produces Piet Mondrian-style
generative art as a PNG image suitable for use in presentations.

Usage:
    uv run python server.py

Or as an installed entry point:
    mondrian-mcp
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.tools.base import ToolResult
from fastmcp.utilities.types import Image
from pydantic import Field

from mondrian.compose import Density, compose
from mondrian.placements import Placement, resolve_dimensions

# Presentation-oriented dimension bounds.
# Floor: below 100px, Mondrian cells are too small to be visible.
# Ceiling: 4096px covers 4K formats; beyond this, generation is slow
# and the PNG payload becomes impractical for MCP transport.
MIN_DIM = 100
MAX_DIM = 4096

mcp = FastMCP(
    name="mondrian-art",
    instructions=(
        "Generate Mondrian-style generative art for use in presentations. "
        "Use generate_mondrian to create PNG images with classic red, yellow, "
        "blue, and white rectilinear compositions. "
        "Choose a placement preset to get dimensions appropriate for common "
        "slide elements (header bands, side panels, full backgrounds)."
    ),
)


@mcp.tool()
def generate_mondrian(
    placement: Annotated[
        Placement,
        Field(
            default="square",
            description=(
                "Canvas size preset. Options: "
                "'header_band' (960×120, for slide title bars), "
                "'left_panel' (200×540, for side accent strips), "
                "'full_bleed' (960×540, for full slide backgrounds), "
                "'square' (400×400, for decorative insets), "
                "'custom' (requires explicit width and height)."
            ),
        ),
    ] = "square",
    width: Annotated[
        int | None,
        Field(
            default=None,
            description=(
                f"Canvas width in pixels ({MIN_DIM}–{MAX_DIM}). "
                "Overrides the placement preset width when provided. "
                "If both width and height are given, the placement preset is ignored entirely."
            ),
            ge=MIN_DIM,
            le=MAX_DIM,
        ),
    ] = None,
    height: Annotated[
        int | None,
        Field(
            default=None,
            description=(
                f"Canvas height in pixels ({MIN_DIM}–{MAX_DIM}). "
                "Overrides the placement preset height when provided. "
                "If both width and height are given, the placement preset is ignored entirely."
            ),
            ge=MIN_DIM,
            le=MAX_DIM,
        ),
    ] = None,
    seed: Annotated[
        int | None,
        Field(
            default=None,
            description=(
                "Integer seed for reproducibility. If omitted, a random seed is chosen "
                "and returned in the response so you can reproduce the same image later."
            ),
        ),
    ] = None,
    density: Annotated[
        Density,
        Field(
            default="normal",
            description=(
                "Grid line density. "
                "'sparse' produces fewer, wider cells; "
                "'normal' is the default; "
                "'dense' produces more lines and smaller cells."
            ),
        ),
    ] = "normal",
) -> ToolResult:
    """Generate a Mondrian-style rectilinear art composition as a PNG image.

    Returns a ToolResult with:
    - content[0]: MCP ImageContent block (type 'image', mimeType 'image/png') — the
      generated art, base64-encoded by FastMCP automatically.
    - structured_content: {'seed': int, 'width': int, 'height': int} — pass 'seed'
      back to reproduce the same image.

    The classic Mondrian palette is always used: red (#c70000), yellow (#f4b600),
    blue (#2d2bb4), and white (most common). Black appears only as grid line strokes.
    """
    resolved_w, resolved_h = resolve_dimensions(placement, width, height)

    if not (MIN_DIM <= resolved_w <= MAX_DIM):
        raise ValueError(
            f"Width must be between {MIN_DIM} and {MAX_DIM} pixels. Got: {resolved_w}."
        )
    if not (MIN_DIM <= resolved_h <= MAX_DIM):
        raise ValueError(
            f"Height must be between {MIN_DIM} and {MAX_DIM} pixels. Got: {resolved_h}."
        )

    png_bytes, used_seed = compose(
        width=resolved_w,
        height=resolved_h,
        seed=seed,
        density=density,
        output_format="png",
    )

    return ToolResult(
        content=[Image(data=png_bytes, format="png").to_image_content()],
        structured_content={
            "seed": used_seed,
            "width": resolved_w,
            "height": resolved_h,
        },
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
