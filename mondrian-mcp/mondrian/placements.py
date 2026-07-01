"""
Placement presets mapping named slots to (width, height) canvas dimensions.

Designed for common Google Slides presentation use cases.
"""

from typing import Literal

Placement = Literal["header_band", "left_panel", "full_bleed", "square", "custom"]

PRESETS: dict[str, tuple[int, int]] = {
    "header_band": (960, 120),
    "left_panel": (200, 540),
    "full_bleed": (960, 540),
    "square": (400, 400),
}


def resolve_dimensions(
    placement: Placement,
    width: int | None = None,
    height: int | None = None,
) -> tuple[int, int]:
    """Resolve canvas dimensions from a placement preset and/or explicit values.

    Explicit width/height always override preset dimensions.
    For 'custom' placement, both width and height must be provided.

    Args:
        placement: Named preset or 'custom'.
        width: Explicit width override (pixels).
        height: Explicit height override (pixels).

    Returns:
        Resolved (width, height) tuple.

    Raises:
        ValueError: If placement is 'custom' and width or height is missing.
        ValueError: If placement is not a recognized preset.
    """
    # When both dimensions are explicitly provided, use them directly regardless
    # of placement. This makes free-form sizing work without requiring
    # placement="custom" — providing both width and height implies custom intent.
    if width is not None and height is not None:
        return width, height

    if placement == "custom":
        if width is None or height is None:
            raise ValueError(
                "placement='custom' requires explicit width and height parameters."
            )
        return width, height

    if placement not in PRESETS:
        valid = ", ".join(sorted(PRESETS.keys()) + ["custom"])
        raise ValueError(f"Unknown placement '{placement}'. Valid values: {valid}")

    preset_w, preset_h = PRESETS[placement]
    return (width if width is not None else preset_w), (height if height is not None else preset_h)
