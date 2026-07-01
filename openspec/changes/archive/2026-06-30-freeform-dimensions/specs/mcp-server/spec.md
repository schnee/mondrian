## MODIFIED Requirements

### Requirement: Tool accepts free-form pixel dimensions with guardrails
The system SHALL accept explicit `width` and `height` values as a free-form canvas size. When both are provided, the resolved dimensions SHALL be exactly those values, regardless of the `placement` parameter. Resolved dimensions SHALL be validated against presentation-oriented bounds: each dimension MUST be between 100 and 4096 pixels (inclusive). Values outside this range SHALL produce a tool error with a message of the form `"Width must be between 100 and 4096 pixels. Got: <value>."` or `"Height must be between 100 and 4096 pixels. Got: <value>."`.

The `placement="custom"` mode continues to function as before and is now equivalent to providing both `width` and `height` with any placement value.

#### Scenario: Both dimensions provided bypasses preset
- **WHEN** `generate_mondrian(width=1200, height=628)` is called without setting `placement="custom"`
- **THEN** the returned PNG has dimensions 1200 × 628

#### Scenario: Width below minimum is rejected
- **WHEN** `generate_mondrian(width=50, height=400)` is called
- **THEN** the tool returns an error containing "Width must be between 100 and 4096 pixels. Got: 50."

#### Scenario: Height above maximum is rejected
- **WHEN** `generate_mondrian(width=400, height=5000)` is called
- **THEN** the tool returns an error containing "Height must be between 100 and 4096 pixels. Got: 5000."

#### Scenario: Boundary values are accepted
- **WHEN** `generate_mondrian(width=100, height=4096)` is called
- **THEN** the tool succeeds and returns a PNG with dimensions 100 × 4096

#### Scenario: Preset dimensions are implicitly valid
- **WHEN** any named placement preset is used without explicit dimensions
- **THEN** no validation error occurs (all preset dimensions are within bounds)
