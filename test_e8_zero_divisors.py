"""
Quick test of E8 zero divisor analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cailculator_mcp.e8_utils import quick_e8_test


def main():
    print("=" * 80)
    print("E8 ZERO DIVISOR ANALYSIS - QUICK TEST")
    print("=" * 80)
    print()

    print("Testing E8 roots embedded in 256D Cayley-Dickson space...")
    print("Searching first 1000 pairs for zero divisors...")
    print()

    results = quick_e8_test(dimension=256, max_pairs=1000)

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    print("E8 Lattice:")
    print(f"  Total roots: {results['statistics']['total_roots']}")
    print(f"  Weyl orbits: {results['statistics']['weyl_orbits']}")
    print()

    if 'zero_divisors_found' in results['statistics']:
        print(f"Zero Divisors Found: {results['statistics']['zero_divisors_found']}")
        print()

    if 'canonical_matches' in results['statistics']:
        print(f"Canonical Six Matches: {results['statistics']['canonical_matches']}")
        print()

    print("Lisi Theory Support:")
    print(f"  Level: {results['lisi_theory_support']}")
    print(f"  Interpretation: {results['interpretation']}")
    print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
