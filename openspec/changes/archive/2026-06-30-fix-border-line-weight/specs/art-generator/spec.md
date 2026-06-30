## MODIFIED Requirements

### Requirement: Grid lines rendered as filled rectangles
The system SHALL render horizontal and vertical grid lines as SVG `stroke` on colored `<rect>` elements, with stroke-width computed as `max(1, round(min(width, height) / 60))`. This produces line weight proportional to ~1.7% of the minimum canvas dimension, consistent with real Mondrian painting proportions and ensuring the stroke never obliterates the smallest colored cells on any supported placement preset.

#### Scenario: Vertical line rendered as rectangle
- **WHEN** a vertical line at x=100 with weight 8 is drawn on a 400px canvas
- **THEN** the SVG contains a `<rect>` with `x="96"`, `width="8"`, `y="0"`, `height="400"`, `fill="black"`

#### Scenario: Line weight scales with canvas minimum dimension
- **WHEN** `compose(width=960, height=120)` is called
- **THEN** the SVG `stroke-width` on colored rects equals `2` (i.e., `round(120 / 60)`)

#### Scenario: Line weight scales correctly for square canvas
- **WHEN** `compose(width=400, height=400)` is called
- **THEN** the SVG `stroke-width` on colored rects equals `7` (i.e., `round(400 / 60)`)

#### Scenario: Line weight never exceeds half the minimum cell size
- **WHEN** `compose()` is called with any placement preset dimensions and `density="normal"`
- **THEN** the `stroke-width` value is strictly less than `min_dist / 2`, where `min_dist = round(min(width, height) / 20)`, ensuring colored fill remains visible in the smallest cells

#### Scenario: Line weight varies across canvas sizes for organic feel
- **WHEN** compositions are generated at `header_band` (960×120), `square` (400×400), and `full_bleed` (960×540) dimensions
- **THEN** the `stroke-width` values differ across the three outputs, reflecting proportional scaling to each canvas
