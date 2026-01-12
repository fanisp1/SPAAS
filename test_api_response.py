import requests
import json

url = "http://localhost:8000/suppress/hypercube/"

with open('C:/SPAAS/realistic_test_data.xlsx', 'rb') as f:
    files = {'file': ('realistic_test_data.xlsx', f)}
    data = {
        'min_frequency': '10',
        'dominance_n': '1',
        'dominance_k': '80.0',
        'p_percent': '10.0'
    }
    
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    print(f"Status: {result['status']}")
    print(f"\nStatistics keys: {result['statistics'].keys()}")
    print(f"Primary suppressions: {result['statistics']['primary_suppressions']}")
    print(f"Secondary suppressions: {result['statistics']['secondary_suppressions']}")
    
    if 'primary_cells' in result['statistics']:
        print(f"\nFirst 5 primary cells: {result['statistics']['primary_cells'][:5]}")
    else:
        print("\nWARNING: primary_cells not in statistics!")
    
    if 'secondary_cells' in result['statistics']:
        print(f"First 5 secondary cells: {result['statistics']['secondary_cells'][:5]}")
    else:
        print("WARNING: secondary_cells not in statistics!")
    
    print(f"\nColumn names: {result['column_names']}")
    print(f"Number of data rows: {len(result['suppressed_data'])}")
