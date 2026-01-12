"""
Test script for Hypercube Secondary Suppression

This script demonstrates the hypercube functionality with a sample dataset.
Run this to verify that the implementation works correctly.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.hypercube import hypercube_suppress, ProtectionRules


def create_sample_data():
    """Create a sample statistical table for testing"""
    
    # Sample data: Cross-tabulation of age groups vs income levels
    # Small values represent sensitive cells that need protection
    data = {
        'Low Income': [45, 2, 12, 78, 34],
        'Medium Income': [120, 8, 23, 145, 89],
        'High Income': [67, 1, 15, 92, 56]
    }
    
    df = pd.DataFrame(data, index=[
        '18-25', '26-35', '36-45', '46-55', '56+'
    ])
    
    return df


def main():
    """Run hypercube suppression test"""
    
    print("=" * 70)
    print("SPAAS Hypercube Suppression Test")
    print("=" * 70)
    print()
    
    # Create sample data
    print("Step 1: Creating sample statistical table...")
    df = create_sample_data()
    
    print("\nOriginal Table:")
    print(df)
    print()
    
    # Configure protection rules
    print("Step 2: Configuring protection rules...")
    protection_rules = ProtectionRules(
        min_frequency=3,      # Suppress cells with values < 3
        dominance_n=1,        # Check single dominance
        dominance_k=80.0,     # 80% dominance threshold
        p_percent=10.0        # 10% protection level
    )
    print(f"  - Minimum Frequency: {protection_rules.min_frequency}")
    print(f"  - Dominance Rule: {protection_rules.dominance_n}-dominance at {protection_rules.dominance_k}%")
    print(f"  - P-Percent Rule: {protection_rules.p_percent}%")
    print()
    
    # Run hypercube suppression
    print("Step 3: Running hypercube suppression algorithm...")
    print("  (This may take a few moments...)")
    print()
    
    try:
        suppressed_df, statistics = hypercube_suppress(
            data=df,
            protection_rules=protection_rules
        )
        
        print("✓ Suppression completed successfully!")
        print()
        
        # Display results
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print()
        
        print("Suppressed Table:")
        print(suppressed_df)
        print()
        
        print("Statistics:")
        print("-" * 70)
        print(f"  Total Cells:            {statistics['total_cells']}")
        print(f"  Primary Suppressions:   {statistics['primary_suppressions']}")
        print(f"  Secondary Suppressions: {statistics['secondary_suppressions']}")
        print(f"  Total Suppressions:     {statistics['total_suppressions']}")
        print(f"  Suppression Rate:       {statistics['suppression_rate']:.2%}")
        print(f"  Method:                 {statistics['method']}")
        print()
        
        print("Protection Rules Applied:")
        print("-" * 70)
        for key, value in statistics['protection_rules'].items():
            print(f"  {key}: {value}")
        print()
        
        # Save results
        output_file = "suppressed_output.csv"
        suppressed_df.to_csv(output_file)
        print(f"✓ Results saved to: {output_file}")
        print()
        
        print("=" * 70)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    except Exception as e:
        print(f"✗ Error during suppression: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
