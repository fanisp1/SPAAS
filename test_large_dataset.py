"""
Quick test of large dataset with hypercube method
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import pandas as pd
from app.hypercube import hypercube_suppress, ProtectionRules

print("📊 Loading large test dataset...")
df = pd.read_csv('large_test_data.csv')

print(f"✅ Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"\nColumns: {list(df.columns)}")
print(f"\nNumeric columns: {list(df.select_dtypes(include=['number']).columns)}")
print(f"\nFirst few rows:")
print(df.head())

print("\n🔒 Running hypercube suppression...")
print("This may take 10-30 seconds for a large dataset...")

rules = ProtectionRules(min_frequency=3)

try:
    suppressed_df, stats = hypercube_suppress(df, rules)
    
    print("\n✅ Success!")
    print(f"\n📊 Statistics:")
    print(f"   - Total cells: {stats['total_cells']}")
    print(f"   - Primary suppressions: {stats['primary_suppressions']}")
    print(f"   - Secondary suppressions: {stats['secondary_suppressions']}")
    print(f"   - Suppression rate: {stats['suppression_rate']:.2%}")
    
    print(f"\n👀 Preview of suppressed data:")
    print(suppressed_df.head())
    
    print("\n✅ Large dataset test passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
