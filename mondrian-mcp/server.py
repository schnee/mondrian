"""
Mondrian MCP Server

Exposes a single MCP tool, generate_mondrian, that produces Piet Mondrian-style
generative art as a PNG image suitable for use in presentations.

Usage:
    uv run python server.py

Or as an installed entry point:
    mondrian-mcp
"""

import base64
from typing import Annotated, Literal

from fastmcp import FastMCP
from pydantic import Field

from mondrian.compose import Density, compose
from mondrian.placements import Placement, resolve_dimensions

mcp = FastMCP(
    name="mondrian-art",
    instructions=(
        "Generate Mondrian-style generative art for use in presentations. "
        "Use generate_mondrian to create PNG images with classic red, yellow, "
        "blue, black, and white rectilinear compositions. "
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
            description="Canvas width in pixels. Overrides the placement preset when provided.",
            gt=0,
        ),
    ] = None,
    height: Annotated[
        int | None,
        Field(
            default=None,
            description="Canvas height in pixels. Overrides the placement preset when provided.",
            gt=0,
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
) -> dict:
    """Generate a Mondrian-style rectilinear art composition as a PNG image.

    Returns a dictionary with:
    - 'png_base64': Base64-encoded PNG bytes of the generated art.
    - 'seed': The integer seed used for generation. Pass this back to reproduce the same image.
    - 'width': Actual canvas width in pixels.
    - 'height': Actual canvas height in pixels.

    The classic Mondrian palette is always used: red (#c70000), yellow (#f4b600),
    blue (#2d2bb4), black, and white (most common).
    """
    resolved_w, resolved_h = resolve_dimensions(placement, width, height)

    png_bytes, used_seed = compose(
        width=resolved_w,
        height=resolved_h,
        seed=seed,
        density=density,
        output_format="png",
    )

    return {
        "png_base64": base64.b64encode(png_bytes).decode("ascii"),
        "seed": used_seed,
        "width": resolved_w,
        "height": resolved_h,
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
