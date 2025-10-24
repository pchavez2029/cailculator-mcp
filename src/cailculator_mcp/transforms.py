"""
Chavez Transform - A Novel Integral Transform for High-Dimensional Data

This module implements the Chavez Transform, which uses zero divisor structure
from Cayley-Dickson algebras to transform high-dimensional data, analogous to
how Fourier Transforms work in frequency space.

Definition:
    For f in L^1(D), D subset of R^n:

    C[f] = integral_D f(x) * K_Z(P,x) * Omega_d(x) dx

    Where:
        K_Z(P,x) = sum_i |z_i(P)|^2 * exp(-alpha * ||x - x_i||^2)
        z_i(P) = zero divisor components of P in P_32 (pathions)
        Omega_d(x) = (1 + ||x||^2)^(-d/2)
        alpha > 0 = convergence parameter
        x_i = zero divisor loci in P

Theorems:
    1. Convergence: For bounded f in L^1(D) and alpha > 0, C[f] converges absolutely
    2. Stability Bounds: |C[f]| <= M * ||f||_1 where M = ||P||^2 * sqrt(pi/alpha)^n
"""

import numpy as np
from scipy import integrate
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from typing import Callable, Tuple, List, Optional
import sys
import os

# Add parent directory to path for hypercomplex import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from hypercomplex import Pathion
except ImportError:
    print("Warning: hypercomplex library not found. Using mock implementation.")
    # Mock Pathion class for testing
    class Pathion:
        def __init__(self, *coeffs):
            self.coeffs = np.array(coeffs if coeffs else [0.0]*32)
        def __mul__(self, other):
            # Simplified mock multiplication
            result_coeffs = [0.0] * 32
            return Pathion(*result_coeffs)
        def __abs__(self):
            return np.linalg.norm(self.coeffs)


