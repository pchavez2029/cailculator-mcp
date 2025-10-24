"""
Test new visualization implementations
"""
import sys
sys.path.insert(0, 'src')

import asyncio
from cailculator_mcp.tools import illustrate


async def test_canonical_six():
    """Test canonical six universality visualization"""
    print("\n" + "="*80)
    print("TEST: Canonical Six Universality")
    print("="*80)

    args = {
        'visualization_type': 'canonical_six_universality',
        'data': {},  # Will use default Gaussian data
        'output_format': 'static',
        'style': 'publication'
    }

    result = await illustrate(args)

    if result.get('success'):
        print("SUCCESS")
        print(f"  Static path: {result.get('static_path')}")
        print(f"  Description: {result.get('description')}")
        print(f"  Interpretation: {result.get('interpretation')}")
        if 'metrics' in result:
            print(f"  Coefficient of Variation: {result['metrics']['coefficient_of_variation']:.6f}")
            print(f"  Mean Transform: {result['metrics']['mean_transform']:.6e}")
    else:
        print(f"FAILED: {result.get('error')}")

    return result.get('success', False)


async def test_dimensional_scaling():
    """Test dimensional scaling visualization"""
    print("\n" + "="*80)
    print("TEST: Dimensional Scaling")
    print("="*80)

    args = {
        'visualization_type': 'dimensional_scaling',
        'data': {
            'pattern_id': 4  # Test Pattern 4 (the anomaly)
        },
        'output_format': 'static',
        'style': 'publication'
    }

    result = await illustrate(args)

    if result.get('success'):
        print("SUCCESS")
        print(f"  Static path: {result.get('static_path')}")
        print(f"  Description: {result.get('description')}")
        print(f"  Interpretation: {result.get('interpretation')}")
        if 'metrics' in result:
            print(f"  Zero Divisor Count: {result['metrics']['zero_divisor_count']}/5 dimensions")
    else:
        print(f"FAILED: {result.get('error')}")

    return result.get('success', False)


async def main():
    print("\n" + "#"*80)
    print("#  NEW VISUALIZATION TESTS")
    print("#"*80)

    results = []
    results.append(("Canonical Six Universality", await test_canonical_six()))
    results.append(("Dimensional Scaling", await test_dimensional_scaling()))

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} - {name}")

    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{len(results)} passed")

    return all(s for _, s in results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
