## ADDED Requirements

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
The system SHALL render horizontal and vertical grid lines as filled black `<rect>` elements centered on their grid position, with variable width controlled by the line weight parameter.

#### Scenario: Vertical line rendered as rectangle
- **WHEN** a vertical line at x=100 with weight 8 is drawn on a 400px canvas
- **THEN** the SVG contains a `<rect>` with `x="96"`, `width="8"`, `y="0"`, `height="400"`, `fill="black"`

#### Scenario: Line weight varies across lines
- **WHEN** `fixedLines=False` and the canvas is at least 100px in its smallest dimension
- **THEN** the SVG contains vertical and horizontal line rectangles with at least two distinct width values

### Requirement: Cell fills use weighted classic Mondrian palette
The system SHALL fill grid cells using the classic Mondrian palette — red (`#c70000`), yellow (`#f4b600`), blue (`#2d2bb4`), black, and white — with white being the most probable fill (weight 0.50) and black the least probable (weight 0.05).

#### Scenario: Only palette colors appear in output
- **WHEN** a composition is generated with any seed
- **THEN** all `fill` attributes on cell `<rect>` elements are one of: `#c70000`, `#f4b600`, `#2d2bb4`, `black`, `white`

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