class ChavezTransform:
    """
    Implements the Chavez Transform for high-dimensional data using zero divisor kernels.
    """

    def __init__(self, dimension: int = 32, alpha: float = 1.0):
        """
        Initialize the Chavez Transform.

        Args:
            dimension: Dimension of the ambient space (default: 32 for pathions)
            alpha: Convergence parameter (must be > 0)
        """
        if alpha <= 0:
            raise ValueError("alpha must be positive")

        self.dimension = dimension
        self.alpha = alpha

    def zero_divisor_kernel(self, P: Pathion, x: np.ndarray,
                           zero_divisor_loci: Optional[np.ndarray] = None) -> float:
        """
        Compute the zero divisor kernel K_Z(P, x).

        K_Z(P,x) = sum_i |z_i(P)|^2 * exp(-alpha * ||x - x_i||^2)

        Args:
            P: Pathion element (zero divisor)
            x: Point in R^n where to evaluate kernel
            zero_divisor_loci: Array of zero divisor loci x_i (if None, uses canonical basis)

        Returns:
            Kernel value at x
        """
        # Extract zero divisor components
        z_components = np.array(P.coefficients())

        # If no loci provided, use canonical basis points
        if zero_divisor_loci is None:
            zero_divisor_loci = np.eye(len(z_components))

        # Ensure x has correct dimension
        if len(x) < len(z_components):
            x = np.pad(x, (0, len(z_components) - len(x)), mode='constant')
        elif len(x) > len(z_components):
            x = x[:len(z_components)]

        # Compute kernel sum
        kernel_value = 0.0
        for i, (z_i, x_i) in enumerate(zip(z_components, zero_divisor_loci)):
            magnitude_sq = np.abs(z_i) ** 2
            distance_sq = np.linalg.norm(x - x_i) ** 2
            kernel_value += magnitude_sq * np.exp(-self.alpha * distance_sq)

        return kernel_value

    def dimensional_weighting(self, x: np.ndarray, d: int) -> float:
        """
        Compute dimensional weighting Omega_d(x).

        Omega_d(x) = (1 + ||x||^2)^(-d/2)

        Args:
            x: Point in R^n
            d: Dimension parameter

        Returns:
            Weighting value at x
        """
        norm_sq = np.linalg.norm(x) ** 2
        return (1.0 + norm_sq) ** (-d / 2.0)

    def integrand(self, x: np.ndarray, f: Callable, P: Pathion, d: int,
                  zero_divisor_loci: Optional[np.ndarray] = None) -> float:
        """
        Compute the integrand f(x) * K_Z(P,x) * Omega_d(x).

        Args:
            x: Point in R^n
            f: Function to transform
            P: Zero divisor pathion
            d: Dimension parameter for weighting
            zero_divisor_loci: Zero divisor loci

        Returns:
            Integrand value at x
        """
        f_val = f(x)
        kernel_val = self.zero_divisor_kernel(P, x, zero_divisor_loci)
        weight_val = self.dimensional_weighting(x, d)

        return f_val * kernel_val * weight_val

    def transform_1d(self, f: Callable, P: Pathion, d: int,
                     domain: Tuple[float, float] = (-5.0, 5.0),
                     zero_divisor_loci: Optional[np.ndarray] = None) -> float:
        """
        Compute the Chavez Transform in 1D using numerical integration.

        Args:
            f: Function to transform (callable taking 1D array)
            P: Zero divisor pathion
            d: Dimension parameter
            domain: Integration domain (a, b)
            zero_divisor_loci: Zero divisor loci

        Returns:
            Transform value C[f]
        """
        def integrand_1d(x_scalar):
            x = np.array([x_scalar])
            return self.integrand(x, f, P, d, zero_divisor_loci)

        result, error = integrate.quad(integrand_1d, domain[0], domain[1])
        return result

    def transform_nd(self, f: Callable, P: Pathion, d: int,
                     domain_ranges: List[Tuple[float, float]],
                     zero_divisor_loci: Optional[np.ndarray] = None,
                     method: str = 'monte_carlo',
                     num_samples: int = 10000) -> float:
        """
        Compute the Chavez Transform in N-D using numerical integration.

        Args:
            f: Function to transform (callable taking ND array)
            P: Zero divisor pathion
            d: Dimension parameter
            domain_ranges: List of (min, max) for each dimension
            zero_divisor_loci: Zero divisor loci
            method: Integration method ('monte_carlo' or 'grid')
            num_samples: Number of samples for Monte Carlo

        Returns:
            Transform value C[f]
        """
        n = len(domain_ranges)

        if method == 'monte_carlo':
            # Monte Carlo integration
            samples = np.random.uniform(
                low=[r[0] for r in domain_ranges],
                high=[r[1] for r in domain_ranges],
                size=(num_samples, n)
            )

            volume = np.prod([r[1] - r[0] for r in domain_ranges])

            integrand_values = np.array([
                self.integrand(x, f, P, d, zero_divisor_loci)
                for x in samples
            ])

            result = volume * np.mean(integrand_values)

        elif method == 'grid':
            # Grid-based integration (only practical for low dimensions)
            if n > 3:
                raise ValueError("Grid integration only practical for n <= 3")

            # Create grid
            grid_size = int(num_samples ** (1/n))
            grids = [np.linspace(r[0], r[1], grid_size) for r in domain_ranges]
            mesh = np.meshgrid(*grids, indexing='ij')
            points = np.stack([m.ravel() for m in mesh], axis=-1)

            # Evaluate integrand
            integrand_values = np.array([
                self.integrand(x, f, P, d, zero_divisor_loci)
                for x in points
            ])

            # Trapezoidal rule
            dx = np.prod([(r[1] - r[0]) / (grid_size - 1) for r in domain_ranges])
            result = np.sum(integrand_values) * dx

        else:
            raise ValueError(f"Unknown method: {method}")

        return result

    def verify_convergence_theorem(self, f: Callable, P: Pathion, d: int,
                                   domain: Tuple[float, float] = (-5.0, 5.0),
                                   num_trials: int = 10) -> dict:
        """
        Verify Theorem 1: Convergence theorem.

        For bounded f in L^1(D) and alpha > 0, C[f] converges absolutely.

        Args:
            f: Test function
            P: Zero divisor pathion
            d: Dimension parameter
            domain: Integration domain
            num_trials: Number of different alpha values to test

        Returns:
            Dictionary with convergence analysis results
        """
        alphas = np.logspace(-1, 2, num_trials)  # Test alpha from 0.1 to 100
        results = []

        for alpha_test in alphas:
            # Temporarily change alpha
            old_alpha = self.alpha
            self.alpha = alpha_test

            try:
                transform_value = self.transform_1d(f, P, d, domain)
                converged = np.isfinite(transform_value)
                results.append({
                    'alpha': alpha_test,
                    'value': transform_value,
                    'converged': converged
                })
            except Exception as e:
                results.append({
                    'alpha': alpha_test,
                    'value': np.nan,
                    'converged': False,
                    'error': str(e)
                })
            finally:
                self.alpha = old_alpha

        convergence_rate = sum(r['converged'] for r in results) / len(results)

        return {
            'theorem': 'Convergence (Theorem 1)',
            'convergence_rate': convergence_rate,
            'all_converged': convergence_rate == 1.0,
            'results': results
        }

    def verify_stability_bounds(self, f: Callable, P: Pathion, d: int,
                               domain: Tuple[float, float] = (-5.0, 5.0),
                               num_trials: int = 10) -> dict:
        """
        Verify Theorem 2: Stability bounds.

        |C[f]| <= M * ||f||_1 where M = ||P||^2 * sqrt(pi/alpha)^n

        Args:
            f: Test function
            P: Zero divisor pathion
            d: Dimension parameter
            domain: Integration domain
            num_trials: Number of tests with different functions

        Returns:
            Dictionary with stability analysis results
        """
        # Compute M (stability constant)
        n = 1  # For 1D test
        P_norm = abs(P)
        M = (P_norm ** 2) * ((np.pi / self.alpha) ** (n / 2))

        # Compute L1 norm of f
        def abs_f(x_scalar):
            x = np.array([x_scalar])
            return np.abs(f(x))

        f_L1_norm, _ = integrate.quad(abs_f, domain[0], domain[1])

        # Compute transform
        transform_value = self.transform_1d(f, P, d, domain)

        # Check bound
        bound = M * f_L1_norm
        satisfied = np.abs(transform_value) <= bound

        ratio = np.abs(transform_value) / bound if bound > 0 else np.inf

        return {
            'theorem': 'Stability Bounds (Theorem 2)',
            'transform_value': transform_value,
            'stability_constant_M': M,
            'f_L1_norm': f_L1_norm,
            'theoretical_bound': bound,
            'bound_satisfied': satisfied,
            'ratio': ratio,
            'alpha': self.alpha,
            'P_norm': P_norm
        }


