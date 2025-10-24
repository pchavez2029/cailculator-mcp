"""
Test script for Chavez Transform
"""

import asyncio
import sys

# You may need to adjust the import path depending on how you run this
try:
    from cailculator_mcp.tools import chavez_transform
except ImportError:
    print("Error: Cannot import cailculator_mcp. Make sure you've installed it with 'pip install -e .'")
    sys.exit(1)


async def test_simple_data():
    """Test with simple symmetric data"""
    print("="*60)
    print("TEST 1: Simple Symmetric Data")
    print("="*60)
    
    data = [1.0, 2.0, 3.0, 2.0, 1.0]
    print(f"Input data: {data}")
    
    result = await chavez_transform({
        "data": data,
        "pattern_id": 1,
        "alpha": 1.0,
        "dimension_param": 2
    })
    
    print("\nResult:")
    if result.get('success'):
        print(f"  ✅ Success: True")
        print(f"  Transform Value: {result.get('transform_value'):.6e}")
        print(f"  Pattern ID: {result.get('pattern_id')}")
        print(f"  Alpha: {result.get('alpha')}")
        
        convergence = result.get('convergence', {})
        print(f"\n  Convergence:")
        print(f"    Rate: {convergence.get('rate', 0)*100:.1f}%")
        print(f"    All Converged: {convergence.get('all_converged')}")
        
        stability = result.get('stability', {})
        print(f"\n  Stability:")
        print(f"    Bound Satisfied: {stability.get('bound_satisfied')}")
        print(f"    Ratio: {stability.get('ratio', 0):.6f}")
    else:
        print(f"  ❌ Error: {result.get('error')}")
    
    print()


async def test_different_patterns():
    """Test with different Canonical Six patterns"""
    print("="*60)
    print("TEST 2: Different Canonical Six Patterns")
    print("="*60)
    
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    print(f"Input data: {data}")
    print()
    
    for pattern_id in range(1, 7):
        result = await chavez_transform({
            "data": data,
            "pattern_id": pattern_id,
            "alpha": 1.0,
            "dimension_param": 2
        })
        
        if result.get('success'):
            value = result.get('transform_value')
            converged = result.get('convergence', {}).get('all_converged')
            status = "✅" if converged else "⚠️"
            print(f"  Pattern {pattern_id}: {value:.6e} {status}")
        else:
            print(f"  Pattern {pattern_id}: ❌ Error - {result.get('error')}")
    
    print()


async def test_edge_cases():
    """Test edge cases"""
    print("="*60)
    print("TEST 3: Edge Cases")
    print("="*60)
    
    # Single value
    print("\n1. Single value:")
    result = await chavez_transform({
        "data": [5.0],
        "pattern_id": 1
    })
    print(f"   Result: {'✅' if result.get('success') else '❌'} {result.get('transform_value', result.get('error'))}")
    
    # Empty array
    print("\n2. Empty array:")
    result = await chavez_transform({
        "data": []
    })
    print(f"   Result: {'✅' if result.get('success') else '❌'} {result.get('error', 'OK')}")
    
    # Large array
    print("\n3. Large array (100 points):")
    import numpy as np
    large_data = np.sin(np.linspace(0, 4*np.pi, 100)).tolist()
    result = await chavez_transform({
        "data": large_data,
        "pattern_id": 1
    })
    print(f"   Result: {'✅' if result.get('success') else '❌'} {result.get('transform_value', result.get('error'))}")
    
    print()


async def main():
    """Run all tests"""
    print("\n")
    print("🧮 CAILculator MCP - Chavez Transform Tests")
    print()
    
    await test_simple_data()
    await test_different_patterns()
    await test_edge_cases()
    
    print("="*60)
    print("✅ ALL TESTS COMPLETE")
    print("="*60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
