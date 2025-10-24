"""
Comprehensive MCP Server Tool Test Suite
Tests all 4 tools after hypercomplex library fix
"""

import sys
sys.path.insert(0, 'src')

import asyncio
import json
import numpy as np
from cailculator_mcp.tools import (
    compute_high_dimensional,
    chavez_transform,
    detect_patterns,
    analyze_dataset
)


def print_test_header(test_name):
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)


def print_result(result, truncate_arrays=True):
    """Pretty print result, optionally truncating long arrays"""
    if truncate_arrays and isinstance(result, dict):
        result_copy = result.copy()
        if 'result' in result_copy and isinstance(result_copy['result'], list):
            if len(result_copy['result']) > 10:
                result_copy['result'] = result_copy['result'][:5] + ['...'] + result_copy['result'][-2:]
        print(json.dumps(result_copy, indent=2))
    else:
        print(json.dumps(result, indent=2))


async def test_1_zero_divisors():
    """Test compute_high_dimensional with known zero divisor pairs"""
    print_test_header("1. ZERO DIVISOR CALCULATIONS (16D, 32D, 64D)")

    dimensions = [16, 32, 64]

    for dim in dimensions:
        print(f"\n{dim}D Test: (e_4 + e_11) × (e_1 - e_14)")

        # Create coefficient arrays
        p_coeffs = [0.0] * dim
        p_coeffs[4] = 1.0
        p_coeffs[11] = 1.0

        q_coeffs = [0.0] * dim
        q_coeffs[1] = 1.0
        q_coeffs[14] = -1.0

        args = {
            'operation': 'multiply',
            'dimension': dim,
            'operands': [p_coeffs, q_coeffs]
        }

        result = await compute_high_dimensional(args)

        if result.get('success'):
            print(f"  OK Success!")
            print(f"  Result norm: {result['metadata']['result_norm']:.2e}")
            print(f"  Is zero divisor: {result['metadata']['is_zero_divisor_result']}")
            print(f"  Interpretation: {result['interpretation'][:80]}...")
        else:
            print(f"  FAIL FAILED: {result.get('error')}")
            return False

    return True


async def test_2_other_operations():
    """Test other hypercomplex operations"""
    print_test_header("2. OTHER HYPERCOMPLEX OPERATIONS")

    # Test conjugate
    print("\nConjugate Test: conj(e_1 + e_2)")
    coeffs = [0.0, 1.0, 1.0] + [0.0]*13  # 16D
    args = {
        'operation': 'conjugate',
        'dimension': 16,
        'operands': [coeffs]
    }
    result = await compute_high_dimensional(args)
    if result.get('success'):
        print(f"  OK Conjugate computed")
        print(f"  Norms equal: {result['metadata']['norms_equal']}")
    else:
        print(f"  FAIL FAILED: {result.get('error')}")
        return False

    # Test norm
    print("\nNorm Test: |e_1 + e_2|")
    args = {
        'operation': 'norm',
        'dimension': 16,
        'operands': [coeffs]
    }
    result = await compute_high_dimensional(args)
    if result.get('success'):
        print(f"  OK Norm: {result['norm']:.4f} (expected: {np.sqrt(2):.4f})")
    else:
        print(f"  FAIL FAILED: {result.get('error')}")
        return False

    # Test addition
    print("\nAddition Test: (e_1 + e_2) + (e_3 + e_4)")
    coeffs2 = [0.0, 0.0, 0.0, 1.0, 1.0] + [0.0]*11
    args = {
        'operation': 'add',
        'dimension': 16,
        'operands': [coeffs, coeffs2]
    }
    result = await compute_high_dimensional(args)
    if result.get('success'):
        print(f"  OK Addition computed")
        print(f"  Result norm: {result['metadata']['result_norm']:.4f}")
    else:
        print(f"  FAIL FAILED: {result.get('error')}")
        return False

    return True


