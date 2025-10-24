"""
Comprehensive test of all visualization generators
"""
import sys
sys.path.insert(0, 'src')

import asyncio
from cailculator_mcp.tools import illustrate


async def test_visualization(name, args):
    """Test a single visualization"""
    print(f"\nTesting: {name}")
    print("-" * 60)
    
    result = await illustrate(args)
    
    if result.get('success'):
        print(f"  SUCCESS")
        print(f"  File: {result.get('static_path')}")
        print(f"  Description: {result.get('description')[:80]}...")
        return True
    else:
        print(f"  FAILED: {result.get('error')}")
        return False


async def main():
    print("\n" + "="*80)
    print("COMPREHENSIVE VISUALIZATION TEST SUITE")
    print("All 7 visualization types - all generate fresh content")
    print("="*80)

    tests = [
        ("Zero Divisor Network", {
            'visualization_type': 'zero_divisor_network',
            'data': {'pattern_id': 1, 'dimension': 16},
            'output_format': 'static',
            'style': 'publication'
        }),
        
        ("Basis Interaction Heatmap", {
            'visualization_type': 'basis_interaction_heatmap',
            'data': {'pattern_id': 2, 'dimension': 16},
            'output_format': 'static',
            'style': 'publication'
        }),
        
        ("Canonical Six Universality", {
            'visualization_type': 'canonical_six_universality',
            'data': {},
            'output_format': 'static',
            'style': 'publication'
        }),
        
        ("Alpha Sensitivity", {
            'visualization_type': 'alpha_sensitivity',
            'data': {'pattern_id': 3},
            'output_format': 'static',
            'style': 'publication'
        }),
        
        ("E8 Mandala", {
            'visualization_type': 'e8_mandala',
            'data': {'pattern_id': 4, 'num_shells': 3},
            'output_format': 'static',
            'style': 'publication'
        }),
        
        ("Pattern Comparison", {
            'visualization_type': 'pattern_comparison',
            'data': {'pattern_ids': [1, 2, 3, 4], 'dimension': 32},
            'output_format': 'static',
            'style': 'publication'
        }),
        
        ("Dimensional Scaling", {
            'visualization_type': 'dimensional_scaling',
            'data': {'pattern_id': 5},
            'output_format': 'static',
            'style': 'publication'
        })
    ]

    results = []
    for name, args in tests:
        success = await test_visualization(name, args)
        results.append((name, success))

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {status:6} - {name}")

    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\nTotal: {passed}/{total} passed ({100*passed/total:.0f}%)")
    
    if passed == total:
        print("\nSUCCESS: All visualizations generate fresh content!")
    else:
        print(f"\nWARNING: {total-passed} visualization(s) failed")
    
    return all(s for _, s in results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
