"""
Test script for Pattern Detection
"""

import asyncio
import sys
import numpy as np

# You may need to adjust the import path depending on how you run this
try:
    from cailculator_mcp.tools import detect_patterns
except ImportError:
    print("Error: Cannot import cailculator_mcp. Make sure you've installed it with 'pip install -e .'")
    sys.exit(1)


async def test_symmetric_data():
    """Test with symmetric data (should detect conjugation symmetry)"""
    print("="*60)
    print("TEST 1: Symmetric Data (Conjugation Symmetry)")
    print("="*60)
    
    # Perfect mirror symmetry
    data = [1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0]
    print(f"Input data: {data}")
    print("Expected: High confidence conjugation symmetry")
    print()
    
    result = await detect_patterns({
        "data": data,
        "pattern_types": ["all"]
    })
    
    print_result(result)
    print()


async def test_zero_crossings():
    """Test with data that crosses zero (bilateral zeros)"""
    print("="*60)
    print("TEST 2: Zero Crossings (Bilateral Zeros)")
    print("="*60)
    
    # Data with symmetric zero crossings
    data = [2.0, 1.0, -1.0, -2.0, -1.0, 1.0, 2.0]
    print(f"Input data: {data}")
    print("Expected: Bilateral zeros pattern")
    print()
    
    result = await detect_patterns({
        "data": data,
        "pattern_types": ["all"]
    })
    
    print_result(result)
    print()


async def test_stable_structure():
    """Test with data that should show dimensional persistence"""
    print("="*60)
    print("TEST 3: Stable Structure (Dimensional Persistence)")
    print("="*60)
    
    # Gaussian-like data (stable under transforms)
    x = np.linspace(-3, 3, 50)
    data = np.exp(-x**2).tolist()
    print(f"Input: Gaussian-like data ({len(data)} points)")
    print("Expected: Dimensional persistence pattern")
    print()
    
    result = await detect_patterns({
        "data": data,
        "pattern_types": ["all"]
    })
    
    print_result(result)
    print()


async def test_specific_patterns():
    """Test detection of specific pattern types"""
    print("="*60)
    print("TEST 4: Specific Pattern Types")
    print("="*60)
    
    data = [1.0, 2.0, 3.0, 2.0, 1.0]
    print(f"Input data: {data}")
    print()
    
    # Test each pattern type individually
    pattern_types = [
        "conjugation_symmetry",
        "bilateral_zeros",
        "dimensional_persistence"
    ]
    
    for ptype in pattern_types:
        print(f"Testing for: {ptype}")
        result = await detect_patterns({
            "data": data,
            "pattern_types": [ptype]
        })
        
        if result.get('success'):
            num_found = result.get('patterns_found', 0)
            if num_found > 0:
                pattern = result['patterns'][0]
                print(f"  ✅ Found: {pattern['description']} (confidence: {pattern['confidence']:.2f})")
            else:
                print(f"  ⚠️  Not detected")
        else:
            print(f"  ❌ Error: {result.get('error')}")
        print()


async def test_random_data():
    """Test with random data (should find few or no patterns)"""
    print("="*60)
    print("TEST 5: Random Data (No Expected Patterns)")
    print("="*60)
    
    # Random noise
    np.random.seed(42)
    data = np.random.randn(20).tolist()
    print(f"Input: Random data ({len(data)} points)")
    print("Expected: Few or no patterns detected")
    print()
    
    result = await detect_patterns({
        "data": data,
        "pattern_types": ["all"]
    })
    
    print_result(result)
    print()


def print_result(result):
    """Pretty print pattern detection result"""
    if result.get('success'):
        num_patterns = result.get('patterns_found', 0)
        print(f"✅ Success: {num_patterns} pattern(s) detected")
        print()
        
        for i, pattern in enumerate(result.get('patterns', []), 1):
            print(f"Pattern {i}:")
            print(f"  Type: {pattern['type']}")
            print(f"  Confidence: {pattern['confidence']:.2%}")
            print(f"  Description: {pattern['description']}")
            
            if pattern.get('indices'):
                print(f"  Key Indices: {pattern['indices'][:10]}")  # Show first 10
            
            if pattern.get('metrics'):
                print(f"  Metrics:")
                for key, value in pattern['metrics'].items():
                    if isinstance(value, float):
                        print(f"    {key}: {value:.4f}")
                    elif isinstance(value, (list, tuple)) and len(value) > 5:
                        print(f"    {key}: [{value[0]:.2f}, {value[1]:.2f}, ... {len(value)} values]")
                    else:
                        print(f"    {key}: {value}")
            print()
    else:
        print(f"❌ Error: {result.get('error')}")


async def main():
    """Run all pattern detection tests"""
    print("\n")
    print("🔍 CAILculator MCP - Pattern Detection Tests")
    print()
    
    await test_symmetric_data()
    await test_zero_crossings()
    await test_stable_structure()
    await test_specific_patterns()
    await test_random_data()
    
    print("="*60)
    print("✅ ALL TESTS COMPLETE")
    print("="*60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