async def test_3_chavez_transform():
    """Test Chavez Transform tool"""
    print_test_header("3. CHAVEZ TRANSFORM")

    # Test with sample data - Gaussian-like distribution
    print("\nTransform Test: Gaussian data with Pattern 4")
    data = list(np.exp(-np.linspace(-3, 3, 20)**2))

    args = {
        'data': data,
        'pattern_id': 4,  # Pattern 4 - the anomaly!
        'alpha': 1.0,
        'dimension_param': 2
    }

    result = await chavez_transform(args)

    if result.get('success'):
        print(f"  OK Transform computed")
        print(f"  Transform value: {result['transform_value']:.6e}")
        print(f"  Pattern ID: {result['pattern_id']}")
        print(f"  Alpha: {result['alpha']}")
        print(f"  Convergence:")
        print(f"    - Rate: {result['convergence']['rate']:.4f}")
        print(f"    - All converged: {result['convergence']['all_converged']}")
        print(f"  Stability:")
        print(f"    - Bound satisfied: {result['stability']['bound_satisfied']}")
        print(f"    - Ratio: {result['stability']['ratio']:.4f}")
    else:
        print(f"  FAIL FAILED: {result.get('error')}")
        return False

    # Test with multiple patterns
    print("\nTesting all 6 Canonical Patterns:")
    for pattern_id in range(1, 7):
        args['pattern_id'] = pattern_id
        result = await chavez_transform(args)
        if result.get('success'):
            print(f"  Pattern {pattern_id}: C[f] = {result['transform_value']:.6e}")
        else:
            print(f"  Pattern {pattern_id}: FAILED")
            return False

    return True


async def test_4_pattern_detection():
    """Test pattern detection tool"""
    print_test_header("4. PATTERN DETECTION")

    # Create data with conjugation symmetry
    print("\nPattern Detection Test: Symmetric data")
    data = [1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0]

    args = {
        'data': data,
        'pattern_types': ['all']
    }

    result = await detect_patterns(args)

    if result.get('success'):
        print(f"  OK Pattern detection completed")
        print(f"  Patterns found: {result['patterns_found']}")
        for pattern in result['patterns']:
            print(f"    - {pattern['type']}: confidence {pattern['confidence']:.2f}")
            print(f"      {pattern['description']}")
    else:
        print(f"  FAIL FAILED: {result.get('error')}")
        return False

    return True


async def test_5_comprehensive_analysis():
    """Test comprehensive dataset analysis"""
    print_test_header("5. COMPREHENSIVE DATASET ANALYSIS")

    # Generate interesting test data
    print("\nFull Analysis Test: Sine wave data")
    t = np.linspace(0, 2*np.pi, 30)
    data = list(np.sin(t) + 0.1*np.random.randn(30))

    args = {
        'data': data,
        'include_transform': True,
        'include_patterns': True,
        'include_statistics': True
    }

    result = await analyze_dataset(args)

    if result.get('success'):
        print(f"  OK Analysis completed")
        print(f"\n  Data Summary:")
        print(f"    - Size: {result['data_summary']['size']}")
        print(f"    - Range: [{result['data_summary']['range'][0]:.2f}, {result['data_summary']['range'][1]:.2f}]")

        if 'statistics' in result:
            print(f"\n  Statistics:")
            print(f"    - Mean: {result['statistics']['mean']:.4f}")
            print(f"    - Std Dev: {result['statistics']['std']:.4f}")

        if 'transform' in result and result['transform'].get('success'):
            print(f"\n  Chavez Transform:")
            print(f"    - Value: {result['transform']['transform_value']:.6e}")
            print(f"    - Converged: {result['transform']['convergence']['all_converged']}")

        if 'patterns' in result and result['patterns'].get('success'):
            print(f"\n  Patterns:")
            print(f"    - Found: {result['patterns']['patterns_found']}")

        print(f"\n  Interpretation:")
        print(f"    {result['interpretation']}")

    else:
        print(f"  FAIL FAILED: {result.get('error')}")
        return False

    return True


async def main():
    """Run all tests"""
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + "  CAILCULATOR MCP SERVER - COMPREHENSIVE TOOL TEST SUITE".center(78) + "#")
    print("#" + "  Testing all tools after hypercomplex library fix".center(78) + "#")
    print("#" + " "*78 + "#")
    print("#"*80)

    tests = [
        ("Zero Divisor Calculations", test_1_zero_divisors),
        ("Other Hypercomplex Operations", test_2_other_operations),
        ("Chavez Transform", test_3_chavez_transform),
        ("Pattern Detection", test_4_pattern_detection),
        ("Comprehensive Analysis", test_5_comprehensive_analysis)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\nFAIL EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, success in results:
        status = "OK PASS" if success else "FAIL FAIL"
        print(f"{status:8} - {test_name}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print("="*80)
    print(f"TOTAL: {passed}/{total} tests passed ({100*passed/total:.0f}%)")
    print("="*80)

    if passed == total:
        print("\nSUCCESS: ALL TESTS PASSED! MCP server is fully operational!")
    else:
        print(f"\nWARNING: {total - passed} test(s) failed. Review output above.")


if __name__ == "__main__":
    asyncio.run(main())
