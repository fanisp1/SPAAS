"""
Advanced Test Script for Hypercube Secondary Suppression

This script demonstrates all protection rules:
- Frequency rule
- Dominance rule
- P-percent rule

Run this to verify the enhanced implementation.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.hypercube import hypercube_suppress, ProtectionRules


def create_test_data_frequency():
    """Test data for frequency rule"""
    data = {
        'Category_A': [45, 2, 12, 78],
        'Category_B': [120, 1, 23, 145],
        'Category_C': [67, 8, 15, 92]
    }
    return pd.DataFrame(data, index=['Region_1', 'Region_2', 'Region_3', 'Region_4'])


def create_test_data_dominance():
    """Test data for dominance rule - one value dominates"""
    data = {
        'Product_A': [500, 10, 5, 8],    # First value dominates (>80%)
        'Product_B': [30, 40, 35, 45],    # Balanced
        'Product_C': [450, 12, 15, 20]    # First value dominates
    }
    return pd.DataFrame(data, index=['Company_1', 'Company_2', 'Company_3', 'Company_4'])


def create_test_data_mixed():
    """Test data with multiple rule violations"""
    data = {
        'Sales_Q1': [1000, 2, 50, 800, 45],  # Row 1: frequency issue (2)
        'Sales_Q2': [1200, 5, 60, 900, 50],  # Row 1: frequency issue (5)
        'Sales_Q3': [1100, 1, 55, 850, 48],  # Row 1: frequency issue (1)
        'Sales_Q4': [1300, 3, 65, 950, 52]   # Mixed issues
    }
    return pd.DataFrame(data, index=['Major_Corp', 'Small_Co', 'Medium_Co', 'Large_Corp', 'Mid_Co'])


def run_test(test_name, data, protection_rules):
    """Run a single test case"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    
    print("\n📊 Original Table:")
    print(data)
    print(f"\nTable dimensions: {data.shape[0]} rows × {data.shape[1]} columns = {data.shape[0] * data.shape[1]} cells")
    
    print("\n🔒 Protection Rules:")
    print(f"  - Min Frequency: {protection_rules.min_frequency}")
    print(f"  - Dominance: {protection_rules.dominance_n}-{protection_rules.dominance_k}% rule")
    print(f"  - P-Percent: {protection_rules.p_percent}%")
    
    print("\n⚙️  Running hypercube suppression...")
    
    try:
        suppressed_df, statistics = hypercube_suppress(
            data=data,
            protection_rules=protection_rules
        )
        
        print("\n✅ Suppression completed!")
        
        print("\n📋 Suppressed Table:")
        print(suppressed_df)
        
        print("\n📊 Statistics:")
        print("-" * 70)
        print(f"  Total Cells:            {statistics['total_cells']}")
        print(f"  Primary Suppressions:   {statistics['primary_suppressions']}")
        print(f"  Secondary Suppressions: {statistics['secondary_suppressions']}")
        print(f"  Total Suppressions:     {statistics['total_suppressions']}")
        print(f"  Suppression Rate:       {statistics['suppression_rate']:.2%}")
        print(f"  Method:                 {statistics['method']}")
        
        # Save results
        output_file = f"suppressed_{test_name.lower().replace(' ', '_')}.csv"
        suppressed_df.to_csv(output_file)
        print(f"\n💾 Results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all test cases"""
    
    print("="*70)
    print("🔬 SPAAS ADVANCED HYPERCUBE SUPPRESSION TEST SUITE")
    print("="*70)
    print("\nThis test suite demonstrates all protection rules:")
    print("  1. Frequency Rule - protects cells with small counts")
    print("  2. Dominance Rule - protects when top contributors dominate")
    print("  3. P-Percent Rule - protects estimable values")
    print()
    
    results = {}
    
    # Test 1: Frequency Rule
    print("\n" + "🔹"*35)
    print("Test 1: Frequency Rule Focus")
    print("🔹"*35)
    
    rules_frequency = ProtectionRules(
        min_frequency=5,      # Stricter: suppress cells < 5
        dominance_n=1,
        dominance_k=85.0,     # Less strict dominance
        p_percent=20.0        # Less strict p-percent
    )
    
    data1 = create_test_data_frequency()
    results['Frequency Rule'] = run_test('Frequency Rule', data1, rules_frequency)
    
    # Test 2: Dominance Rule
    print("\n" + "🔹"*35)
    print("Test 2: Dominance Rule Focus")
    print("🔹"*35)
    
    rules_dominance = ProtectionRules(
        min_frequency=3,       # Less strict frequency
        dominance_n=1,         # Single dominance
        dominance_k=70.0,      # Stricter: 70% dominance threshold
        p_percent=20.0
    )
    
    data2 = create_test_data_dominance()
    results['Dominance Rule'] = run_test('Dominance Rule', data2, rules_dominance)
    
    # Test 3: Mixed Rules
    print("\n" + "🔹"*35)
    print("Test 3: All Rules Combined")
    print("🔹"*35)
    
    rules_mixed = ProtectionRules(
        min_frequency=3,
        dominance_n=1,
        dominance_k=75.0,
        p_percent=15.0
    )
    
    data3 = create_test_data_mixed()
    results['Mixed Rules'] = run_test('Mixed Rules', data3, rules_mixed)
    
    # Test 4: Balanced Protection
    print("\n" + "🔹"*35)
    print("Test 4: Balanced Protection")
    print("🔹"*35)
    
    rules_balanced = ProtectionRules(
        min_frequency=3,
        dominance_n=2,          # Top 2 dominance
        dominance_k=80.0,
        p_percent=10.0
    )
    
    results['Balanced'] = run_test('Balanced Protection', data1, rules_balanced)
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUITE SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        return 0
    else:
        print("⚠️  Some tests failed - review errors above")
        print("="*70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
