"""
Create a test Excel file for SPAAS
"""

import pandas as pd

# Create sample data
data = {
    'Region': ['North', 'South', 'East', 'West', 'Central'],
    'Sales_Q1': [45, 2, 12, 78, 34],
    'Sales_Q2': [120, 1, 23, 145, 89],
    'Sales_Q3': [67, 8, 15, 92, 56],
    'Sales_Q4': [89, 5, 19, 110, 67]
}

df = pd.DataFrame(data)

# Save as Excel
output_file = 'test_data.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"✅ Created {output_file}")
print("\nData preview:")
print(df)
print("\nYou can now upload this file to SPAAS!")
