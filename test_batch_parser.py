"""
Test script for batch parser and format handlers.

Run this to test the batch mode functionality with your test data.
"""

from pathlib import Path
from backend.app.batch_parser import parse_batch_file
from backend.app.tauargus_formats import TauArgusFormatHandler

def test_batch_parser():
    """Test parsing batch files."""
    print("=" * 70)
    print("TESTING BATCH PARSER")
    print("=" * 70)
    
    # Test TestTable.arb (simple)
    print("\n1. Testing TestTable.arb...")
    batch_file = Path("test_data/batch/TestTable.arb")
    
    if not batch_file.exists():
        print(f"❌ File not found: {batch_file}")
        return
    
    try:
        batch = parse_batch_file(str(batch_file))
        print(f"✅ Parsed successfully!")
        print(f"   Commands: {len(batch.commands)}")
        print(f"   Data file: {batch.table_data_file}")
        print(f"   Metadata file: {batch.metadata_file}")
        print(f"   Table spec: {batch.table_spec}")
        print(f"   Safety rules: {batch.safety_rules}")
        print(f"   Method: {batch.suppression_method}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_format_handlers():
    """Test format handlers with real data."""
    print("\n" + "=" * 70)
    print("TESTING FORMAT HANDLERS")
    print("=" * 70)
    
    # Test .tab parser
    print("\n2. Testing .tab parser (pp.tab)...")
    tab_file = Path("test_data/batch/pp.tab")
    
    if not tab_file.exists():
        print(f"❌ File not found: {tab_file}")
        return
    
    try:
        df = TauArgusFormatHandler.parse_tab_file(str(tab_file))
        print(f"✅ Parsed successfully!")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")
        print(f"   Column names: {df.columns.tolist()}")
        print(f"\n   Sample data (first 3 rows):")
        print(df.head(3))
        
        # Count status codes
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts()
            print(f"\n   Status distribution:")
            for status, count in status_counts.items():
                print(f"      {status}: {count}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test .rda parser
    print("\n3. Testing .rda parser (pp.rda)...")
    rda_file = Path("test_data/batch/pp.rda")
    
    if not rda_file.exists():
        print(f"❌ File not found: {rda_file}")
        return
    
    try:
        metadata = TauArgusFormatHandler.parse_rda_file(str(rda_file))
        print(f"✅ Parsed successfully!")
        print(f"   Variables: {len(metadata.variables)}")
        print(f"   Variable names: {[v.name for v in metadata.variables]}")
        print(f"\n   Variable details:")
        for var in metadata.variables:
            print(f"      - {var.name}: {var.type}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test .hrc parser
    print("\n4. Testing .hrc parser (region2.hrc)...")
    hrc_file = Path("test_data/batch/region2.hrc")
    
    if not hrc_file.exists():
        print(f"❌ File not found: {hrc_file}")
        return
    
    try:
        hierarchy = TauArgusFormatHandler.parse_hrc_file(str(hrc_file))
        print(f"✅ Parsed successfully!")
        print(f"   Total nodes: {len(hierarchy)}")
        
        # Count by level
        level_counts = {}
        for code, info in hierarchy.items():
            level = info['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print(f"   Hierarchy levels:")
        for level in sorted(level_counts.keys()):
            print(f"      Level {level}: {level_counts[level]} nodes")
        
        print(f"\n   Top-level regions:")
        for code, info in hierarchy.items():
            if info['level'] == 0:
                print(f"      - {code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_full_workflow():
    """Test complete workflow: parse batch file and load data."""
    print("\n" + "=" * 70)
    print("TESTING FULL WORKFLOW")
    print("=" * 70)
    
    print("\n5. Testing complete batch workflow...")
    batch_file = Path("test_data/batch/TestTable.arb")
    
    try:
        # Parse batch file
        batch = parse_batch_file(str(batch_file))
        print(f"✅ Batch file parsed")
        
        # Update paths to be relative to current directory
        if batch.table_data_file:
            # Extract filename and use local path
            filename = Path(batch.table_data_file).name
            batch.table_data_file = f"test_data/batch/{filename}"
        
        if batch.metadata_file:
            filename = Path(batch.metadata_file).name
            batch.metadata_file = f"test_data/batch/{filename}"
        
        print(f"   Data file: {batch.table_data_file}")
        print(f"   Metadata file: {batch.metadata_file}")
        
        # Check files exist
        if not Path(batch.table_data_file).exists():
            print(f"❌ Data file not found: {batch.table_data_file}")
            return
        
        if not Path(batch.metadata_file).exists():
            print(f"❌ Metadata file not found: {batch.metadata_file}")
            return
        
        # Load data
        df = TauArgusFormatHandler.parse_tab_file(batch.table_data_file)
        print(f"✅ Data loaded: {len(df)} cells")
        
        # Load metadata
        metadata = TauArgusFormatHandler.parse_rda_file(batch.metadata_file)
        print(f"✅ Metadata loaded: {len(metadata.variables)} variables")
        
        # Display summary
        print(f"\n   📊 DATA SUMMARY:")
        print(f"      Total cells: {len(df)}")
        print(f"      Variables: {', '.join([v.name for v in metadata.variables])}")
        
        if 'Status' in df.columns:
            unsafe_count = (df['Status'] == 'U').sum()
            safe_count = (df['Status'] == 'S').sum()
            empty_count = (df['Status'] == 'E').sum()
            print(f"      Unsafe cells: {unsafe_count}")
            print(f"      Safe cells: {safe_count}")
            print(f"      Empty cells: {empty_count}")
        
        print(f"\n✅ FULL WORKFLOW SUCCESSFUL!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 SPAAS Batch Mode Test Suite\n")
    
    test_batch_parser()
    test_format_handlers()
    test_full_workflow()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Start backend: cd backend && uvicorn app.main:app --reload")
    print("  2. Test API: POST to http://localhost:8000/batch/parse/")
    print("  3. Use frontend to upload batch files")
    print()
