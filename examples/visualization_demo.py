"""
Demonstration of CAILculator MCP visualization capabilities.

This script shows how to generate both free tier (static) and premium tier (interactive)
visualizations using the Chavez Transform.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from cailculator_mcp.visualizations import (
    plot_canonical_six_universality,
    plot_alpha_sensitivity,
    plot_dimensional_weighting,
    plot_e8_comparison,
    plot_kernel_localization,
    plot_comprehensive_analysis,
    save_figure,
    PLOTLY_AVAILABLE
)


def demo_canonical_six():
    """Demo: Canonical Six pattern universality (the purple bars)."""
    print("\n" + "="*80)
    print("DEMO 1: Canonical Six Pattern Universality")
    print("="*80)

    # All six patterns produce identical transform values
    pattern_values = {
        1: 7.771203e-01,
        2: 7.771203e-01,
        3: 7.771203e-01,
        4: 7.771203e-01,
        5: 7.771203e-01,
        6: 7.771203e-01,
    }

    print("Pattern values:")
    for p, v in pattern_values.items():
        print(f"  Pattern {p}: {v:.6e}")

    # Generate free tier static plot
    print("\nGenerating free tier (static) visualization...")
    fig_static = plot_canonical_six_universality(pattern_values, interactive=False)
    save_figure(fig_static, '../assets/static/canonical_six_universality.png')
    print("  ✓ Saved to assets/static/canonical_six_universality.png")

    # Generate premium tier interactive plot (if Plotly available)
    if PLOTLY_AVAILABLE:
        print("\nGenerating premium tier (interactive) visualization...")
        fig_interactive = plot_canonical_six_universality(pattern_values, interactive=True)
        save_figure(fig_interactive, '../assets/static/canonical_six_universality.html', format='html')
        print("  ✓ Saved to assets/static/canonical_six_universality.html")
    else:
        print("\n⚠️  Plotly not installed - premium tier unavailable")
        print("   Install with: pip install plotly")


def demo_alpha_sensitivity():
    """Demo: Transform sensitivity to alpha parameter."""
    print("\n" + "="*80)
    print("DEMO 2: Alpha Parameter Sensitivity")
    print("="*80)

    # Generate test data (matches research report behavior)
    alpha_values = np.logspace(-2, 2, 20)
    transform_values = 2.65 * np.exp(-0.5 * alpha_values)  # Exponential decay

    print(f"Testing {len(alpha_values)} alpha values from {alpha_values[0]:.3f} to {alpha_values[-1]:.1f}")
    print(f"Transform range: {transform_values.min():.3e} to {transform_values.max():.3e}")

    # Generate static plot
    print("\nGenerating visualization...")
    fig = plot_alpha_sensitivity(alpha_values, transform_values, optimal_alpha=0.01, interactive=False)
    save_figure(fig, '../assets/static/alpha_sensitivity.png')
    print("  ✓ Saved to assets/static/alpha_sensitivity.png")


def demo_e8_comparison():
    """Demo: E8 vs Canonical geometry comparison (Pattern 4 anomaly)."""
    print("\n" + "="*80)
    print("DEMO 3: E8 vs Canonical Geometry")
    print("="*80)

    # Data from performance report showing Pattern 4 amplification
    pattern_data = {
        1: {'canonical': 3.655e1, 'e8': 8.644e0},   # Dampening
        2: {'canonical': 7.170e1, 'e8': 9.597e0},   # Dampening
        3: {'canonical': 9.450e1, 'e8': 9.900e0},   # Dampening
        4: {'canonical': 1.866e1, 'e8': 3.274e1},   # AMPLIFICATION (175%)
        5: {'canonical': 2.756e1, 'e8': 1.526e1},   # Dampening
        6: {'canonical': 8.300e1, 'e8': 5.875e1},   # Dampening
    }

    print("Pattern comparison:")
    for p, vals in pattern_data.items():
        ratio = vals['e8'] / vals['canonical']
        effect = "AMPLIFY" if ratio > 1 else "DAMPEN"
        print(f"  Pattern {p}: Canonical={vals['canonical']:.2e}, E8={vals['e8']:.2e} ({ratio:.1%} - {effect})")

    # Generate visualization
    print("\nGenerating visualization...")
    fig = plot_e8_comparison(pattern_data, interactive=False)
    save_figure(fig, '../assets/static/e8_comparison.png')
    print("  ✓ Saved to assets/static/e8_comparison.png")
    print("\n⭐ DISCOVERY: Pattern 4 shows 175% amplification under E8 geometry!")


def demo_comprehensive():
    """Demo: Comprehensive 6-panel analysis figure."""
    print("\n" + "="*80)
    print("DEMO 4: Comprehensive Analysis (6-Panel Figure)")
    print("="*80)

    # Generate test data for all panels
    alpha_values = np.logspace(-2, 2, 20)
    alpha_transform = 2.65 * np.exp(-0.5 * alpha_values)

    d_values = np.arange(1, 11)
    d_transform = 0.842 - 0.033 * d_values

    x_spatial = np.linspace(-3, 3, 100)
    spatial_transform = 0.7 * np.exp(-x_spatial**2)

    x_kernel = np.linspace(-5, 5, 200)
    kernel_vals = np.exp(-x_kernel**2)

    freqs = np.linspace(0, 13, 100)
    fourier_mag = 45 * np.exp(-0.5 * freqs)

    pattern_values = {i: 7.771203e-01 for i in range(1, 7)}

    print("Generating comprehensive 6-panel analysis...")
    print("  Panel 1: Alpha sensitivity")
    print("  Panel 2: Dimensional weighting")
    print("  Panel 3: Fourier reference")
    print("  Panel 4: Spatial behavior")
    print("  Panel 5: Kernel localization")
    print("  Panel 6: Canonical Six universality")

    fig = plot_comprehensive_analysis(
        alpha_data=(alpha_values, alpha_transform),
        d_data=(d_values, d_transform),
        spatial_data=(x_spatial, spatial_transform),
        kernel_data=(x_kernel, kernel_vals),
        fourier_data=(freqs, fourier_mag),
        pattern_values=pattern_values,
        optimal_alpha=0.01
    )

    save_figure(fig, '../assets/static/comprehensive_analysis.png')
    print("\n  ✓ Saved to assets/static/comprehensive_analysis.png")


def main():
    print("="*80)
    print("CAILCULATOR MCP - VISUALIZATION DEMO")
    print("="*80)
    print("\nThis demo generates example visualizations for the Chavez Transform.")
    print("Free tier: Static PNG images")
    print("Premium tier: Interactive HTML plots (requires plotly)")

    # Create output directory if needed
    os.makedirs('../assets/static', exist_ok=True)

    # Run demos
    demo_canonical_six()
    demo_alpha_sensitivity()
    demo_e8_comparison()
    demo_comprehensive()

    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print("\nGenerated visualizations saved to: assets/static/")
    print("\nThese images demonstrate:")
    print("  ✓ Canonical Six universal symmetry (all patterns identical)")
    print("  ✓ Alpha parameter control (exponential decay)")
    print("  ✓ E8 geometric sensitivity (Pattern 4 amplification)")
    print("  ✓ Comprehensive multi-panel analysis")
    print("\nReady for MCP server integration!")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
