# Full Hypercube Implementation Tasks

## Overview
This document outlines the tasks for implementing complete SPAAS/GHMITER4 hypercube functionality including:
1. Hierarchical table support (subtotals, grand totals, multi-level aggregations)
2. Custom suppression cost functions
3. Parameter file support for configuration

---

## Phase 1: Foundation (Parameter Files & Cost Functions)

### Task 1.1: Design Parameter File Schema
**File**: `backend/app/schemas.py`

Create JSON schema for parameter files:
```json
{
  "protection_rules": {
    "min_frequency": 10,
    "dominance_n": 1,
    "dominance_k": 80.0,
    "p_percent": 10.0
  },
  "cost_function": {
    "type": "proportional",
    "base_cost": 1.0,
    "value_weight": 1.0
  },
  "hierarchy": {
    "dimensions": ["Region", "Product"],
    "levels": {
      "Region": ["Total", "Region", "SubRegion"],
      "Product": ["Total", "Category", "Product"]
    },
    "total_markers": ["Total", "All", "TOTAL"]
  },
  "solver": {
    "timeout_seconds": 300,
    "mip_gap": 0.01
  }
}
```

**Subtasks**:
- [ ] Add Pydantic models for parameter validation
- [ ] Support JSON and INI formats
- [ ] Add default values for all optional parameters
- [ ] Create example parameter files

### Task 1.2: Implement Parameter File Loader
**File**: `backend/app/config_loader.py` (new)

**Functions to implement**:
- `load_parameter_file(path: str) -> Dict` - Read JSON/INI
- `validate_parameters(params: Dict) -> bool` - Validate structure
- `merge_with_defaults(params: Dict) -> Dict` - Fill defaults
- `parse_to_objects(params: Dict) -> Tuple[ProtectionRules, CostConfig, HierarchyConfig]`

**Subtasks**:
- [ ] Implement JSON loader
- [ ] Implement INI loader (optional)
- [ ] Add parameter validation
- [ ] Create comprehensive error messages
- [ ] Write unit tests

### Task 1.3: Implement Cost Function Classes
**File**: `backend/app/cost.py` (new)

**Classes to implement**:
```python
class CostFunction(ABC):
    @abstractmethod
    def calculate_cost(self, cell_info: CellInfo, hierarchy_level: int) -> float:
        pass

class UniformCost(CostFunction):
    """All cells cost = 1"""
    
class ProportionalCost(CostFunction):
    """Cost = cell_value * weight"""
    
class InverseProportionalCost(CostFunction):
    """Cost = base_cost / cell_value (prefer suppressing large cells)"""
    
class HierarchyAwareCost(CostFunction):
    """Higher cost for totals/subtotals"""
    
class CustomCost(CostFunction):
    """User-defined cost per cell"""
```

**Subtasks**:
- [ ] Create abstract base class
- [ ] Implement all cost strategies
- [ ] Add cost function factory
- [ ] Write unit tests for each strategy
- [ ] Add cost function to parameter file schema

### Task 1.4: Integrate Cost Functions into Hypercube
**File**: Update `backend/app/hypercube.py`

**Changes needed**:
- [ ] Add `cost_function` parameter to `HypercubeEngine.__init__()`
- [ ] Update `build_constraint_graph()` to use cost function for cell costs
- [ ] Modify `solve_secondary_suppressions()` to use custom costs in objective
- [ ] Update `_heuristic_secondary_suppression()` to sort by custom costs
- [ ] Test with flat tables using different cost functions

### Task 1.5: Update API to Accept Parameter Files
**File**: Update `backend/app/main.py`

**New endpoint**:
```python
@app.post("/suppress/hypercube/with-params/")
async def hypercube_with_parameters(
    data_file: UploadFile = File(...),
    param_file: UploadFile = File(None),  # Optional
    # Fallback inline parameters if no param file
    min_frequency: int = Form(None),
    dominance_n: int = Form(None),
    ...
)
```

**Subtasks**:
- [ ] Create new endpoint
- [ ] Handle both parameter file and inline parameters
- [ ] Merge inline parameters with file parameters
- [ ] Maintain backward compatibility with existing endpoint
- [ ] Add comprehensive error handling

### Task 1.6: Create Example Files
**Files**: Create in `examples/` directory

**Files to create**:
- [ ] `params_basic.json` - Simple parameter file
- [ ] `params_custom_cost.json` - With custom cost function
- [ ] `params_solver_options.json` - With solver configuration
- [ ] `flat_table_example.xlsx` - Test data (no hierarchies yet)
- [ ] `README_EXAMPLES.md` - Explain each example

---

## Phase 2: Hierarchical Tables

### Task 2.1: Implement Hierarchy Parser
**File**: `backend/app/hierarchy.py` (new)

**Classes**:
```python
class HierarchyNode:
    """Represents node in hierarchy tree"""
    cell_id: str
    level: int
    parent: Optional[HierarchyNode]
    children: List[HierarchyNode]
    is_total: bool

class HierarchyParser:
    """Parse table structure and build hierarchy"""
    def identify_hierarchy_levels()
    def build_hierarchy_tree()
    def get_aggregation_constraints()
    
class HierarchyValidator:
    """Validate hierarchy consistency"""
    def validate_consistency()
    def check_totals_match_sums()
```

