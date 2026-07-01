"""Tests for placement preset resolution (mondrian.placements)."""

import pytest

from mondrian.placements import resolve_dimensions


# --- Preset resolution ---

def test_header_band_preset():
    w, h = resolve_dimensions("header_band")
    assert (w, h) == (960, 120)


def test_left_panel_preset():
    w, h = resolve_dimensions("left_panel")
    assert (w, h) == (200, 540)


def test_full_bleed_preset():
    w, h = resolve_dimensions("full_bleed")
    assert (w, h) == (960, 540)


def test_square_preset():
    w, h = resolve_dimensions("square")
    assert (w, h) == (400, 400)


# --- Explicit dims override preset ---

def test_explicit_width_overrides_preset():
    w, h = resolve_dimensions("header_band", width=1920)
    assert w == 1920
    assert h == 120  # height still from preset


def test_explicit_height_overrides_preset():
    w, h = resolve_dimensions("header_band", height=240)
    assert w == 960  # width still from preset
    assert h == 240


def test_both_explicit_override_preset():
    w, h = resolve_dimensions("header_band", width=1920, height=240)
    assert (w, h) == (1920, 240)


# --- Custom placement ---

def test_custom_requires_both_dimensions():
    with pytest.raises(ValueError, match="requires explicit width and height"):
        resolve_dimensions("custom")


def test_custom_requires_width():
    with pytest.raises(ValueError, match="requires explicit width and height"):
        resolve_dimensions("custom", height=300)


def test_custom_requires_height():
    with pytest.raises(ValueError, match="requires explicit width and height"):
        resolve_dimensions("custom", width=400)


def test_custom_with_both_dimensions():
    w, h = resolve_dimensions("custom", width=1280, height=720)
    assert (w, h) == (1280, 720)


# --- Implicit free-form inference (both dims provided) ---

def test_both_dims_with_named_preset_bypasses_preset():
    """When both width and height are provided, the preset is ignored entirely."""
    w, h = resolve_dimensions("square", width=800, height=600)
    assert (w, h) == (800, 600)


def test_both_dims_with_custom_placement_still_works():
    """Both dims + placement='custom' hits the implicit path before custom error check."""
    w, h = resolve_dimensions("custom", width=800, height=600)
    assert (w, h) == (800, 600)


def test_both_dims_with_header_band_bypasses_preset():
    """Any named preset is bypassed when both dims are given."""
    w, h = resolve_dimensions("header_band", width=1920, height=240)
    assert (w, h) == (1920, 240)


def test_one_dim_still_uses_preset_as_fallback():
    """Only width provided — preset height is still used."""
    w, h = resolve_dimensions("square", width=800)
    assert (w, h) == (800, 400)


def test_other_one_dim_still_uses_preset_as_fallback():
    """Only height provided — preset width is still used."""
    w, h = resolve_dimensions("square", height=300)
    assert (w, h) == (400, 300)


# --- Invalid placement ---

def test_unknown_placement_raises():
    with pytest.raises(ValueError, match="Unknown placement"):
        resolve_dimensions("diagonal_stripe")  # type: ignore[arg-type]
