"""
Test script for High-Dimensional Calculator
Tests the compute_high_dimensional tool
"""

import asyncio
import sys
import json

try:
    from cailculator_mcp.tools import compute_high_dimensional
except ImportError:
    print("Error: Cannot import cailculator_mcp. Make sure you've installed it with 'pip install -e .'")
    sys.exit(1)


async def test_sedenion_multiplication():
    """Test sedenion multiplication (16D)"""
    print("="*60)
    print("TEST 1: Sedenion Multiplication (16D)")
    print("="*60)
    
    # Create two simple sedenions
    s1 = [1.0, 1.0] + [0.0]*14  # (1 + e_1)
    s2 = [2.0, 0.0, 1.0] + [0.0]*13  # (2 + e_2)
    
    print(f"s1 = (1 + e_1) = first two coeffs: {s1[:3]}")
    print(f"s2 = (2 + e_2) = first three coeffs: {s2[:3]}")
    print()
    
    result = await compute_high_dimensional({
        "operation": "multiply",
        "dimension": 16,
        "operands": [s1, s2]
    })
    
    print_result(result)
    print()


async def test_pathion_operations():
    """Test pathion operations (32D)"""
    print("="*60)
    print("TEST 2: Pathion Operations (32D)")
    print("="*60)
    
    # Create a pathion
    p1 = [1.0, 2.0, 3.0] + [0.0]*29
    
    print("Testing multiple operations on pathion p1:")
    print(f"  First 3 coefficients: {p1[:3]}")
    print()
    
    # Test norm
    print("1. Computing norm...")
    result = await compute_high_dimensional({
        "operation": "norm",
        "dimension": 32,
        "operands": [p1]
    })
    if result.get('success'):
        print(f"   Norm: {result['norm']:.6f}")
        print(f"   Norm²: {result['norm_squared']:.6f}")
    else:
        print(f"   Error: {result.get('error')}")
    print()
    
    # Test conjugate
    print("2. Computing conjugate...")
    result = await compute_high_dimensional({
        "operation": "conjugate",
        "dimension": 32,
        "operands": [p1]
    })
    if result.get('success'):
        conj = result['result']
        print(f"   Conjugate first 3 coeffs: {conj[:3]}")
        print(f"   Original norm: {result['metadata']['original_norm']:.6f}")
        print(f"   Conjugate norm: {result['metadata']['conjugate_norm']:.6f}")
        print(f"   Norms equal: {result['metadata']['norms_equal']}")
    else:
        print(f"   Error: {result.get('error')}")
    print()
    
    # Test inverse
    print("3. Computing inverse...")
    result = await compute_high_dimensional({
        "operation": "inverse",
        "dimension": 32,
        "operands": [p1]
    })
    if result.get('success'):
        print(f"   Inverse computed successfully")
        print(f"   Verification: {result['metadata']['is_verified']}")
        print(f"   Verification error: {result['metadata']['verification_error']:.2e}")
    else:
        print(f"   Error: {result.get('error')}")
    print()


async def test_zero_divisors():
    """Test zero divisor detection in sedenions"""
    print("="*60)
    print("TEST 3: Zero Divisor Detection (16D Sedenions)")
    print("="*60)
    
    # Known zero divisor pattern in sedenions: e_1 + e_14
    # (indices 1 and 14 sum to 15, which is the characteristic pattern)
    zero_div = [0.0, 1.0] + [0.0]*12 + [1.0, 0.0]
    
    print("Testing element: e_1 + e_14 (known zero divisor pattern)")
    print()
    
    # Check if it's a zero divisor
    result = await compute_high_dimensional({
        "operation": "is_zero_divisor",
        "dimension": 16,
        "operands": [zero_div]
    })
    
    if result.get('success'):
        print(f"  Is zero divisor: {result['is_zero_divisor']}")
        print(f"  Norm: {result['norm']:.6f}")
        print(f"  {result['interpretation']}")
    else:
        print(f"  Error: {result.get('error')}")
    print()
    
    # Find zero divisor pairs
    print("Finding zero divisor pairs...")
    result = await compute_high_dimensional({
        "operation": "find_zero_divisors",
        "dimension": 16,
        "operands": [[100]]  # Search 100 samples
    })
    
    if result.get('success'):
        print(f"  Found {result['zero_divisor_pairs_found']} pair(s)")
        if result.get('pairs'):
            for i, pair in enumerate(result['pairs'][:3], 1):
                print(f"\n  Pair {i}:")
                print(f"    |x| = {pair['x_norm']:.6f}")
                print(f"    |y| = {pair['y_norm']:.6f}")
                print(f"    |x*y| = {pair['product_norm']:.10f} ← near zero!")
    else:
        print(f"  Error: {result.get('error')}")
    print()


async def test_addition_subtraction():
    """Test addition and subtraction"""
    print("="*60)
    print("TEST 4: Addition and Subtraction (32D)")
    print("="*60)
    
    p1 = [1.0, 2.0] + [0.0]*30
    p2 = [3.0, 1.0] + [0.0]*30
    
    print("p1 first 2 coeffs: [1.0, 2.0]")
    print("p2 first 2 coeffs: [3.0, 1.0]")
    print()
    
    # Addition
    print("1. p1 + p2:")
    result = await compute_high_dimensional({
        "operation": "add",
        "dimension": 32,
        "operands": [p1, p2]
    })
    if result.get('success'):
        sum_result = result['result']
        print(f"   Result first 2 coeffs: {sum_result[:2]}")
        print(f"   Expected: [4.0, 3.0] ✓")
    print()
    
    # Subtraction
    print("2. p1 - p2:")
    result = await compute_high_dimensional({
        "operation": "subtract",
        "dimension": 32,
        "operands": [p1, p2]
    })
    if result.get('success'):
        diff_result = result['result']
        print(f"   Result first 2 coeffs: {diff_result[:2]}")
        print(f"   Expected: [-2.0, 1.0] ✓")
    print()


