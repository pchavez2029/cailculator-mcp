# CAILculator Examples

This directory contains example visualizations and usage demonstrations for the CAILculator MCP server.

## Visualizations

The `visualizations/` folder contains example outputs from the `illustrate` tool. These demonstrate the types of visualizations users can generate locally:

### zero_divisor_network_p1.png
Network graph showing basis element interactions for Canonical Six Pattern 1 in 32D pathions. Demonstrates how specific basis elements multiply to produce zero.

### canonical_six_universality.png
Bar chart comparing Chavez Transform values across all 6 Canonical patterns, demonstrating their mathematical universality (low coefficient of variation).

### e8_mandala_p4.png
E8 lattice projection in polar coordinates with Pattern 4 sector highlighted, showing the 8-fold symmetry characteristic of the E8 exceptional Lie algebra.

## Usage Examples

See the main [README.md](../README.md) for complete setup instructions.

### Example 1: Zero Divisor Detection
```python
# Via Claude Desktop MCP
"Find zero divisors in 32-dimensional pathions using Pattern 1"
```

### Example 2: Chavez Transform
```python
# Apply transform to time series data
"Apply Chavez Transform to this Bitcoin price data using Pattern 3"
```

### Example 3: Pattern Analysis
```python
# Detect mathematical patterns in data
"Detect patterns in this dataset and generate visualizations"
```

## Generating Your Own

All visualizations are generated locally on your machine using matplotlib. The `illustrate` tool automatically saves files to an `assets/visualizations/` directory in your working folder.

Example visualization request:
```
"Create a zero divisor network visualization for Pattern 4 in 64-dimensional space"
```

The tool will generate the PNG file and return the file path so you can view it.

---

**Chavez AI Labs** - *"Better math, less suffering"*
