"""
Quick validation test for Chavez Transform before MCP integration
Run this to verify the transform is ready for production use
"""

import sys
sys.path.insert(0, 'src')

from cailculator_mcp.transforms import ChavezTransform, create_canonical_six_pathion
import numpy as np

print("="*60)
print("CHAVEZ TRANSFORM - PRODUCTION READINESS TEST")
print("="*60)
print()

# Test 1: Basic functionality
print("Test 1: Basic transform functionality...")
try:
    ct = ChavezTransform(alpha=1.0)
    P = create_canonical_six_pathion(1)
    f = lambda x: np.exp(-np.linalg.norm(x)**2)
    result = ct.transform_1d(f, P, d=2)
    print(f"  [OK] Transform executed: {result:.6e}")
    assert np.isfinite(result), "Result must be finite"
    print("  [OK] Result is finite")
except Exception as e:
    print(f"  [FAIL] FAILED: {e}")
    sys.exit(1)

# Test 2: All Canonical Six patterns
print("\nTest 2: All Canonical Six patterns...")
try:
    results = []
    for i in range(1, 7):
        P = create_canonical_six_pathion(i)
        r = ct.transform_1d(f, P, d=2)
        results.append(r)
        print(f"  [OK] Pattern {i}: {r:.6e}")

    # Check they're all the same (universal symmetry)
    if np.allclose(results, results[0]):
        print("  [OK] Perfect symmetry confirmed!")
    else:
        print("  [WARN] Warning: Patterns differ slightly")
except Exception as e:
    print(f"  [FAIL] FAILED: {e}")
    sys.exit(1)

# Test 3: Error handling
print("\nTest 3: Error handling...")
try:
    try:
        bad_ct = ChavezTransform(alpha=-1.0)
        print("  [FAIL] Should have raised ValueError for negative alpha")
        sys.exit(1)
    except ValueError as e:
        print(f"  [OK] Catches bad alpha: {e}")
except Exception as e:
    print(f"  [FAIL] Unexpected error: {e}")
    sys.exit(1)

# Test 4: Different test functions
print("\nTest 4: Different test functions...")
try:
    test_funcs = {
        'polynomial': lambda x: 1.0 + np.sum(x**2),
        'exponential': lambda x: np.exp(-np.abs(np.sum(x))),
    }

    for name, func in test_funcs.items():
        result = ct.transform_1d(func, P, d=2)
        print(f"  [OK] {name}: {result:.6e}")
        assert np.isfinite(result), f"{name} must produce finite result"
except Exception as e:
    print(f"  [FAIL] FAILED: {e}")
    sys.exit(1)

# Test 5: Multi-dimensional
print("\nTest 5: Multi-dimensional transform...")
try:
    f_2d = lambda x: np.exp(-np.linalg.norm(x)**2)
    domain_2d = [(-3, 3), (-3, 3)]
    result_2d = ct.transform_nd(f_2d, P, d=2, domain_ranges=domain_2d,
                                method='monte_carlo', num_samples=1000)
    print(f"  [OK] 2D transform: {result_2d:.6e}")
    assert np.isfinite(result_2d), "2D result must be finite"
except Exception as e:
    print(f"  [FAIL] FAILED: {e}")
    sys.exit(1)

print()
print("="*60)
print("[SUCCESS] ALL TESTS PASSED - TRANSFORM READY FOR PRODUCTION!")
print("="*60)
print()
print("Next steps:")
print("1. Implement server.py")
print("2. Wrap transform in MCP tool interface")
print("3. Test with dev API key")
print()
