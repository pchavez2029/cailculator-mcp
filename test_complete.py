"""
Test script for Complete Dataset Analysis
"""

import asyncio
import sys
import json
import numpy as np

try:
    from cailculator_mcp.tools import analyze_dataset
except ImportError:
    print("Error: Cannot import cailculator_mcp. Make sure you've installed it with 'pip install -e .'")
    sys.exit(1)


async def test_complete_analysis():
    """Test complete dataset analysis"""
    print("="*60)
    print("COMPLETE DATASET ANALYSIS TEST")
    print("="*60)
    print()
    
    # Create interesting test data: Gaussian with some structure
    x = np.linspace(-3, 3, 30)
    data = (np.exp(-x**2) * np.cos(2*x) + 1.5).tolist()
    
    print(f"Input: Structured data with {len(data)} points")
    print(f"  Range: [{min(data):.2f}, {max(data):.2f}]")
    print()
    
    result = await analyze_dataset({
        "data": data,
        "include_transform": True,
        "include_patterns": True,
        "include_statistics": True
    })
    
    if not result.get('success'):
        print(f"❌ Error: {result.get('error')}")
        return
    
    print("✅ Analysis Complete!")
    print()
    
    # Data Summary
    print("-" * 60)
    print("DATA SUMMARY")
    print("-" * 60)
    summary = result.get('data_summary', {})
    print(f"Size: {summary.get('size')} points")
    print(f"Range: {summary.get('range')}")
    print()
    
    # Statistics
    if 'statistics' in result:
        print("-" * 60)
        print("STATISTICS")
        print("-" * 60)
        stats = result['statistics']
        print(f"Mean:     {stats['mean']:.4f}")
        print(f"Median:   {stats['median']:.4f}")
        print(f"Std Dev:  {stats['std']:.4f}")
        print(f"Variance: {stats['variance']:.4f}")
        print(f"Min:      {stats['min']:.4f}")
        print(f"Max:      {stats['max']:.4f}")
        print()
    
    # Transform Results
    if 'transform' in result:
        print("-" * 60)
        print("CHAVEZ TRANSFORM")
        print("-" * 60)
        transform = result['transform']
        
        if transform.get('success'):
            print(f"Transform Value: {transform['transform_value']:.6e}")
            print(f"Pattern ID: {transform['pattern_id']}")
            print(f"Alpha: {transform['alpha']}")
            
            convergence = transform.get('convergence', {})
            print(f"\nConvergence:")
            print(f"  Rate: {convergence.get('rate', 0)*100:.1f}%")
            print(f"  All Converged: {'✅' if convergence.get('all_converged') else '⚠️'}")
            
            stability = transform.get('stability', {})
            print(f"\nStability:")
            print(f"  Bound Satisfied: {'✅' if stability.get('bound_satisfied') else '⚠️'}")
            print(f"  Ratio: {stability.get('ratio', 0):.6f}")
        else:
            print(f"❌ Transform Error: {transform.get('error')}")
        print()
    
    # Pattern Detection
    if 'patterns' in result:
        print("-" * 60)
        print("PATTERN DETECTION")
        print("-" * 60)
        patterns = result['patterns']
        
        if patterns.get('success'):
            num_patterns = patterns.get('patterns_found', 0)
            print(f"Patterns Found: {num_patterns}")
            print()
            
            for i, pattern in enumerate(patterns.get('patterns', []), 1):
                confidence = pattern['confidence']
                emoji = "🔴" if confidence > 0.8 else "🟡" if confidence > 0.5 else "⚪"
                
                print(f"{emoji} Pattern {i}: {pattern['type']}")
                print(f"   Confidence: {confidence:.1%}")
                print(f"   {pattern['description']}")
                print()
        else:
            print(f"❌ Pattern Detection Error: {patterns.get('error')}")
        print()
    
    # Interpretation
    if 'interpretation' in result:
        print("-" * 60)
        print("INTERPRETATION")
        print("-" * 60)
        print(result['interpretation'])
        print()
    
    print("="*60)


async def test_minimal_analysis():
    """Test with minimal options"""
    print("="*60)
    print("MINIMAL ANALYSIS TEST (Statistics Only)")
    print("="*60)
    print()
    
    data = [1, 2, 3, 4, 5]
    print(f"Input: {data}")
    print()
    
    result = await analyze_dataset({
        "data": data,
        "include_transform": False,
        "include_patterns": False,
        "include_statistics": True
    })
    
    if result.get('success'):
        print("✅ Success!")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Error: {result.get('error')}")
    
    print()
    print("="*60)
    print()


async def test_large_dataset():
    """Test with larger dataset"""
    print("="*60)
    print("LARGE DATASET TEST")
    print("="*60)
    print()
    
    # Generate 200 points of interesting data
    x = np.linspace(0, 10, 200)
    data = (np.sin(x) * np.exp(-0.1*x) + np.cos(2*x) * 0.3).tolist()
    
    print(f"Input: {len(data)} points")
    print("Analyzing...")
    print()
    
    import time
    start = time.time()
    
    result = await analyze_dataset({
        "data": data,
        "include_transform": True,
        "include_patterns": True,
        "include_statistics": True
    })
    
    elapsed = time.time() - start
    
    if result.get('success'):
        print(f"✅ Success! (took {elapsed:.2f}s)")
        print()
        print("Quick Summary:")
        print(f"  Data points: {result['data_summary']['size']}")
        
        if 'statistics' in result:
            stats = result['statistics']
            print(f"  Mean: {stats['mean']:.4f}")
            print(f"  Std: {stats['std']:.4f}")
        
        if 'patterns' in result and result['patterns'].get('success'):
            num = result['patterns']['patterns_found']
            print(f"  Patterns detected: {num}")
        
        if 'transform' in result and result['transform'].get('success'):
            val = result['transform']['transform_value']
            print(f"  Transform value: {val:.6e}")
        
        print()
        print(f"Interpretation: {result.get('interpretation', 'N/A')[:150]}...")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    print()
    print("="*60)
    print()


async def main():
    """Run all complete analysis tests"""
    print("\n")
    print("📊 CAILculator MCP - Complete Analysis Tests")
    print()
    
    await test_complete_analysis()
    await test_minimal_analysis()
    await test_large_dataset()
    
    print("="*60)
    print("✅ ALL TESTS COMPLETE")
    print("="*60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
