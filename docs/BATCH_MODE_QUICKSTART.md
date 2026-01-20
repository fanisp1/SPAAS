# Batch Mode Implementation - Quick Start Guide

**Goal**: Add full τ-ARGUS batch mode compatibility to SPAAS Hypercube  
**Timeline**: 6 weeks  
**Status**: 🚀 Ready to Start

---

## What You Have Now ✅

1. **Working Hypercube Implementation** (`backend/app/hypercube.py`)
   - Basic primary suppression (frequency, dominance, p-percent rules)
   - Graph-based secondary suppression
   - OR-Tools optimization
   - Web API endpoints working

2. **Format Handler Foundation** (`backend/app/tauargus_formats.py` - JUST CREATED!)
   - .asc microdata parser
   - .rda metadata parser
   - .tab tabulated parser
   - .hrc hierarchy parser
   - .hst apriori parser
   - .sbs export format

3. **Documentation**
   - Complete technical approach (COMPLETE_SPAAS_APPROACH.md)
   - τ-ARGUS integration analysis (TAUARGUS_INTEGRATION_ANALYSIS.md)
   - Implementation plan (in Plans section)

---

## What's Missing (To Implement)

### Week 1-2: Batch Processing Infrastructure

#### 1. Batch File Parser (`backend/app/batch_parser.py`)
**Purpose**: Parse .arb batch command files

**File Structure**:
```python
from pathlib import Path
from typing import Dict, List
from enum import Enum

class BatchCommand(Enum):
    OPENMICRODATA = "OPENMICRODATA"
    OPENMETADATA = "OPENMETADATA"
    OPENTABLEDATA = "OPENTABLEDATA"
    SPECIFYTABLE = "SPECIFYTABLE"
    SAFETYRULE = "SAFETYRULE"
    SUPPRESS = "SUPPRESS"
    WRITETABLE = "WRITETABLE"
    COMMENT = "COMMENT"
    SILENT = "SILENT"

class BatchParser:
    def parse_arb(self, arb_file: Path) -> List[Dict]:
        """
        Parse .arb batch file into command sequence
        
        Returns:
            List of commands like:
            [
                {'command': 'OPENMICRODATA', 'file': 'data.asc'},
                {'command': 'OPENMETADATA', 'file': 'data.rda'},
                {'command': 'SAFETYRULE', 'rules': {...}},
                ...
            ]
        """
        pass
```

**Key Features**:
- Line-by-line tokenization
- Handle comments (`//` or `\\`)
- State machine validation (commands in correct order)
- Path resolution (relative to batch file or data directory)

#### 2. Batch API Endpoint (`backend/app/batch_api.py`)
**Purpose**: REST API for batch job processing

```python
from fastapi import APIRouter, UploadFile, File
from typing import List

router = APIRouter(prefix="/batch", tags=["Batch Processing"])

@router.post("/process")
async def process_batch_job(
    arb_file: UploadFile = File(...),
    data_files: List[UploadFile] = File(...)
):
    """
    1. Save uploaded files to temp directory
    2. Parse .arb file
    3. Execute commands sequentially
    4. Return results
    """
    pass
```

#### 3. Job Executor (`backend/app/batch_executor.py`)
**Purpose**: Execute batch commands

```python
class BatchExecutor:
    def __init__(self):
        self.data = None
        self.metadata = None
        self.protection_rules = None
        self.results = None
    
    def execute_command(self, command: Dict):
        if command['command'] == 'OPENMICRODATA':
            self.data = TauArgusFormatHandler.parse_microdata_asc(...)
        elif command['command'] == 'SAFETYRULE':
            self.protection_rules = self.parse_rules(command['rules'])
        elif command['command'] == 'SUPPRESS':
            engine = HypercubeEngine(self.protection_rules)
            self.results = engine.run(self.data)
        # ... etc
```

### Week 3: Hypercube Engine Enhancements

#### 4. Add Missing Variables to Hypercube
**File**: `backend/app/hypercube.py` (MODIFY)

