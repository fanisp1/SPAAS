# 🚀 SPAAS Quick Start Guide

## Start the Application

### Option 1: Manual Start (Recommended)

**Step 1: Start Backend** (Terminal 1)
```powershell
cd C:\SPAAS\backend
python -m uvicorn app.main:app --reload
```

Wait for message: "Application startup complete."

**Step 2: Start Frontend** (Terminal 2 - New Window)
```powershell
cd C:\SPAAS\frontend
npm run dev
```

Wait for message: "Ready in X seconds"

**Step 3: Open Browser**

Navigate to: http://localhost:3000

## Using the Application

### 1. Upload Your Data File
- Click the upload box or drag-and-drop
- Supported formats: CSV (.csv) or Excel (.xlsx)
- Example: Use one of the test CSV files generated earlier

### 2. Configure Protection Rules

**Minimum Frequency** (default: 3)
- Cells below this value will be suppressed
- Higher = more suppressions

**Dominance N** (default: 1)
- Number of top contributors to check
- 1 = single dominance, 2 = top 2, etc.

**Dominance K%** (default: 80%)
- Percentage threshold
- Lower = stricter protection

**P-Percent %** (default: 10%)
- Estimation threshold
- Lower = stricter protection

### 3. Run Suppression
- Click "🚀 Run Hypercube Suppression"
- Processing typically takes 1-10 seconds

### 4. View Results
- Statistics cards show suppressions breakdown
- Table shows suppressed data (X = suppressed cells)
- Download button to get CSV file

## Test with Sample Data

Use any of the generated CSV files from your tests:
- `suppressed_output.csv`
- `suppressed_frequency_rule.csv`
- `suppressed_dominance_rule.csv`

Or create a simple test CSV:

```csv
Region,Product_A,Product_B,Product_C
North,45,120,67
South,2,8,1
East,12,23,15
West,78,145,92
```

## API Endpoints

With backend running, you can also use the API directly:

**API Documentation**: http://localhost:8000/docs

**Upload & Process**:
```bash
curl -X POST "http://localhost:8000/suppress/hypercube/" \
  -F "file=@data.csv" \
  -F "min_frequency=3"
```

**Download Suppressed Data**:
```bash
curl -X POST "http://localhost:8000/suppress/hypercube/download/" \
  -F "file=@data.csv" \
  -F "min_frequency=3" \
  -o suppressed.csv
```

## Troubleshooting

### Backend Won't Start
```powershell
# Check Python environment
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Won't Start
```powershell
# Reinstall dependencies
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
npm run dev
```

### CORS Error
- Ensure backend is running BEFORE frontend
- Check backend console for CORS middleware loaded
- Frontend must be on http://localhost:3000

### File Upload Fails
- Check file format (CSV or XLSX only)
- Ensure file has numeric data
- Check backend console for detailed errors

## Stopping the Application

- **Backend**: Press `Ctrl+C` in backend terminal
- **Frontend**: Press `Ctrl+C` in frontend terminal

## Next Steps

Once you're familiar with the hypercube method:

1. Try different protection rule combinations
2. Test with your own data files
3. Compare results with different parameters
4. Export and share suppressed datasets

## Resources

- Main README: `C:\SPAAS\README.md`
- Frontend README: `C:\SPAAS\frontend\README_FRONTEND.md`
- Progress Report: `C:\SPAAS\PROGRESS_REPORT.md`
- Next Steps: `C:\SPAAS\NEXT_STEPS.md`

---

**Need help?** Check the API documentation at http://localhost:8000/docs when backend is running.