def create_canonical_six_pathion(pattern_id: int = 1) -> Pathion:
    """
    Create a Pathion corresponding to one of the Canonical Six patterns.

    Args:
        pattern_id: Which canonical pattern to use (1-6)

    Returns:
        Pathion zero divisor
    """
    # Canonical Six patterns in 16D (sedenions), embedded in 32D
    # Pattern structure: (e_a + e_b) where a+b = 15

    patterns = {
        1: (1, 14),   # e_1 + e_14
        2: (2, 13),   # e_2 + e_13
        3: (3, 12),   # e_3 + e_12
        4: (4, 11),   # e_4 + e_11
        5: (5, 10),   # e_5 + e_10
        6: (6, 9),    # e_6 + e_9
    }

    if pattern_id not in patterns:
        raise ValueError(f"pattern_id must be 1-6, got {pattern_id}")

    a, b = patterns[pattern_id]

    # Create pathion with 1.0 in positions a and b
    coeffs = [0.0] * 32
    coeffs[a] = 1.0
    coeffs[b] = 1.0

    return Pathion(*coeffs)


def test_functions():
    """
    Create a suite of test functions for validation.

    Returns:
        Dictionary of test functions
    """
    return {
        'gaussian': lambda x: np.exp(-np.linalg.norm(x)**2),
        'polynomial': lambda x: 1.0 + np.sum(x**2),
        'exponential_decay': lambda x: np.exp(-np.abs(np.sum(x))),
        'sinc': lambda x: np.sinc(np.linalg.norm(x)),
        'bounded_oscillatory': lambda x: np.sin(np.linalg.norm(x)) * np.exp(-0.1 * np.linalg.norm(x)**2),
    }


