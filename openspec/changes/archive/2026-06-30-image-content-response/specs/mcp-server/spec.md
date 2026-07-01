## MODIFIED Requirements

### Requirement: Tool returns image content block and structured metadata
The system SHALL return the generated PNG as an MCP `ImageContent` block (type `"image"`, mimeType `"image/png"`) in the tool response `content` array, and SHALL return `seed`, `width`, and `height` as integer fields in `structured_content`. The response SHALL NOT contain a `png_base64` key or any raw base64 string in the text content.

This replaces the previous requirement ("Tool returns PNG and metadata") which returned a JSON text block containing `png_base64`, `seed`, `width`, and `height`.

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
