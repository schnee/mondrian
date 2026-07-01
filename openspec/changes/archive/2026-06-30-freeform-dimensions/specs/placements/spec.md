## NEW Capability: Placements

### Requirement: Implicit free-form inference when both dimensions are provided
The system SHALL return `(width, height)` directly from `resolve_dimensions` when both `width` and `height` are non-None, regardless of the `placement` parameter value. This makes explicit dimension provision the highest-priority path, superseding both preset lookup and the `placement="custom"` requirement.

#### Scenario: Both dims provided with a named preset bypasses preset
- **WHEN** `resolve_dimensions("square", width=800, height=600)` is called
- **THEN** the result is `(800, 600)`, not `(800, 400)`

#### Scenario: Both dims provided with placement="custom" still works
- **WHEN** `resolve_dimensions("custom", width=800, height=600)` is called
- **THEN** the result is `(800, 600)` (hits implicit path before custom error check)

#### Scenario: One dim provided still uses preset as fallback
- **WHEN** `resolve_dimensions("square", width=800, height=None)` is called
- **THEN** the result is `(800, 400)` (preset height used as fallback)

#### Scenario: placement="custom" with missing dims still errors
- **WHEN** `resolve_dimensions("custom", width=None, height=None)` is called
- **THEN** a ValueError is raised indicating width and height are required
