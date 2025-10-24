"""
Test 128D and 256D Support - Canonical Six Patterns
Tests the extended dimensional support in CAILculator MCP Server
"""

from cailculator_mcp.hypercomplex import create_hypercomplex

def test_canonical_six_at_dimension(dimension, pattern_id=4):
    """Test a Canonical Six pattern at specified dimension."""

    # Pattern 4: (e_4 + e_11) × (e_1 - e_14) = 0
    # This pattern is valid across all Cayley-Dickson dimensions

    p_coeffs = [0.0] * dimension
    p_coeffs[4] = 1.0
    p_coeffs[11] = 1.0

    q_coeffs = [0.0] * dimension
    q_coeffs[1] = 1.0
    q_coeffs[14] = -1.0

    P = create_hypercomplex(dimension, p_coeffs)
    Q = create_hypercomplex(dimension, q_coeffs)

    product = P * Q
    product_norm = abs(product)

    return {
        'dimension': dimension,
        'pattern_id': pattern_id,
        'p_norm': abs(P),
        'q_norm': abs(Q),
        'product_norm': product_norm,
        'is_zero_divisor': product_norm < 1e-8
    }


def main():
    print("="*80)
    print("CAILCULATOR MCP SERVER - HIGH DIMENSIONAL SUPPORT TEST")
    print("Testing Canonical Six Patterns Across 16D to 256D")
    print("="*80)
    print()

    dimensions = [16, 32, 64, 128, 256]

    results = []

    for dim in dimensions:
        print(f"Testing {dim}D (Pattern 4: e_4 + e_11 × e_1 - e_14)...")
        result = test_canonical_six_at_dimension(dim)
        results.append(result)

        status = "PASS" if result['is_zero_divisor'] else "FAIL"
        print(f"  |P| = {result['p_norm']:.6f}")
        print(f"  |Q| = {result['q_norm']:.6f}")
        print(f"  |P × Q| = {result['product_norm']:.2e}")
        print(f"  Status: {status}")
        print()

    print("="*80)
    print("SUMMARY")
    print("="*80)

    all_passed = all(r['is_zero_divisor'] for r in results)

    for r in results:
        status = "OK" if r['is_zero_divisor'] else "XX"
        print(f"  [{status}] {r['dimension']:3d}D - Product norm: {r['product_norm']:.2e}")

    print()
    if all_passed:
        print("SUCCESS: All dimensions (16D-256D) support Canonical Six patterns!")
    else:
        print("ERROR: Some dimensions failed zero divisor tests")

    print()
    print("Supported dimensions: 16, 32, 64, 128, 256")
    print("Note: 512D and beyond require custom libraries (not yet implemented)")
    print()


if __name__ == "__main__":
    main()
