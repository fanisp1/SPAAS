# SPAAS Test Data

This directory contains all test datasets for SPAAS development and validation.

## 📂 Directory Structure

```
test_data/
├── simple/          # Simple test cases for unit testing
├── batch/           # Batch mode test files (.arb + data)
├── reference/       # τ-ARGUS reference datasets
└── README.md        # This file
```

---

## 📁 `/simple/` - Simple Test Cases

**Purpose**: Small, hand-crafted datasets for unit testing individual components

**Use Cases**:
- Testing format parsers (.asc, .rda, .tab parsing)
- Validating protection rules
- Quick smoke tests during development

**Example Files**:
```
simple/
├── basic_test.asc         # Simple 3x3 table
├── basic_test.rda         # Metadata for basic test
├── hierarchy_test.hrc     # Simple 2-level hierarchy
├── apriori_test.hst       # Manual protection examples
└── tabulated_test.tab     # Pre-aggregated table
```

**Create Test Files**:
```powershell
# See BATCH_MODE_QUICKSTART.md for instructions
cd C:\SPAAS\test_data\simple
# Create test files following examples in docs
```

---

## 📁 `/batch/` - Batch Mode Test Files

**Purpose**: Complete batch job test scenarios with .arb files

**Use Cases**:
- End-to-end batch processing tests
- τ-ARGUS compatibility validation
- Workflow testing

**Example Files**:
```
batch/
├── test_hypercube.arb     # Batch file for hypercube test
├── test_data.asc          # Microdata for batch
├── test_data.rda          # Metadata
├── industry.hrc           # Hierarchy
├── expected_output.sbs    # Expected result
└── README_batch.md        # Batch file format docs
```

**Batch File Format** (.arb):
```xml
<OPENMICRODATA> "test_data.asc"
<OPENMETADATA> "test_data.rda"
<SPECIFYTABLE> "Value" | "Industry" "Region"
<SAFETYRULE>
Frequency(3,10)
Dominance(1,85)
</SAFETYRULE>
<SUPPRESS>
HYPERCUBE
</SUPPRESS>
<WRITETABLE>
Output="result.sbs"
Format=SBS
</WRITETABLE>
```

---

## 📁 `/reference/` - τ-ARGUS Reference Data

**Purpose**: Official τ-ARGUS test datasets for validation

**Source**: Copy from τ-ARGUS installation:
```powershell
# If τ-ARGUS is installed:
copy "C:\Program Files\TauArgus\data\tau_testW.*" C:\SPAAS\test_data\reference\
copy "C:\Program Files\TauArgus\data\*.hrc" C:\SPAAS\test_data\reference\
```

**Expected Files**:
```
reference/
├── tau_testW.asc          # τ-ARGUS standard test data
├── tau_testW.rda          # Metadata
├── IndustryCode.hrc       # Industry hierarchy (NACE)
├── Region.hrc             # Region hierarchy
└── REFERENCE_RESULTS.md   # Expected suppression counts
```

**Reference Results** (from τ-ARGUS):
```
Table: IndustryCode (711 codes) × Region (18 codes)
Rules: Dominance(1,85) + Frequency(3,10)
Method: Hypercube

Expected:
- Primary unsafe (dominance): 570
- Primary unsafe (frequency): 483
- Secondary suppressed: 38,208
- Total cells: 12,798
- Processing time: ~8 seconds (τ-ARGUS)

SPAAS Target:
- Same suppression pattern
- Processing time: <1 second (10x faster)
```

---

## 🧪 Testing Workflow

### 1. Unit Tests (Simple Data)
```powershell
cd C:\SPAAS\backend
python -m pytest tests/test_formats.py -v
```

### 2. Integration Tests (Batch Data)
```powershell
cd C:\SPAAS\backend
python -m pytest tests/test_batch.py -v
```

### 3. Validation Tests (Reference Data)
```powershell
cd C:\SPAAS\backend
python -m pytest tests/test_reference.py -v
```

---

## 📝 Creating New Test Data

### Simple Test Case Template

**File**: `simple/my_test.rda`
```xml
<SEPARATOR> ","
<VARIABLE>
Name=Dimension1
StartingPosition=1
FieldLength=4
Type=EXPLANATORY
</VARIABLE>
<VARIABLE>
Name=Dimension2
StartingPosition=6
FieldLength=2
Type=EXPLANATORY
</VARIABLE>
<VARIABLE>
Name=Value
StartingPosition=9
FieldLength=10
Decimals=1
Type=RESPONSE
</VARIABLE>
```

**File**: `simple/my_test.asc`
```
A001 01    100.5
A001 02    200.3
B002 01     50.2
```

### Batch Test Case Template

1. Create data files (`.asc`, `.rda`)
2. Create batch file (`.arb`)
3. Run manually with τ-ARGUS to get expected output
4. Store expected output for comparison

---

## 🔍 Data Validation

### Check File Format
```python
from pathlib import Path
from app.tauargus_formats import TauArgusFormatHandler

# Validate .rda metadata
metadata = TauArgusFormatHandler.parse_metadata_rda(
    Path("test_data/simple/test.rda")
)
print(f"Variables: {len(metadata.variables)}")

# Validate .asc data
df = TauArgusFormatHandler.parse_microdata_asc(
    Path("test_data/simple/test.asc"),
    Path("test_data/simple/test.rda")
)
print(f"Records: {len(df)}")
print(df.head())
```

---

## 📚 Additional Resources

- **File Format Specs**: `docs/TAUARGUS_INTEGRATION_ANALYSIS.md`
- **Batch Mode Guide**: `docs/BATCH_MODE_QUICKSTART.md`
- **τ-ARGUS Manual**: `C:\Program Files\TauArgus\help\TauManualV4.1.pdf`

---

## ⚠️ Important Notes

1. **File Encoding**: All text files should be UTF-8
2. **Line Endings**: Windows (CRLF) is fine
3. **Fixed-Width Format**: Be careful with column positions in .asc files
4. **Paths in .arb**: Can be relative to batch file or absolute

---

## 🎯 Next Steps

1. **Copy τ-ARGUS reference data** (if available)
2. **Create simple test cases** for format validation
3. **Build batch test suite** for end-to-end testing
4. **Run validation tests** against τ-ARGUS results
