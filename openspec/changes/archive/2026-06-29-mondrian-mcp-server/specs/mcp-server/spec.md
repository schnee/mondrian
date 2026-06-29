## ADDED Requirements

### Requirement: Expose generate_mondrian as an MCP tool
The system SHALL expose a single MCP tool named `generate_mondrian` that accepts art generation parameters and returns PNG output with reproducibility metadata.

#### Scenario: Tool is discoverable via MCP
- **WHEN** an MCP client connects to the server and lists available tools
- **THEN** `generate_mondrian` appears in the tool list with a description and input schema

#### Scenario: Tool returns PNG and metadata
- **WHEN** `generate_mondrian` is called with valid parameters
- **THEN** the response includes base64-encoded PNG bytes and a `seed` field containing the integer seed used for generation

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
