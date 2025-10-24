# Assets Directory

This directory contains visualization assets and configuration for the CAILculator MCP server.

## Structure

```
assets/
├── static/          # Pre-rendered static images (PNG/SVG)
├── templates/       # Plot configuration templates
└── README.md        # This file
```

## Usage

### Static Images (Free Tier)

The `static/` directory stores pre-generated example visualizations for:
- Documentation and README files
- Marketing materials
- Quick preview images for free tier users

To generate static images, use the visualization module:

```python
from cailculator_mcp.visualizations import plot_canonical_six_universality, save_figure

pattern_values = {1: 0.777, 2: 0.777, 3: 0.777, 4: 0.777, 5: 0.777, 6: 0.777}
fig = plot_canonical_six_universality(pattern_values, interactive=False)
save_figure(fig, 'assets/static/canonical_six_universality.png', format='png')
```

### Templates

The `templates/` directory contains configuration files for consistent styling:
- `plot_config.json` - Default theme and plot configurations

### Tier System

**Free Tier**:
- Static matplotlib plots (PNG/SVG)
- Standard resolution (150 DPI)
- Basic color scheme
- No interactivity

**Premium Tier**:
- Interactive Plotly visualizations
- High resolution exports
- Custom color schemes
- Hover tooltips, zoom, pan
- Downloadable in multiple formats (PNG, SVG, HTML, PDF)

## Adding New Visualizations

1. Create plotting function in `src/cailculator_mcp/visualizations.py`
2. Add configuration to `templates/plot_config.json`
3. Generate example static image and save to `static/`
4. Update this README with usage example

## Example Visualizations

Place example images in `static/` for reference:
- `canonical_six_universality.png` - Purple bars showing pattern symmetry
- `alpha_sensitivity.png` - Transform vs convergence parameter
- `e8_comparison.png` - E8 vs canonical geometry comparison
- `comprehensive_analysis.png` - 6-panel summary figure

These examples demonstrate the transform's capabilities and serve as templates for user-generated visualizations.
