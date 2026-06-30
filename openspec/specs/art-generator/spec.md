# Art Generator Spec

## Purpose

TBD — Generates Mondrian-style rectilinear compositions as SVG (and optionally PNG).

## Requirements

### Requirement: Generate a Mondrian composition as SVG
The system SHALL generate a Mondrian-style rectilinear composition as an SVG string given width, height, and optional seed parameters.

#### Scenario: Basic generation produces valid SVG
- **WHEN** `compose(width=960, height=540)` is called
- **THEN** the function returns a valid SVG string with a `viewBox="0 0 960 540"` attribute

#### Scenario: Seeded generation is reproducible
- **WHEN** `compose(width=400, height=400, seed=42)` is called twice with the same seed
- **THEN** both calls return identical SVG strings

#### Scenario: Unseeded generation is non-deterministic
- **WHEN** `compose(width=400, height=400)` is called twice without a seed
- **THEN** the two SVG strings are not required to be identical

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

### Requirement: Overlapping rectangle drawing order preserved
The system SHALL draw cell rectangles in grid iteration order (y-lines outer loop, x-lines inner loop), where each cell's opposite corner is sampled from a random other grid line, causing later rectangles to visually overwrite earlier ones.

#### Scenario: Rectangle corner sampled from other grid lines
- **WHEN** a cell at grid position `(x[j], y[i])` is drawn
- **THEN** its opposite corner `(x_other, y_other)` is sampled from `x` lines excluding `x[j]` and `y` lines excluding `y[i]`

### Requirement: Random edge extension
The system SHALL independently decide (with 50% probability each) whether to extend grid lines to each of the four canvas edges (left, right, top, bottom).

#### Scenario: Edge lines appear probabilistically
- **WHEN** 20 compositions are generated with the same width and height but different seeds
- **THEN** some compositions include a line at x=0 and some do not

### Requirement: Density controls grid line count
The system SHALL accept a density parameter (`sparse`, `normal`, `dense`) that adjusts the minimum distance between grid lines, producing fewer lines for `sparse` and more for `dense`.

#### Scenario: Sparse produces fewer lines than dense
- **WHEN** `compose(width=400, height=400, density="sparse", seed=1)` and `compose(width=400, height=400, density="dense", seed=1)` are compared
- **THEN** the sparse composition contains fewer total grid lines than the dense composition

### Requirement: SVG output converts to PNG
The system SHALL accept a flag or be callable in a mode that converts the SVG output to PNG bytes via `cairosvg`, at the requested pixel dimensions.

#### Scenario: PNG output has correct dimensions
- **WHEN** `compose(width=960, height=120, output_format="png")` is called
- **THEN** the returned PNG image has width=960 and height=120 pixels