if __name__ == "__main__":
    print("="*80)
    print("CHAVEZ TRANSFORM - IMPLEMENTATION AND VERIFICATION")
    print("="*80)
    print()

    # Initialize transform
    print("Initializing Chavez Transform...")
    alpha = 1.0
    dimension = 32
    ct = ChavezTransform(dimension=dimension, alpha=alpha)
    print(f"  Dimension: {dimension}")
    print(f"  Alpha: {alpha}")
    print()

    # Create Canonical Six pathion
    print("Creating Canonical Six pathion (Pattern 1: e_1 + e_14)...")
    P = create_canonical_six_pathion(pattern_id=1)
    print(f"  P norm: {abs(P):.6f}")
    print(f"  Non-zero components: {np.sum(np.abs(np.array(P.coefficients())) > 1e-10)}")
    print()

    # Load test functions
    print("="*80)
    print("TEST FUNCTION SUITE")
    print("="*80)
    print()

    test_funcs = test_functions()

    for name, f in test_funcs.items():
        print(f"Testing with {name} function...")

        # Compute transform
        d = 2  # Dimension parameter for weighting
        domain = (-3.0, 3.0)

        try:
            transform_value = ct.transform_1d(f, P, d, domain)
            print(f"  C[{name}] = {transform_value:.6e}")
        except Exception as e:
            print(f"  Error: {e}")

        print()

    # Verify Theorem 1: Convergence
    print("="*80)
    print("THEOREM 1: CONVERGENCE VERIFICATION")
    print("="*80)
    print()

    f_test = test_funcs['gaussian']
    convergence_results = ct.verify_convergence_theorem(f_test, P, d=2, num_trials=10)

    print(f"Convergence rate: {convergence_results['convergence_rate']*100:.1f}%")
    print(f"All tests converged: {convergence_results['all_converged']}")
    print()
    print("Alpha values tested:")
    for r in convergence_results['results']:
        status = "CONVERGED" if r['converged'] else "FAILED"
        print(f"  alpha={r['alpha']:.3f}: C[f]={r.get('value', 'N/A'):.6e} [{status}]")
    print()

    # Verify Theorem 2: Stability Bounds
    print("="*80)
    print("THEOREM 2: STABILITY BOUNDS VERIFICATION")
    print("="*80)
    print()

    stability_results = ct.verify_stability_bounds(f_test, P, d=2)

    print(f"Transform value: |C[f]| = {np.abs(stability_results['transform_value']):.6e}")
    print(f"Stability constant M: {stability_results['stability_constant_M']:.6e}")
    print(f"||f||_1: {stability_results['f_L1_norm']:.6e}")
    print(f"Theoretical bound: M * ||f||_1 = {stability_results['theoretical_bound']:.6e}")
    print(f"Bound satisfied: {stability_results['bound_satisfied']}")
    print(f"Ratio |C[f]| / bound: {stability_results['ratio']:.6f}")
    print()

    if stability_results['bound_satisfied']:
        print("SUCCESS: Stability bound is satisfied!")
    else:
        print("WARNING: Stability bound violated!")

    print()

    # Test all Canonical Six patterns
    print("="*80)
    print("CANONICAL SIX PATTERNS - TRANSFORM VALUES")
    print("="*80)
    print()

    for pattern_id in range(1, 7):
        P_pattern = create_canonical_six_pathion(pattern_id)
        transform_val = ct.transform_1d(test_funcs['gaussian'], P_pattern, d=2)
        print(f"Pattern {pattern_id}: C[gaussian] = {transform_val:.6e}")

    print()
    print("="*80)
    print("CHAVEZ TRANSFORM IMPLEMENTATION COMPLETE")
    print("="*80)