**Subtasks**:
- [ ] Implement HierarchyNode class
- [ ] Implement total detection (by marker or by value)
- [ ] Build parent-child relationships
- [ ] Generate aggregation constraints
- [ ] Validate totals match sums
- [ ] Handle multiple dimensions
- [ ] Write comprehensive tests

### Task 2.2: Extend Constraint Graph
**File**: Update `backend/app/hypercube.py`

**Changes**:
- [ ] Add hierarchical constraints to graph
- [ ] Handle multi-level aggregations
- [ ] Add protection propagation constraints
- [ ] Ensure totals protected if enough details suppressed
- [ ] Test with simple 1-level hierarchy

### Task 2.3: Update Primary Suppression
**File**: Update `backend/app/hypercube.py`

**Changes**:
- [ ] Apply protection rules to all hierarchy levels
- [ ] Handle different thresholds for totals vs details
- [ ] Propagate sensitivity up hierarchy
- [ ] Test with hierarchical tables

### Task 2.4: Update Optimization
**File**: Update `backend/app/hypercube.py`

**Changes**:
- [ ] Add hierarchical constraints to IP model
- [ ] Ensure parent-child suppression consistency
- [ ] Handle increased constraint complexity
- [ ] Add solver timeout handling
- [ ] Test optimization with hierarchies

---

## Phase 3: Frontend Integration

### Task 3.1: Add Parameter File Upload
**File**: Update `frontend/app/page.tsx`

**Changes**:
- [ ] Add parameter file upload component
- [ ] Add "Advanced Mode" toggle
- [ ] Handle two modes: simple (inline) vs advanced (file)
- [ ] Show parameter file preview

### Task 3.2: Add Cost Function Selector
**File**: New component `frontend/components/CostFunctionSelector.tsx`

**Features**:
- [ ] Dropdown for cost function type
- [ ] Input fields for cost parameters
- [ ] Preview of cost calculation
- [ ] Help text explaining each option

### Task 3.3: Display Hierarchies in UI
**File**: Update `frontend/components/ResultsDisplay.tsx`

**Features**:
- [ ] Indent rows based on hierarchy level
- [ ] Bold/style totals differently
- [ ] Collapse/expand hierarchy levels
- [ ] Color code hierarchy levels
- [ ] Show hierarchy structure in legend

---

## Phase 4: Testing & Validation

### Task 4.1: Create Test Suite
**Files**: `backend/tests/test_*.py`

**Test files to create**:
- [ ] `test_parameter_loader.py` - Parameter file parsing
- [ ] `test_cost_functions.py` - All cost strategies
- [ ] `test_hierarchy_parser.py` - Hierarchy detection
- [ ] `test_hypercube_hierarchical.py` - End-to-end with hierarchies
- [ ] `test_integration.py` - Full API tests

### Task 4.2: Create Test Data
**Files**: In `backend/tests/data/`

**Test datasets**:
- [ ] Flat table (current)
- [ ] 1-level hierarchy (Region totals)
- [ ] 2-level hierarchy (Region → SubRegion)
- [ ] Cross-classified (Region × Product)
- [ ] Invalid hierarchy (totals mismatch)
- [ ] Large table (performance test)

---

## Phase 5: Documentation

### Task 5.1: Technical Documentation
**Files to create**:
- [ ] `HIERARCHY_GUIDE.md` - How to structure hierarchical tables
- [ ] `PARAMETER_FILE_SPEC.md` - Complete parameter file reference
- [ ] `COST_FUNCTIONS.md` - Cost function guide
- [ ] `API_REFERENCE.md` - Updated API documentation

### Task 5.2: User Guide
**Files to update**:
- [ ] `README.md` - Update with new features
- [ ] `QUICK_START.md` - Add advanced examples
- [ ] `EXAMPLES.md` - Example workflows

---

## Current Status

✅ **Completed**:
- Basic hypercube implementation (flat tables)
- Web UI with file upload
- Protection rules (frequency, dominance, p-percent)
- Primary and secondary suppression
- Color-coded results (blue=primary, red=secondary)
- Excel export with colors

⏳ **Next Session (Phase 1)**:
- Parameter file schema design
- Parameter file loader
- Cost function implementation
- Integration with existing code

---

## Files to Prepare for Next Session

Please locate and prepare:
1. **Original SPAAS parameter files** - Any `.par`, `.ini`, or config files from Fortran SPAAS
2. **Example hierarchical tables** - Tables with subtotals/grand totals
3. **GHMITER4 documentation** - Any technical specs or user manuals
4. **Test data from original SPAAS** - Real-world examples

---

## Notes

- All changes maintain backward compatibility
- Existing `/suppress/hypercube/` endpoint continues to work
- New features accessible via `/suppress/hypercube/with-params/` or advanced UI
- Performance target: Handle tables up to 10,000 cells
- Testing strategy: Unit tests + integration tests + example files

---

## Questions for Next Session

1. What format are the original parameter files? (INI, custom format, etc.)
2. Are there specific hierarchy conventions in the original data?
3. What cost functions were used in the original SPAAS?
4. Are there any specific solver settings that were important?

---

**Last Updated**: 2026-01-12
**Status**: Ready to begin Phase 1