**Changes**:
```python
class HypercubeEngine:
    def __init__(self,
                 protection_rules: ProtectionRules,
                 shadow_variable: Optional[str] = None,  # NEW
                 holding_variable: Optional[str] = None, # NEW
                 weight_variable: Optional[str] = None,  # NEW
                 cost_function: str = "unity"):          # NEW
        self.shadow_variable = shadow_variable
        self.holding_variable = holding_variable
        self.weight_variable = weight_variable
        self.cost_function = cost_function
        # ... rest of init
    
    def detect_singletons(self, data: pd.DataFrame) -> Set[str]:
        """Use holding variable to find singleton cells"""
        if not self.holding_variable:
            return set()
        
        singletons = set()
        for i in range(len(data)):
            for j in range(len(data.columns)):
                # Count unique holding values in cell
                # If count == 1, it's a singleton
                pass
        return singletons
```

### Week 4: Hierarchical Support

#### 5. Hierarchy Management (`backend/app/hierarchy.py`)
**Purpose**: Handle hierarchical tables

```python
@dataclass
class HierarchyNode:
    code: str
    level: int
    parent: Optional['HierarchyNode']
    children: List['HierarchyNode']
    is_total: bool

class HierarchyTree:
    def __init__(self, hrc_dict: Dict):
        self.nodes = self.build_tree(hrc_dict)
    
    def get_ancestors(self, code: str) -> List[str]:
        """Get all parent codes"""
        pass
    
    def get_descendants(self, code: str) -> List[str]:
        """Get all child codes"""
        pass
```

---

## Step-by-Step Implementation Guide

### Start Today: Test Format Handlers

**Step 1**: Create a test .rda file
```bash
# File: C:\SPAAS\test_data\test.rda
cat > C:\SPAAS\test_data\test.rda << 'EOF'
<SEPARATOR> ","
<VARIABLE>
Name=IndustryCode
StartingPosition=1
FieldLength=4
Type=EXPLANATORY
</VARIABLE>
<VARIABLE>
Name=Region
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
EOF
```

**Step 2**: Create test .asc file
```bash
# File: C:\SPAAS\test_data\test.asc
cat > C:\SPAAS\test_data\test.asc << 'EOF'
A001 01 100.5
A001 02 200.3
B002 01 50.2
EOF
```

**Step 3**: Test the parser
```python
# backend/app/test_formats.py
from tauargus_formats import TauArgusFormatHandler
from pathlib import Path

# Test RDA parser
metadata = TauArgusFormatHandler.parse_metadata_rda(
    Path("C:/SPAAS/test_data/test.rda")
)
print(f"Found {len(metadata.variables)} variables")
for var in metadata.variables:
    print(f"  - {var.name}: pos {var.start}, len {var.length}, type {var.type}")

# Test ASC parser
df = TauArgusFormatHandler.parse_microdata_asc(
    Path("C:/SPAAS/test_data/test.asc"),
    Path("C:/SPAAS/test_data/test.rda")
)
print(f"\nLoaded data:\n{df}")
```

**Step 4**: Run the test
```bash
cd C:\SPAAS\backend
python -m app.test_formats
```

---

## Next Week: Batch Parser

### Day 1-2: Implement BatchParser

**Create**: `backend/app/batch_parser.py`

**Test with simple .arb**:
```xml
<OPENMICRODATA> "test.asc"
<OPENMETADATA> "test.rda"
<SPECIFYTABLE> "Value" | "IndustryCode" "Region"
<SAFETYRULE>
Frequency(3,10)
</SAFETYRULE>
<SUPPRESS>
HYPERCUBE
</SUPPRESS>
<WRITETABLE>
Output="result.sbs"
Format=SBS
</WRITETABLE>
```

### Day 3-4: Batch API

**Create**: `backend/app/batch_api.py`

**Add to main.py**:
```python
from .batch_api import router as batch_router

app.include_router(batch_router)
```

### Day 5: Integration Testing

**Test end-to-end**:
1. Upload .arb + data files via API
2. Execute batch job
3. Download .sbs result
4. Compare with τ-ARGUS output

---

## Testing Strategy

### Test Data Location
Download τ-ARGUS test data:
```
C:\Program Files\TauArgus\data\
  - tau_testW.asc
  - tau_testW.rda
  - IndustryCode.hrc
  - Region.hrc
```

