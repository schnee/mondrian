# Placements Spec

## Purpose

Resolves canvas dimensions from named placement presets and/or explicit pixel values. Designed for common presentation use cases (Google Slides, etc.).

## Requirements

### Requirement: Named presets map to standard presentation dimensions
The system SHALL provide a set of named placement presets that map to (width, height) canvas dimensions suited for common presentation slot types.

**Presets:**
- `header_band`: 960 × 120
- `left_panel`: 200 × 540
- `full_bleed`: 960 × 540
- `square`: 400 × 400
- `custom`: requires explicit width and height

#### Scenario: Preset resolves to correct dimensions
- **WHEN** `resolve_dimensions("header_band")` is called
- **THEN** the result is `(960, 120)`

### Requirement: Explicit dimensions override preset dimensions
The system SHALL use explicit `width` and/or `height` values in place of the corresponding preset dimension when provided.

#### Scenario: Width override
- **WHEN** `resolve_dimensions("square", width=800)` is called
- **THEN** the result is `(800, 400)`

#### Scenario: Height override
- **WHEN** `resolve_dimensions("square", height=300)` is called
- **THEN** the result is `(400, 300)`

### Requirement: Implicit free-form inference when both dimensions are provided
The system SHALL return `(width, height)` directly when both `width` and `height` are non-None, regardless of the `placement` parameter value. This makes free-form sizing work without requiring `placement="custom"` — providing both dimensions implies custom intent and supersedes preset lookup.

#### Scenario: Both dims with named preset bypasses preset
- **WHEN** `resolve_dimensions("square", width=800, height=600)` is called
- **THEN** the result is `(800, 600)`, not `(800, 400)`

#### Scenario: Both dims with placement="custom" still works
- **WHEN** `resolve_dimensions("custom", width=800, height=600)` is called
- **THEN** the result is `(800, 600)`

### Requirement: placement="custom" requires explicit dimensions
The system SHALL raise a `ValueError` when `placement="custom"` is used without providing both `width` and `height`.

#### Scenario: Custom with missing dims errors
- **WHEN** `resolve_dimensions("custom")` is called without width or height
- **THEN** a `ValueError` is raised indicating both are required