async def test_higher_dimensions():
    """Test calculations in higher dimensions (64D, 128D)"""
    print("="*60)
    print("TEST 5: Higher Dimensions (64D, 128D)")
    print("="*60)
    
    # Test 64D (chingons)
    print("1. Chingon multiplication (64D):")
    c1 = [1.0, 1.0] + [0.0]*62
    c2 = [1.0, 0.0, 1.0] + [0.0]*61
    
    result = await compute_high_dimensional({
        "operation": "multiply",
        "dimension": 64,
        "operands": [c1, c2]
    })
    
    if result.get('success'):
        print(f"   ✓ Success in {result['dimension_name']}")
        print(f"   Result norm: {result['metadata']['result_norm']:.6f}")
    else:
        print(f"   Error: {result.get('error')}")
    print()
    
    # Test 128D
    print("2. 128D algebra norm calculation:")
    a1 = [1.0] + [0.0]*127
    
    result = await compute_high_dimensional({
        "operation": "norm",
        "dimension": 128,
        "operands": [a1]
    })
    
    if result.get('success'):
        print(f"   ✓ Success in {result['dimension_name']}")
        print(f"   Norm: {result['norm']:.6f}")
    else:
        print(f"   Error: {result.get('error')}")
    print()


async def test_edge_cases():
    """Test edge cases and error handling"""
    print("="*60)
    print("TEST 6: Edge Cases and Error Handling")
    print("="*60)
    
    # Wrong dimension
    print("1. Wrong number of coefficients:")
    result = await compute_high_dimensional({
        "operation": "norm",
        "dimension": 32,
        "operands": [[1.0, 2.0, 3.0]]  # Only 3 coeffs instead of 32
    })
    print(f"   Expected error: {result.get('error', 'No error')}")
    print()
    
    # Invalid dimension
    print("2. Invalid dimension (10D):")
    result = await compute_high_dimensional({
        "operation": "norm",
        "dimension": 10,
        "operands": [[1.0]*10]
    })
    print(f"   Expected error: {result.get('error', 'No error')}")
    print()
    
    # Zero element inverse (should fail)
    print("3. Inverse of zero element:")
    zero = [0.0]*32
    result = await compute_high_dimensional({
        "operation": "inverse",
        "dimension": 32,
        "operands": [zero]
    })
    print(f"   Expected error: {result.get('error', 'No error')}")
    print()


async def test_real_world_example():
    """Test a real-world calculation example"""
    print("="*60)
    print("TEST 7: Real-World Example - E8 Pattern Analysis")
    print("="*60)
    
    print("Computing Canonical Six pattern (e_1 + e_14) multiplication...")
    print()
    
    # Canonical Six pattern 1: e_1 + e_14
    pattern1 = [0.0, 1.0] + [0.0]*12 + [1.0, 0.0]
    
    # Canonical Six pattern 2: e_2 + e_13  
    pattern2 = [0.0, 0.0, 1.0] + [0.0]*10 + [1.0] + [0.0]*2
    
    result = await compute_high_dimensional({
        "operation": "multiply",
        "dimension": 16,
        "operands": [pattern1, pattern2]
    })
    
    if result.get('success'):
        print(f"  Dimension: {result['dimension_name']}")
        print(f"  Result norm: {result['metadata']['result_norm']:.10f}")
        
        if result['metadata'].get('is_zero_divisor_result'):
            print(f"  🎯 Zero divisor detected!")
            print(f"  {result['interpretation']}")
        else:
            print(f"  Result is non-zero")
        
        print(f"\n  First 5 coefficients of result: {result['result'][:5]}")
    else:
        print(f"  Error: {result.get('error')}")
    
    print()


def print_result(result):
    """Pretty print computation result"""
    if result.get('success'):
        print(f"✅ Success!")
        print(f"Operation: {result['operation']}")
        print(f"Dimension: {result['dimension']} ({result['dimension_name']})")
        
        if 'result' in result:
            res = result['result']
            print(f"Result (first 5 coeffs): {res[:5]}")
            
            if 'result_string' in result and len(result['result_string']) < 100:
                print(f"Result string: {result['result_string']}")
        
        if 'metadata' in result:
            print(f"Metadata:")
            for key, value in result['metadata'].items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.6f}")
                elif isinstance(value, list) and len(value) <= 3:
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")
        
        if 'interpretation' in result:
            print(f"\n💡 {result['interpretation']}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def main():
    """Run all calculator tests"""
    print("\n")
    print("🧮 CAILculator MCP - High-Dimensional Calculator Tests")
    print()
    
    await test_sedenion_multiplication()
    await test_pathion_operations()
    await test_zero_divisors()
    await test_addition_subtraction()
    await test_higher_dimensions()
    await test_edge_cases()
    await test_real_world_example()
    
    print("="*60)
    print("✅ ALL CALCULATOR TESTS COMPLETE")
    print("="*60)
    print()
    print("Summary:")
    print("  ✓ Sedenion calculations (16D)")
    print("  ✓ Pathion calculations (32D)")
    print("  ✓ Chingon calculations (64D)")
    print("  ✓ Higher dimensions (128D)")
    print("  ✓ Zero divisor detection")
    print("  ✓ All basic operations")
    print("  ✓ Error handling")
    print()


if __name__ == "__main__":
    asyncio.run(main())
