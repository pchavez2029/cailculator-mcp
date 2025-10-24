"""
Test visualization tools
"""
import sys
sys.path.insert(0, 'src')

import asyncio
from cailculator_mcp.tools import illustrate


async def test_zero_divisor_network():
    """Test zero divisor network visualization"""
    print("\n" + "="*80)
    print("TEST: Zero Divisor Network Visualization")
    print("="*80)

    args = {
        'visualization_type': 'zero_divisor_network',
        'data': {
            'pattern_id': 1,
            'dimension': 16
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
    else:
        print(f"FAILED: {result.get('error')}")

    return result.get('success', False)


async def test_basis_heatmap():
    """Test basis interaction heatmap"""
    print("\n" + "="*80)
    print("TEST: Basis Interaction Heatmap")
    print("="*80)

    args = {
        'visualization_type': 'basis_interaction_heatmap',
        'data': {
            'pattern_id': 2,
            'dimension': 16
        },
        'output_format': 'static',
        'style': 'publication'
    }

    result = await illustrate(args)

    if result.get('success'):
        print("SUCCESS")
        print(f"  Static path: {result.get('static_path')}")
        print(f"  Description: {result.get('description')}")
    else:
        print(f"FAILED: {result.get('error')}")

    return result.get('success', False)


async def main():
    print("\n" + "#"*80)
    print("#  VISUALIZATION TESTS")
    print("#"*80)

    results = []
    results.append(("Zero Divisor Network", await test_zero_divisor_network()))
    results.append(("Basis Heatmap", await test_basis_heatmap()))

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} - {name}")

    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{len(results)} passed")


if __name__ == "__main__":
    asyncio.run(main())
