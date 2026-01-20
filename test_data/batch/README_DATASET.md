# Batch Test Dataset

## Overview

This is a **real τ-ARGUS test dataset** copied from your `data_tau_Argus_Table_input` folder. It contains a complete working example with all necessary files for batch mode testing.

## Files Included ✅

| File | Type | Size | Description |
|------|------|------|-------------|
| `pp.tab` | Data | 10.5 KB | Tabulated data table (162 cells) |
| `pp.rda` | Metadata | 722 B | Variable definitions and metadata |
| `region2.hrc` | Hierarchy | 75 B | Regional hierarchy (4 regions, 12 provinces) |
| `REGION.CDL` | Code List | 211 B | Province and region name mappings |
| `spaas_test.arb` | Batch | 395 B | Batch commands using GH suppression |
| `TestTable.arb` | Batch | 227 B | Simple batch file for testing |

## Dataset Description

### Table Structure
- **Dimensions**: Size (categorical) × Region (hierarchical)
- **Total Cells**: 162
- **Hierarchy Levels**: 2 (regions → provinces)

### Regions & Provinces

**Nr (North)**
- 1 = Groningen
- 2 = Friesland  
- 3 = Drenthe

**Os (East)**
- 4 = Overijssel
- 5 = Flevoland
- 6 = Gelderland
- 7 = Utrecht

**Ws (West)**
- 8 = Noord-Holland
- 9 = Zuid-Holland
- 10 = Zeeland

**Zd (South)**
- 11 = Noord-Brabant
- 12 = Limburg

### Variables (from pp.rda)

| Variable | Type | Description |
|----------|------|-------------|
| Size | Categorical | Size classification |
| Region | Hierarchical | Regional code (with hierarchy) |
| Var2 | Response (Numeric) | Main value, 2 decimals |
| FreqVar | Frequency | Record count |
| Var2_Shadow | Shadow | Top contributor for dominance |
| Var2_Cost | Cost | Suppression cost variable |
| Top1 | MaxScore | Largest contributor |
| Top2 | MaxScore | Second largest contributor |
| StatusVar | Status | Cell status (S/U/P) |
| LowerProtLevel | Lower Protection | Minimum protection level |
| UpperProtLevel | Upper Protection | Maximum protection level |

### Status Codes

- **S** = Safe (no protection needed)
- **U** = Unsafe (primary suppression required)
- **E** = Empty (no data)

### Sample Data (pp.tab)

```
"Total";"Total";16847646,84;42723;16847646,84;16847646,84;175677,00;141482,00;S;0,01;0,01
"Total";"Nr";4373664,00;11395;4373664,00;4373664,00;43587,00;43293,00;S;0,01;0,01
" 2";"Nr";5,00;6;5,00;5,00;5,00;0,00;U;0,75;0,75
```

**Column order**:
1. Size (quoted string)
2. Region (quoted string)
3. Var2 value
4. Frequency
5. Var2 (repeated)
6. Var2 (repeated)
7. Var2_Shadow
8. Var2_Cost
9. StatusVar (S/U/E)
10. LowerProtLevel
11. UpperProtLevel

## Batch Files

### TestTable.arb (Simple)
```xml
<OPENTABLEDATA>  "pp.tab"
<OPENMETADATA>   "pp.rda"
<SPECIFYTABLE>   "Size""Region"|"Var2"|"Var2_Shadow"|"Var2"
<READTABLE> 1T
<GOINTERACTIVE>
```

**What it does**: Opens the table in interactive mode (τ-ARGUS GUI)

### spaas_test.arb (Suppression)
```xml
<OPENTABLEDATA>  "U:\\Confidentiality\\3. Tools\\Argus\\data_tau_Argus_Table_input\\pp.tab"
<OPENMETADATA>   "U:\\Confidentiality\\3. Tools\\Argus\\data_tau_Argus_Table_input\\pp.rda"
<SPECIFYTABLE>   "Size""Region"|"Var2"|"Var2_Shadow"|"Var2"
<READTABLE> 2
<SUPPRESS>       GH(1,100,0,1)
<GOINTERACTIVE>
```

**What it does**: 
- Opens table data
- Applies GH (Ghmiter/Hypercube) suppression with parameters (1,100,0,1)
- Opens in interactive mode for review

**Note**: Paths in spaas_test.arb are absolute. You'll need to update them to use relative paths or copy to match your directory structure.

## Using This Dataset

### Test Format Parsers

```python
from backend.app.tauargus_formats import TauArgusFormatHandler

# Parse metadata
meta = TauArgusFormatHandler.parse_rda_file("test_data/batch/pp.rda")
print(f"Variables: {[v.name for v in meta.variables]}")

# Parse tabulated data
df = TauArgusFormatHandler.parse_tab_file("test_data/batch/pp.tab")
print(f"Cells: {len(df)}")
print(f"Unsafe cells: {(df['Status'] == 'U').sum()}")

# Parse hierarchy
hierarchy = TauArgusFormatHandler.parse_hrc_file("test_data/batch/region2.hrc")
print(f"Regions: {len([n for n in hierarchy if n.level == 0])}")
print(f"Provinces: {len([n for n in hierarchy if n.level == 1])}")
```

### Expected Output

When you parse this data successfully:
- **162 cells** total
- **Multiple unsafe cells** marked with status 'U'
- **4 top-level regions** (Nr, Os, Ws, Zd)
- **12 provinces** at leaf level
- **11 variables** defined in metadata

## Next Steps

1. **Test parsers** with this dataset
2. **Update paths** in spaas_test.arb to relative paths
3. **Implement batch executor** to process .arb files
4. **Run suppression** and verify results
5. **Export to .sbs** format

## Notes

- This is production-quality test data from a real project
- The data appears to be related to Dutch provinces/regions
- File paths in .arb files use backslashes (Windows)
- Decimal separator is comma (European format)
- Column separator in .tab is semicolon
- Strings are quoted in .tab files

---

✅ **Status**: Ready to use for testing format handlers and batch processing!
