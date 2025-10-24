#!/usr/bin/env python3
"""
Create Example Visualizations for CAILculator MCP

Generates 3 marketing-ready visualizations showcasing key features:
1. Zero Divisor Network - Shows pattern structure
2. Canonical Six Universality - Demonstrates pattern consistency
3. E8 Mandala - Highlights exceptional Lie algebra connection

Output: Small PNGs (~50-100KB each) in examples/visualizations/
"""

import sys
import os
from pathlib import Path

# Add parent src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Output directory
OUTPUT_DIR = Path(__file__).parent / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)

# Small figure size for compact files
FIG_SIZE = (8, 6)
DPI = 100  # Lower DPI = smaller files

# Marketing color scheme - "Colors of impossibility"
COLORS = {
    'primary': '#8B5CF6',    # Purple
    'secondary': '#3B82F6',  # Blue
    'accent': '#F59E0B',     # Gold
    'background': '#1F2937', # Dark gray
}

def create_zero_divisor_network():
    """
    Example 1: Zero Divisor Network Visualization
    Shows the structure of Canonical Six Pattern #1
    """
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)

    # Canonical Six Pattern #1: (e4 + e11) × (e1 - e14) = 0
    # Visualize as a simple network

    positions = {
        'e₄': (0, 1),
        'e₁₁': (0, -1),
        'e₁': (2, 1),
        'e₁₄': (2, -1),
        'P': (0.5, 0),
        'Q': (1.5, 0),
        '0': (3, 0),
    }

    # Draw nodes
    for label, (x, y) in positions.items():
        if label in ['P', 'Q']:
            color = COLORS['primary']
            size = 1000
        elif label == '0':
            color = COLORS['accent']
            size = 1200
        else:
            color = COLORS['secondary']
            size = 700

        ax.scatter(x, y, s=size, c=color, alpha=0.9, edgecolors='white', linewidth=2.5)
        ax.text(x, y, label, ha='center', va='center', color='white',
                fontweight='bold', fontsize=13)

    # Draw connections
    connections = [
        ('e₄', 'P'), ('e₁₁', 'P'),   # P = e4 + e11
        ('e₁', 'Q'), ('e₁₄', 'Q'),   # Q = e1 - e14
        ('P', '0'), ('Q', '0'),      # P × Q = 0
    ]

    for start, end in connections:
        x_values = [positions[start][0], positions[end][0]]
        y_values = [positions[start][1], positions[end][1]]
        ax.plot(x_values, y_values, 'w-', alpha=0.4, linewidth=2.5)

    # Styling
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-1.8, 1.8)
    ax.set_facecolor(COLORS['background'])
    ax.set_title('Zero Divisor Network: Pattern 1\n(e₄ + e₁₁) × (e₁ - e₁₄) = 0',
                 color='white', fontsize=15, pad=20, fontweight='bold')
    ax.axis('off')
    fig.patch.set_facecolor(COLORS['background'])

    output_path = OUTPUT_DIR / "zero_divisor_network_p1.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=COLORS['background'])
    plt.close()

    print(f"[OK] Created: {output_path.name} ({output_path.stat().st_size // 1024}KB)")

