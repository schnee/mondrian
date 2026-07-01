# MCP Server Spec

## Purpose

TBD — Exposes the Mondrian art generator as an MCP tool, runnable as a standalone server process compatible with Claude Desktop, Devin, and other MCP clients.

## Requirements

### Requirement: Expose generate_mondrian as an MCP tool
The system SHALL expose a single MCP tool named `generate_mondrian` that accepts art generation parameters and returns the PNG as an MCP `ImageContent` block with reproducibility metadata in `structured_content`.

#### Scenario: Tool is discoverable via MCP
- **WHEN** an MCP client connects to the server and lists available tools
- **THEN** `generate_mondrian` appears in the tool list with a description and input schema

#### Scenario: Tool returns ImageContent block
- **WHEN** `generate_mondrian` is called with valid parameters
- **THEN** `result.content` contains exactly one item with `type="image"` and `mimeType="image/png"`

#### Scenario: PNG data is valid and non-empty
- **WHEN** `generate_mondrian` is called with valid parameters
- **THEN** `result.content[0].data` is a non-empty base64 string that decodes to a valid PNG

#### Scenario: Structured metadata is machine-readable
- **WHEN** `generate_mondrian(placement="square", seed=42)` is called
- **THEN** `result.structured_content` contains `{"seed": 42, "width": 400, "height": 400}`

#### Scenario: No png_base64 key in response
- **WHEN** `generate_mondrian` is called with valid parameters
- **THEN** `result.structured_content` does NOT contain a `png_base64` key

### Requirement: Tool accepts free-form pixel dimensions with guardrails
The system SHALL accept explicit `width` and `height` values as a free-form canvas size. When both are provided, the resolved dimensions SHALL be exactly those values, regardless of the `placement` parameter. Resolved dimensions SHALL be validated against presentation-oriented bounds: each dimension MUST be between 100 and 4096 pixels (inclusive). Values outside this range SHALL produce a tool error with a message of the form `"Width must be between 100 and 4096 pixels. Got: <value>."` or `"Height must be between 100 and 4096 pixels. Got: <value>."`.

The `placement="custom"` mode continues to function as before and is now equivalent to providing both `width` and `height` with any placement value.

#### Scenario: Both dimensions provided bypasses preset
- **WHEN** `generate_mondrian(width=1200, height=628)` is called without setting `placement="custom"`
- **THEN** the returned PNG has dimensions 1200 × 628

#### Scenario: Width below minimum is rejected
- **WHEN** `generate_mondrian(width=50, height=400)` is called
- **THEN** the tool returns an error indicating the width is below the minimum

#### Scenario: Height above maximum is rejected
- **WHEN** `generate_mondrian(width=400, height=5000)` is called
- **THEN** the tool returns an error indicating the height exceeds the maximum

#### Scenario: Boundary values are accepted
- **WHEN** `generate_mondrian(width=100, height=4096)` is called
- **THEN** the tool succeeds and returns a PNG with dimensions 100 × 4096

#### Scenario: Preset dimensions are implicitly valid
- **WHEN** any named placement preset is used without explicit dimensions
- **THEN** no validation error occurs (all preset dimensions are within bounds)

### Requirement: Tool accepts placement presets
The system SHALL accept a `placement` parameter that maps to standard (width, height) dimensions for common presentation use cases. Explicit `width` and `height` parameters SHALL override preset dimensions when provided.

**Placement presets:**
- `header_band`: 960 × 120
- `left_panel`: 200 × 540
- `full_bleed`: 960 × 540
- `square`: 400 × 400
- `custom`: requires explicit `width` and `height`

#### Scenario: Placement preset sets dimensions
- **WHEN** `generate_mondrian(placement="header_band")` is called without explicit width/height
- **THEN** the returned PNG has dimensions 960 × 120

#### Scenario: Explicit dimensions override preset
- **WHEN** `generate_mondrian(placement="header_band", width=1920, height=240)` is called
- **THEN** the returned PNG has dimensions 1920 × 240

#### Scenario: Custom placement requires explicit dimensions
- **WHEN** `generate_mondrian(placement="custom")` is called without width and height
- **THEN** the tool returns an error indicating that width and height are required for custom placement

### Requirement: Tool accepts density presets
The system SHALL accept a `density` parameter (`sparse`, `normal`, `dense`) that controls grid line frequency, defaulting to `normal`.

#### Scenario: Default density is normal
- **WHEN** `generate_mondrian(placement="square")` is called without a density parameter
- **THEN** the composition is generated with `normal` density

### Requirement: Tool accepts an optional seed for reproducibility
The system SHALL accept an optional integer `seed` parameter. When omitted, a seed SHALL be randomly chosen and returned in the response metadata so the caller can reproduce the result.

#### Scenario: Provided seed produces reproducible output
- **WHEN** `generate_mondrian(placement="square", seed=42)` is called twice
- **THEN** both calls return identical PNG bytes and both return `seed: 42` in metadata

#### Scenario: Omitted seed is auto-generated and returned
- **WHEN** `generate_mondrian(placement="square")` is called without a seed
- **THEN** the response includes a `seed` integer value that, when passed back, reproduces the same output

### Requirement: Server starts and is configurable via standard MCP mechanisms
The system SHALL be runnable as a standalone MCP server process, configurable for use with Claude Desktop, Devin, or any MCP-compatible client.

#### Scenario: Server starts without error
- **WHEN** `python server.py` (or equivalent entry point) is executed
- **THEN** the process starts and listens for MCP connections without error

#### Scenario: Server is documented for client configuration
- **WHEN** a user reads the README
- **THEN** they find instructions for adding the server to an MCP client configuration (e.g., Claude Desktop `mcp_servers` block)
