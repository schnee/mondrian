"""Tests for the generate_mondrian MCP tool response shape."""

import asyncio
import base64
from io import BytesIO

import pytest
from PIL import Image as PILImage

from server import mcp


# Helper: call the tool and return a ToolResult
def call_tool(params: dict):
    async def _run():
        return await mcp.call_tool("generate_mondrian", params)
    return asyncio.run(_run())


# --- Response structure ---

def test_content_is_image_block():
    """content[0] must be an MCP ImageContent block."""
    result = call_tool({"placement": "square", "seed": 42})
    assert len(result.content) == 1
    assert result.content[0].type == "image"
    assert result.content[0].mimeType == "image/png"


def test_image_data_is_valid_png():
    """The base64 data in content[0] must decode to a valid PNG."""
    result = call_tool({"placement": "square", "seed": 42})
    png_bytes = base64.b64decode(result.content[0].data)
    img = PILImage.open(BytesIO(png_bytes))
    assert img.format == "PNG"


def test_structured_content_has_seed_width_height():
    """structured_content must contain seed, width, height as integers."""
    result = call_tool({"placement": "square", "seed": 42})
    sc = result.structured_content
    assert sc["seed"] == 42
    assert sc["width"] == 400
    assert sc["height"] == 400


def test_structured_content_no_png_base64_key():
    """structured_content must not contain the old png_base64 key."""
    result = call_tool({"placement": "square", "seed": 42})
    assert "png_base64" not in result.structured_content


def test_png_dimensions_match_placement():
    """PNG image dimensions must match the resolved preset dimensions."""
    result = call_tool({"placement": "header_band", "seed": 1})
    png_bytes = base64.b64decode(result.content[0].data)
    img = PILImage.open(BytesIO(png_bytes))
    assert img.width == 960
    assert img.height == 120


def test_auto_seed_is_returned():
    """When no seed is provided, structured_content must contain an integer seed."""
    result = call_tool({"placement": "square"})
    assert isinstance(result.structured_content["seed"], int)


def test_seeded_output_is_reproducible():
    """Two calls with the same seed must return identical image data."""
    r1 = call_tool({"placement": "square", "seed": 99})
    r2 = call_tool({"placement": "square", "seed": 99})
    assert r1.content[0].data == r2.content[0].data


def test_explicit_dimensions_override_preset():
    """Explicit width/height must override the placement preset."""
    result = call_tool({"placement": "square", "width": 200, "height": 100, "seed": 1})
    sc = result.structured_content
    assert sc["width"] == 200
    assert sc["height"] == 100
    png_bytes = base64.b64decode(result.content[0].data)
    img = PILImage.open(BytesIO(png_bytes))
    assert img.width == 200
    assert img.height == 100
