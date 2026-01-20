# Batch Mode Setup & Testing Guide

## ✅ What's Been Created

### Backend Components
1. **`batch_parser.py`** (351 lines) - Complete batch file parser
   - Parses .arb batch command files
   - Extracts commands, safety rules, file paths
   - Resolves relative/absolute paths

2. **`main.py`** - Two new API endpoints:
   - `POST /batch/parse/` - Parse .arb file and return structure
   - `POST /batch/execute/` - Execute batch file and run suppression

3. **`tauargus_formats.py`** (515 lines) - Format handlers (already created)
   - Parse `.tab`, `.rda`, `.hrc`, `.hst` files

### Test Data ✅
Copied real τ-ARGUS test data to `test_data/batch/`:
- `pp.tab` - 162 cells of tabulated data
- `pp.rda` - Metadata with 11 variables
- `region2.hrc` - Hierarchy (4 regions, 12 provinces)
- `REGION.CDL` - Code list
- `TestTable.arb` - Simple batch file
- `spaas_test.arb` - Batch with suppression

### Test Script
- `test_batch_parser.py` - Comprehensive test suite

---

## 🚀 Quick Start

### 1. Install Dependencies

First, make sure you have all required Python packages:

```powershell
cd C:\SPAAS\backend
pip install fastapi uvicorn pandas openpyxl python-multipart
```

### 2. Test Batch Parser (Optional)

Test the parsers directly without the API:

```powershell
cd C:\SPAAS
python test_batch_parser.py
```

**Expected output:**
- ✅ Batch file parsed (TestTable.arb)
- ✅ .tab file loaded (162 cells)
- ✅ .rda metadata loaded (11 variables)
- ✅ .hrc hierarchy loaded (4 regions, 12 provinces)

### 3. Start Backend Server

```powershell
cd C:\SPAAS\backend
uvicorn app.main:app --reload
```

Server runs at: **http://localhost:8000**

### 4. Test API Endpoints

#### A. Test Batch Parser Endpoint

Using PowerShell (from any directory):

```powershell
# Parse a batch file (see what's in it)
$batchFile = "C:\SPAAS\test_data\batch\TestTable.arb"
curl.exe -X POST http://localhost:8000/batch/parse/ `
  -F "batch_file=@$batchFile"
```

**Expected Response:**
```json
{
  "status": "success",
  "filename": "TestTable.arb",
  "commands": [...],
  "summary": {
    "table_data_file": "pp.tab",
    "metadata_file": "pp.rda",
    "safety_rules": []
  }
}
```

#### B. Test Execute Endpoint (Coming Soon)

The execute endpoint requires the data files to be accessible. Since the batch file references absolute paths, we need to either:
- Update the paths in the .arb file, OR
- Upload all files together

---

## 📋 Testing with Frontend (Next Steps)

### Frontend Changes Needed

Create a new page: `frontend/app/batch/page.tsx`

```typescript
'use client';

import { useState } from 'react';

export default function BatchMode() {
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleParse = async () => {
    if (!batchFile) return;

    const formData = new FormData();
    formData.append('batch_file', batchFile);

    const response = await fetch('http://localhost:8000/batch/parse/', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Batch Mode</h1>
      
      <div className="mb-4">
        <label className="block mb-2">Upload Batch File (.arb)</label>
        <input
          type="file"
          accept=".arb"
          onChange={(e) => setBatchFile(e.files?.[0] || null)}
          className="border p-2"
        />
      </div>

      <button
        onClick={handleParse}
        disabled={!batchFile}
        className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-300"
      >
        Parse Batch File
      </button>

      {result && (
        <div className="mt-6 p-4 bg-gray-100 rounded">
          <h2 className="font-bold mb-2">Results:</h2>
          <pre className="text-sm overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
```

---

## 🧪 Testing Checklist

### Phase 1: Backend Testing
- [ ] Install dependencies (`pip install ...`)
- [ ] Run test script (`python test_batch_parser.py`)
- [ ] Start backend server (`uvicorn app.main:app --reload`)
- [ ] Test `/batch/parse/` endpoint with curl
- [ ] Verify server logs show no errors

### Phase 2: API Testing
- [ ] Upload `TestTable.arb` via API
- [ ] Check parsed output includes correct file paths
- [ ] Upload `spaas_test.arb` via API
- [ ] Verify safety rules are extracted (GH suppression)

### Phase 3: Frontend Testing (Optional)
- [ ] Create batch mode page in frontend
- [ ] Upload batch file via UI
- [ ] Display parsed batch structure
- [ ] Show file references and commands

### Phase 4: End-to-End (Future)
- [ ] Update .arb file paths to be relative
- [ ] Execute batch file with data
- [ ] Run hypercube suppression
- [ ] Download results

---

## 📂 Project Structure

```
C:\SPAAS\
├── backend/
│   └── app/
│       ├── main.py           ✅ Updated with batch endpoints
│       ├── batch_parser.py   ✅ NEW - Batch file parser
│       ├── tauargus_formats.py ✅ Format handlers
│       └── hypercube.py      ✅ Suppression engine
├── test_data/
│   └── batch/                ✅ Real test data copied
│       ├── pp.tab
│       ├── pp.rda
│       ├── region2.hrc
│       ├── REGION.CDL
│       ├── TestTable.arb
│       └── spaas_test.arb
└── test_batch_parser.py      ✅ Test script
```

---

## 🎯 Current Status

**✅ Complete:**
- Batch file parser implementation
- Format handlers (.tab, .rda, .hrc)
- API endpoints for parsing and execution
- Real test data copied and organized
- Test script created

**⏳ To Do:**
1. Install dependencies
2. Test the backend
3. (Optional) Create frontend batch mode page
4. Test complete workflow

---

## 💡 Quick Test (Right Now!)

**Simplest test** - Just parse a batch file:

```powershell
# 1. Install deps (if needed)
cd C:\SPAAS\backend
pip install fastapi uvicorn pandas

# 2. Start server
uvicorn app.main:app --reload

# 3. In another terminal, test:
curl.exe http://localhost:8000/
# Should return: {"message":"SPAAS Modernized Backend is running."}

# 4. Test batch endpoint:
$file = "C:\SPAAS\test_data\batch\TestTable.arb"
curl.exe -X POST http://localhost:8000/batch/parse/ -F "batch_file=@$file"
```

---

## 🐛 Troubleshooting

**Problem: ModuleNotFoundError**
```powershell
pip install pandas fastapi uvicorn openpyxl python-multipart
```

**Problem: File not found in execute**
- The .arb file has absolute paths (U:\...)
- You need to update paths or upload all files together
- For now, focus on `/batch/parse/` endpoint

**Problem: CORS errors in frontend**
- Backend already has CORS enabled for localhost:3000
- Make sure frontend is running on that port

---

## 📞 Need Help?

Check these files for details:
- `docs/BATCH_MODE_QUICKSTART.md` - Detailed batch mode guide
- `docs/TAUARGUS_INTEGRATION_ANALYSIS.md` - Format specifications
- `test_data/batch/README_DATASET.md` - Dataset documentation

**Next major milestone**: Execute batch file end-to-end with suppression! 🎉
