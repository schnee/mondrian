## MODIFIED Requirements

### Requirement: Cell fills use weighted classic Mondrian palette
The system SHALL fill grid cells using the classic Mondrian palette — red (`#c70000`), yellow (`#f4b600`), blue (`#2d2bb4`), and white — with white being the most probable fill (weight 0.55) and the three primaries equally weighted at 0.15 each. Black SHALL NOT appear as a cell fill color; black is reserved exclusively for grid line strokes, consistent with Piet Mondrian's historical painting practice.

#### Scenario: Only palette colors appear in output
- **WHEN** a composition is generated with any seed
- **THEN** all `fill` attributes on cell `<rect>` elements are one of: `#c70000`, `#f4b600`, `#2d2bb4`, `white`

#### Scenario: Black never appears as a cell fill
- **WHEN** 50 compositions are generated with sequential seeds
- **THEN** no cell `<rect>` element has `fill="black"`

#### Scenario: White dominates over many samples
- **WHEN** 100 compositions are generated and fill colors are counted
- **THEN** white is the most frequently occurring fill color
