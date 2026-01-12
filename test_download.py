import requests

# Test downloading Excel file from backend
url = "http://localhost:8000/suppress/hypercube/download/"

with open('C:/SPAAS/realistic_test_data.xlsx', 'rb') as f:
    files = {'file': ('realistic_test_data.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    data = {
        'min_frequency': '10',
        'dominance_n': '1',
        'dominance_k': '80.0',
        'p_percent': '10.0',
        'output_format': 'excel'  # EXPLICITLY SET TO EXCEL
    }
    
    print(f"Sending request to {url}")
    print(f"Parameters: {data}")
    
    response = requests.post(url, files=files, data=data)
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response size: {len(response.content)} bytes")
    
    # Check first bytes
    first_bytes = response.content[:50]
    print(f"\nFirst 50 bytes as text: {first_bytes.decode('latin-1', errors='replace')}")
    
    # Check if it's Excel (should start with PK for ZIP format)
    if response.content[:2] == b'PK':
        print("\n✓ File is a valid Excel/ZIP file!")
        with open('C:/SPAAS/test_api_download.xlsx', 'wb') as out:
            out.write(response.content)
        print("Saved to test_api_download.xlsx")
    else:
        print("\n✗ File is NOT Excel - likely CSV")
        print("Saving as .txt to inspect...")
        with open('C:/SPAAS/test_api_download.txt', 'wb') as out:
            out.write(response.content)
