# mondrian-mcp

A Python MCP server that generates Piet Mondrian-style generative art as PNG images.
Use it with AI agents (Devin, Claude) to decorate presentations with classic rectilinear
compositions in red, yellow, blue, black, and white.

Port of the [mondrian R package](https://github.com/schnee/mondrian), preserving the
original algorithm's overlapping rectangle drawing order for an organic, painted feel.

## Requirements

### System dependency: libcairo

`cairosvg` (used for SVG→PNG conversion) requires the Cairo graphics library.

**macOS (Homebrew):**
```bash
brew install cairo
```

**Linux (apt):**
```bash
sudo apt-get install libcairo2
```

**Linux (yum/dnf):**
```bash
sudo dnf install cairo
```

### Python

Python 3.10 or later is required. [uv](https://docs.astral.sh/uv/) is recommended for
environment management and is used in all examples below.

## Installation

```bash
# Clone the repo (or cd into the mondrian-mcp/ directory)
cd mondrian-mcp

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (Python 3.12 will be fetched automatically if needed)
uv sync --python 3.12
```

## Usage

### As an MCP server

```bash
uv run python server.py
```

The server communicates over stdio using the MCP protocol.

### Quick test

```bash
uv run python -c "
from mondrian.compose import compose
svg, seed = compose(width=960, height=120, seed=42)
print('Generated SVG, seed:', seed)
with open('/tmp/mondrian_test.svg', 'w') as f:
    f.write(svg)
print('Saved to /tmp/mondrian_test.svg')
"
```

## The `generate_mondrian` tool

### Parameters

| Parameter   | Type    | Default       | Description |
|-------------|---------|---------------|-------------|
| `placement` | string  | `"square"`    | Canvas size preset (see below) |
| `width`     | integer | from preset   | Override canvas width in pixels |
| `height`    | integer | from preset   | Override canvas height in pixels |
| `seed`      | integer | random        | Seed for reproducibility; returned in response |
| `density`   | string  | `"normal"`    | Grid line density: `sparse`, `normal`, `dense` |

### Placement presets

| Preset        | Dimensions  | Use case |
|---------------|-------------|----------|
| `header_band` | 960 × 120   | Slide title bar / header strip |
| `left_panel`  | 200 × 540   | Side accent column |
| `full_bleed`  | 960 × 540   | Full slide background |
| `square`      | 400 × 400   | Decorative inset or icon area |
| `custom`      | you provide | Any size; requires explicit `width` and `height` |

### Response

```json
{
  "png_base64": "<base64-encoded PNG>",
  "seed": 42,
  "width": 960,
  "height": 120
}
```

Save the `seed` to reproduce the exact same image later.

## MCP Client Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mondrian-art": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mondrian-mcp", "python", "server.py"],
      "env": {
        "DYLD_LIBRARY_PATH": "/opt/homebrew/lib"
      }
    }
  }
}
```

Replace `/path/to/mondrian-mcp` with the absolute path to this directory.

### Devin / Windsurf MCP config

Add to your MCP configuration (e.g. `.devin/config.json`):

```json
{
  "mcpServers": {
    "mondrian-art": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mondrian-mcp", "python", "server.py"],
      "env": {
        "DYLD_LIBRARY_PATH": "/opt/homebrew/lib"
      }
    }
  }
}
```

> **Note (macOS):** The `DYLD_LIBRARY_PATH` env var is required so `cairosvg` can find
> the Homebrew-installed `libcairo`. This must be set in the MCP client config's `env`
> block (not just in your shell profile), as MCP servers are launched as child processes.

### Linux

On Linux, `libcairo` is found automatically via the system linker. No `DYLD_LIBRARY_PATH`
is needed. The `env` block can be omitted.

## Example agent interaction

```
User: Create a header banner for my presentation slide about machine learning.

Agent: [calls generate_mondrian with placement="header_band", density="normal"]

Response: {
  "png_base64": "iVBORw0KGgo...",
  "seed": 1847392,
  "width": 960,
  "height": 120
}

Agent: Generated a 960×120 Mondrian header band (seed: 1847392).
       Use seed 1847392 to reproduce this exact image.
```

## Development

```bash
# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/test_compose.py -v
```

## Algorithm

Faithful Python port of the R `compose()` function:

1. Sample a random number of horizontal and vertical grid lines (weighted toward fewer)
2. Place lines at multiples of `minDistApart` (adjusted by density)
3. Randomly assign variable line widths
4. Independently decide (50% each) whether to extend lines to each canvas edge
5. For each grid cell `(x[j], y[i])`, sample a random *other* x and y line as the
   opposite rectangle corner, assign a weighted color, draw — later rectangles overwrite
   earlier ones, creating the characteristic organic overlap
6. Draw thick grid lines on top as filled black rectangles
7. Render SVG → PNG via `cairosvg`

**Color palette** (classic Mondrian, fixed — no customization):
- White (50% probability)
- Red `#c70000` (15%)
- Yellow `#f4b600` (15%)
- Blue `#2d2bb4` (15%)
- Black (5%)
