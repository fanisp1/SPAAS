import sys
sys.path.insert(0, 'C:/SPAAS/backend')
from app.hypercube import hypercube_suppress, ProtectionRules
import pandas as pd

df = pd.read_excel('C:/SPAAS/realistic_test_data.xlsx')
print(f'DataFrame shape: {df.shape}')
print(f'Columns: {list(df.columns)}')
print(f'Column indices: {list(range(len(df.columns)))}')
print()

protection_rules = ProtectionRules(min_frequency=10)
suppressed_data, statistics = hypercube_suppress(df, protection_rules)

print(f'Total suppressions: {len(statistics["suppressed_cells"])}')
print(f'First 10 suppressed cells:')
for cell in statistics["suppressed_cells"][:10]:
    row, col = cell['row'], cell['col']
    col_name = df.columns[col]
    value = df.iloc[row, col]
    print(f"  Row {row}, Col {col} ({col_name}): {value}")