def create_canonical_six_universality():
    """
    Example 2: Canonical Six Universality
    Shows consistency across all 6 patterns
    """
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)

    # Chavez Transform amplification values (normalized)
    patterns = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']
    values = [0.83, 0.79, 0.75, 1.75, 0.71, 0.44]  # From E8 experiment

    # Create bar chart
    colors = [COLORS['accent'] if v > 1.5 else COLORS['primary'] for v in values]
    bars = ax.bar(patterns, values, color=colors, alpha=0.9, edgecolor='white', linewidth=2)

    # Add mean line
    mean_val = np.mean(values)
    ax.axhline(y=mean_val, color='white', linestyle='--', alpha=0.5, linewidth=2)
    ax.text(5.2, mean_val + 0.05, f'Mean: {mean_val:.2f}',
            color='white', alpha=0.8, fontsize=10, va='bottom')

    # Styling
    ax.set_ylabel('Chavez Transform Value', color='white', fontsize=12, fontweight='bold')
    ax.set_xlabel('Pattern', color='white', fontsize=12, fontweight='bold')
    ax.set_title('Canonical Six: Mathematical Universality\n(P4 Anomaly Highlighted)',
                 color='white', fontsize=15, pad=20, fontweight='bold')
    ax.tick_params(colors='white', labelsize=11)
    ax.set_facecolor(COLORS['background'])
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.patch.set_facecolor(COLORS['background'])

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        label = f'{val:.2f}'
        if val > 1.5:
            label += ' ⭐'
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
               label, ha='center', va='bottom', color='white',
               fontsize=11, fontweight='bold')

    output_path = OUTPUT_DIR / "canonical_six_universality.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=COLORS['background'])
    plt.close()

    print(f"[OK] Created: {output_path.name} ({output_path.stat().st_size // 1024}KB)")

def create_e8_mandala():
    """
    Example 3: E8 Mandala
    Polar projection showing 8-fold symmetry
    """
    fig = plt.figure(figsize=FIG_SIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection='polar')

    # Create 8 sectors for E8 symmetry
    theta = np.linspace(0, 2*np.pi, 9)
    radii = [1.0, 1.2, 1.0, 1.5, 1.0, 1.3, 1.0, 1.1]  # Vary radii for visual interest

    # P4 is sector 4 (index 3)
    colors_sectors = [COLORS['accent'] if i == 3 else COLORS['primary']
                     for i in range(8)]

    # Plot sectors
    for i in range(8):
        theta_segment = [theta[i], theta[i+1]]
        ax.fill_between(theta_segment, 0, radii[i],
                        color=colors_sectors[i], alpha=0.7,
                        edgecolor='white', linewidth=2)

        # Add labels
        mid_theta = (theta[i] + theta[i+1]) / 2
        label_r = radii[i] * 0.6
        label = f'P{i+1}' if i < 6 else ''  # Only label first 6
        if label:
            ax.text(mid_theta, label_r, label,
                   ha='center', va='center', color='white',
                   fontsize=12, fontweight='bold')

    # Central circle
    central_circle = plt.Circle((0, 0), 0.3, transform=ax.transData._b,
                               color=COLORS['secondary'], alpha=0.9,
                               edgecolor='white', linewidth=2)
    ax.add_artist(central_circle)
    ax.text(0, 0, 'E8', ha='center', va='center', color='white',
           fontsize=16, fontweight='bold', transform=ax.transData._b)

    # Styling
    ax.set_ylim(0, 1.6)
    ax.set_facecolor(COLORS['background'])
    ax.set_title('E8 Lattice Projection: Pattern 4 Sector\n8-Fold Symmetry',
                 color='white', fontsize=15, pad=30, fontweight='bold')
    ax.grid(True, color='white', alpha=0.2, linewidth=1)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    fig.patch.set_facecolor(COLORS['background'])

    output_path = OUTPUT_DIR / "e8_mandala_p4.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=COLORS['background'])
    plt.close()

    print(f"[OK] Created: {output_path.name} ({output_path.stat().st_size // 1024}KB)")

def main():
    """Generate all example visualizations"""
    print("\n" + "="*70)
    print("CAILculator MCP - Creating Marketing Example Visualizations")
    print("="*70 + "\n")

    try:
        create_zero_divisor_network()
        create_canonical_six_universality()
        create_e8_mandala()

        print("\n" + "="*70)
        print("[SUCCESS] All marketing examples created!")
        print("="*70 + "\n")

        # List created files with sizes
        print("Created files:")
        total_size = 0
        for file in sorted(OUTPUT_DIR.glob("*.png")):
            size_kb = file.stat().st_size // 1024
            total_size += size_kb
            print(f"  • {file.name:<40} {size_kb:>4}KB")

        print(f"\nTotal size: {total_size}KB")
        print("\nThese are ready for GitHub/marketing materials!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
