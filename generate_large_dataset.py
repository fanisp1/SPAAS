"""
Generate Large Test Dataset for SPAAS

Creates a realistic statistical table with various characteristics:
- Multiple dimensions (regions, products, time periods)
- Mix of small and large values (to test all protection rules)
- Realistic business data scenario
"""

import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

print("🔧 Generating large test dataset...")
print()

# Configuration
NUM_REGIONS = 50
NUM_PRODUCTS = 20
NUM_TIME_PERIODS = 12

# Generate regions (US states, major cities, etc.)
regions = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
    'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
    'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte',
    'San Francisco', 'Indianapolis', 'Seattle', 'Denver', 'Boston',
    'El Paso', 'Nashville', 'Detroit', 'Oklahoma City', 'Portland',
    'Las Vegas', 'Memphis', 'Louisville', 'Baltimore', 'Milwaukee',
    'Albuquerque', 'Tucson', 'Fresno', 'Mesa', 'Sacramento',
    'Atlanta', 'Kansas City', 'Colorado Springs', 'Omaha', 'Raleigh',
    'Miami', 'Long Beach', 'Virginia Beach', 'Oakland', 'Minneapolis',
    'Tulsa', 'Tampa', 'Arlington', 'New Orleans', 'Wichita'
]

# Generate product categories
products = [
    'Electronics', 'Clothing', 'Food & Beverage', 'Home & Garden', 'Sports',
    'Books', 'Toys', 'Healthcare', 'Automotive', 'Beauty',
    'Office Supplies', 'Pet Supplies', 'Jewelry', 'Music', 'Video Games',
    'Furniture', 'Tools', 'Baby Products', 'Party Supplies', 'Crafts'
]

# Time periods (months)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

print(f"📊 Dataset configuration:")
print(f"   - Regions: {NUM_REGIONS}")
print(f"   - Products: {NUM_PRODUCTS}")
print(f"   - Time Periods: {NUM_TIME_PERIODS}")
print(f"   - Total cells: {NUM_REGIONS * NUM_PRODUCTS * NUM_TIME_PERIODS:,}")
print()

# Create the dataset
data_records = []

for region_idx, region in enumerate(regions):
    for product_idx, product in enumerate(products):
        row = {'Region': region, 'Product': product}
        
        # Generate sales data for each month
        # Create realistic patterns:
        # - Some products/regions have high sales
        # - Some have very low sales (will trigger protection rules)
        # - Add some dominant values (one region dominates)
        
        for month_idx, month in enumerate(months):
            # Base value influenced by region and product popularity
            base_value = 100 + (region_idx * 50) + (product_idx * 30)
            
            # Add seasonality
            seasonal_factor = 1 + 0.3 * np.sin(month_idx * np.pi / 6)
            
            # Add random variation
            random_factor = np.random.uniform(0.5, 1.5)
            
            # Calculate sales
            sales = int(base_value * seasonal_factor * random_factor)
            
            # Intentionally create some small values (< 3) to test frequency rule
            if np.random.random() < 0.05:  # 5% chance of very small value
                sales = np.random.randint(0, 3)
            
            # Create some dominant values (one region much larger)
            if region_idx < 5 and product_idx < 5:  # Top regions/products
                sales = int(sales * np.random.uniform(2, 5))
            
            row[month] = sales
        
        data_records.append(row)

# Create DataFrame
df = pd.DataFrame(data_records)

print("✅ Dataset generated successfully!")
print()
print(f"📈 Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
print()

# Calculate statistics
numeric_columns = df.select_dtypes(include=[np.number]).columns
total_cells = len(numeric_columns) * len(df)
small_values = (df[numeric_columns] < 3).sum().sum()
zero_values = (df[numeric_columns] == 0).sum().sum()

print("📊 Data statistics:")
print(f"   - Total numeric cells: {total_cells:,}")
print(f"   - Cells with value < 3: {small_values:,} ({small_values/total_cells*100:.1f}%)")
print(f"   - Zero values: {zero_values:,}")
print(f"   - Min value: {df[numeric_columns].min().min()}")
print(f"   - Max value: {df[numeric_columns].max().max()}")
print(f"   - Mean value: {df[numeric_columns].mean().mean():.0f}")
print()

# Display preview
print("👀 Data preview (first 5 rows, first 6 columns):")
print(df.iloc[:5, :6])
print()

# Save as CSV
csv_filename = 'large_test_data.csv'
df.to_csv(csv_filename, index=False)
print(f"✅ Saved as: {csv_filename}")
print(f"   File size: {pd.io.common.get_filepath_or_buffer(csv_filename)[0]}")

# Save as Excel
excel_filename = 'large_test_data.xlsx'
df.to_excel(excel_filename, index=False, engine='openpyxl')
print(f"✅ Saved as: {excel_filename}")
print()

print("🎯 Files ready to use with SPAAS!")
print()
print("Expected behavior when processing:")
print(f"   - {small_values} cells should be flagged for primary suppression (frequency rule)")
print("   - Additional cells will be added as secondary suppressions")
print("   - Dominance rule may trigger for top regions/products")
print()
print("📤 Upload either file to SPAAS and process!")