### Reference Test
```python
# backend/app/test_reference.py
from tauargus_formats import TauArgusFormatHandler
from hypercube import HypercubeEngine, ProtectionRules

# Load τ-ARGUS test data
df = TauArgusFormatHandler.parse_microdata_asc(
    Path("C:/Program Files/TauArgus/data/tau_testW.asc"),
    Path("C:/Program Files/TauArgus/data/tau_testW.rda")
)

# Apply same rules as τ-ARGUS
rules = ProtectionRules(
    min_frequency=3,
    dominance_n=1,
    dominance_k=85.0,
    p_percent=10.0
)

engine = HypercubeEngine(rules)
results, stats = engine.run(df)

print(f"Primary suppressions: {stats['primary_count']}")
print(f"Secondary suppressions: {stats['secondary_count']}")

# Compare with τ-ARGUS expected:
# - Primary unsafe (dominance): 570
# - Primary unsafe (frequency): 483
# - Secondary: 38,208
```

---

## Common Issues & Solutions

### Issue 1: Fixed-Width Parsing Errors
**Problem**: Columns don't align  
**Solution**: Check .rda starting positions (1-indexed vs 0-indexed)

### Issue 2: Hierarchy Not Loading
**Problem**: .hrc file format incorrect  
**Solution**: Verify indentation (use spaces, not tabs)

### Issue 3: Batch Commands Out of Order
**Problem**: State machine rejects valid sequence  
**Solution**: Check τ-ARGUS documentation for allowed transitions

---

## Progress Tracking

Use the implementation plan checklist:
- [ ] Week 1-2: Format Compatibility
- [ ] Week 3: Hypercube Enhancements  
- [ ] Week 4: Hierarchical Support
- [ ] Week 5: Testing
- [ ] Week 6: Documentation

**Mark items complete as you go!**

---

## Resources

### Documentation
1. **TAUARGUS_INTEGRATION_ANALYSIS.md** - Complete τ-ARGUS analysis
2. **COMPLETE_SPAAS_APPROACH.md** - Full technical approach
3. **Implementation Plan** - Detailed 6-week roadmap (in Plans)

### τ-ARGUS Source Code
- Location: `C:\Users\Nick\Documents\tauargus-master`
- Key file: `src/tauargus/model/batch.java` (batch processor)

### Test Data
- Location: `C:\Program Files\TauArgus\data\`
- Files: `tau_testW.asc`, `tau_testW.rda`

---

## Quick Commands

### Create test directory
```powershell
mkdir C:\SPAAS\test_data
```

### Run format tests
```powershell
cd C:\SPAAS\backend
python -m pytest app/test_formats.py -v
```

### Start backend server
```powershell
cd C:\SPAAS\backend
uvicorn app.main:app --reload --port 8000
```

### Test batch API
```powershell
curl -X POST "http://localhost:8000/batch/process" `
  -F "arb_file=@test.arb" `
  -F "data_files=@test.asc" `
  -F "data_files=@test.rda"
```

---

## Success Criteria

After 6 weeks, you should have:

✅ **Functional**:
- [ ] Parse all τ-ARGUS file formats (.asc, .rda, .tab, .hrc, .hst)
- [ ] Execute .arb batch files
- [ ] Run hypercube with all features (shadow, holding, weight variables)
- [ ] Export .sbs format matching τ-ARGUS
- [ ] Handle hierarchical tables

✅ **Performance**:
- [ ] 10-50x faster than τ-ARGUS (Python vs C++/Fortran)
- [ ] Process tau_testW.asc in <1 second

✅ **Quality**:
- [ ] Match τ-ARGUS suppression results exactly
- [ ] Pass all reference tests
- [ ] >90% code coverage

---

## Get Help

**Stuck?** Review these documents:
1. `TAUARGUS_INTEGRATION_ANALYSIS.md` - How τ-ARGUS works
2. Implementation Plan (in Plans) - Detailed tasks
3. τ-ARGUS source: `tauargus-master/src/tauargus/model/batch.java`

**Next Step**: Start testing the format handlers you just created! 🚀
