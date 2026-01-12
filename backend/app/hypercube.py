"""
Hypercube Secondary Cell Suppression Method

This module implements the hypercube method for secondary cell suppression,
replacing the original GHMITER4 Fortran implementation with modern Python
using graph algorithms and optimization techniques.

The hypercube method protects sensitive cells by finding optimal secondary
suppressions that prevent disclosure through additive constraints.
"""

import numpy as np
import pandas as pd
import networkx as nx
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from ortools.linear_solver import pywraplp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CellInfo:
    """Represents a single cell in the table with its properties"""
    cell_id: str
    row_idx: int
    col_idx: int
    value: float
    is_primary_suppressed: bool
    suppression_cost: float
    sensitivity_level: float = 1.0
    
    def __hash__(self):
        return hash(self.cell_id)


@dataclass
class AdditiveConstraint:
    """Represents an additive relationship between cells (e.g., row/column totals)"""
    constraint_id: str
    cell_ids: List[str]
    total: float
    constraint_type: str  # 'row', 'column', 'margin', etc.


@dataclass
class ProtectionRules:
    """Defines the protection rules for cell suppression"""
    min_frequency: int = 3  # Minimum frequency rule
    dominance_n: int = 1    # n-dominance rule (top n contributors)
    dominance_k: float = 80.0  # k% threshold for dominance
    p_percent: float = 10.0  # p-percent rule
    safety_range: float = 0.1  # Protection level (10% = cannot estimate within 10%)


class HypercubeEngine:
    """
    Advanced Hypercube Secondary Suppression Engine
    
    This class implements the hypercube method using graph algorithms
    to find optimal secondary suppressions that protect sensitive cells.
    """
    
    def __init__(self, protection_rules: Optional[ProtectionRules] = None):
        """
        Initialize the hypercube engine
        
        Args:
            protection_rules: Rules for determining cell sensitivity
        """
        self.protection_rules = protection_rules or ProtectionRules()
        self.constraint_graph: Optional[nx.Graph] = None
        self.cells: Dict[str, CellInfo] = {}
        self.constraints: List[AdditiveConstraint] = []
        
    def identify_primary_suppressions(
        self, 
        data: pd.DataFrame,
        sensitive_cols: Optional[List[str]] = None
    ) -> Set[str]:
        """
        Identify primary suppressions based on protection rules
        
        Args:
            data: Input table as pandas DataFrame
            sensitive_cols: List of sensitive column names (if applicable)
            
        Returns:
            Set of cell IDs that need primary suppression
        """
        logger.info("Identifying primary suppressions...")
        primary_cells = set()
        
        # Get only numeric columns
        numeric_data = data.select_dtypes(include=[np.number])
        if numeric_data.empty:
            logger.warning("No numeric columns found in data")
            return primary_cells
        
        # Get the column indices in the original dataframe
        numeric_col_indices = [data.columns.get_loc(col) for col in numeric_data.columns]
        
        rows = len(data)
        
        # Apply all protection rules to each cell (only numeric columns)
        for i in range(rows):
            for j in numeric_col_indices:
                cell_value = data.iloc[i, j]
                cell_id = f"cell_{i}_{j}"
                
                # Skip NaN values and non-numeric values
                if pd.isna(cell_value) or not isinstance(cell_value, (int, float, np.number)):
                    continue
                
                suppress_reasons = []
                
                # Rule 1: Frequency rule - suppress if value < threshold
                if cell_value < self.protection_rules.min_frequency:
                    suppress_reasons.append("frequency")
                
                # Rule 2: Dominance rule - check row and column
                if self._check_dominance_rule(i, j, data):
                    suppress_reasons.append("dominance")
                
                # Rule 3: P-percent rule
                if self._check_p_percent_rule(i, j, data):
                    suppress_reasons.append("p-percent")
                
                # If any rule triggered, add to primary suppressions
                if suppress_reasons:
                    primary_cells.add(cell_id)
                    logger.debug(f"Primary suppression: {cell_id} (rules: {', '.join(suppress_reasons)})")
        
        logger.info(f"Identified {len(primary_cells)} primary suppressions")
        return primary_cells
    
    def _check_dominance_rule(self, row_idx: int, col_idx: int, data: pd.DataFrame) -> bool:
        """
        Check n-k dominance rule for a cell
        
        A cell fails the dominance rule if the top n contributors account for
        more than k% of the total in either its row or column.
        
        Args:
            row_idx: Row index of the cell
            col_idx: Column index of the cell
            data: Full data table
            
        Returns:
            True if cell violates dominance rule (needs suppression)
        """
        cell_value = data.iloc[row_idx, col_idx]
        
        # Get only numeric data
        numeric_data = data.select_dtypes(include=[np.number])
        
        # Check row dominance (only numeric values)
        row_values = numeric_data.iloc[row_idx, :].dropna().tolist()
        if len(row_values) > 1:
            row_total = sum(row_values)
            if row_total > 0:
                sorted_row = sorted(row_values, reverse=True)
                top_n_sum = sum(sorted_row[:self.protection_rules.dominance_n])
                dominance_pct = (top_n_sum / row_total) * 100
                
                if dominance_pct > self.protection_rules.dominance_k:
                    # Check if current cell is in top n
                    if cell_value in sorted_row[:self.protection_rules.dominance_n]:
                        return True
        
        # Check column dominance (only numeric values)
        col_name = data.columns[col_idx]
        if col_name in numeric_data.columns:
            col_values = numeric_data[col_name].dropna().tolist()
        else:
            return False  # Non-numeric column, skip dominance check
        if len(col_values) > 1:
            col_total = sum(col_values)
            if col_total > 0:
                sorted_col = sorted(col_values, reverse=True)
                top_n_sum = sum(sorted_col[:self.protection_rules.dominance_n])
                dominance_pct = (top_n_sum / col_total) * 100
                
                if dominance_pct > self.protection_rules.dominance_k:
                    # Check if current cell is in top n
                    if cell_value in sorted_col[:self.protection_rules.dominance_n]:
                        return True
        
        return False
    
    def _check_p_percent_rule(self, row_idx: int, col_idx: int, data: pd.DataFrame) -> bool:
        """
        Check p-percent rule for a cell
        
        The p-percent rule protects against disclosure when an attacker can
        estimate the cell value within p% by using marginal totals.
        
        Args:
            row_idx: Row index of the cell
            col_idx: Column index of the cell
            data: Full data table
            
        Returns:
            True if cell violates p-percent rule (needs suppression)
        """
        cell_value = data.iloc[row_idx, col_idx]
        
        if cell_value == 0:
            return False
        
        # Get only numeric data
        numeric_data = data.select_dtypes(include=[np.number])
        col_name = data.columns[col_idx]
        
        # Skip if not numeric column
        if col_name not in numeric_data.columns:
            return False
        
        # Check row-based estimation risk (only numeric values)
        row_values = numeric_data.iloc[row_idx, :].dropna().tolist()
        if len(row_values) > 1:
            row_total = sum(row_values)
            others_in_row = [v for idx, v in enumerate(row_values) if idx != col_idx]
            
            if others_in_row:
                max_other = max(others_in_row)
                min_other = min(others_in_row)
                
                # Calculate estimation interval
                interval = cell_value * (self.protection_rules.p_percent / 100)
                
                # Check if cell can be estimated within p%
                estimated_min = row_total - sum(others_in_row) - interval
                estimated_max = row_total - sum(others_in_row) + interval
                
                # If true value falls within narrow estimation range, needs protection
                if abs(estimated_max - estimated_min) < 2 * interval:
                    return True
        
        # Check column-based estimation risk (only numeric values)
        col_values = numeric_data[col_name].dropna().tolist()
        if len(col_values) > 1:
            col_total = sum(col_values)
            others_in_col = [v for idx, v in enumerate(col_values) if idx != row_idx]
            
            if others_in_col:
                # Calculate estimation interval
                interval = cell_value * (self.protection_rules.p_percent / 100)
                
                # Check if cell can be estimated within p%
                estimated_min = col_total - sum(others_in_col) - interval
                estimated_max = col_total - sum(others_in_col) + interval
                
                # If true value falls within narrow estimation range, needs protection
                if abs(estimated_max - estimated_min) < 2 * interval:
                    return True
        
        return False
    
    def build_constraint_graph(
        self,
        data: pd.DataFrame,
        primary_suppressions: Set[str]
    ) -> nx.Graph:
        """
        Build a constraint graph representing additive relationships
        
        Args:
            data: Input table as pandas DataFrame
            primary_suppressions: Set of primary suppressed cell IDs
            
        Returns:
            NetworkX graph with cells as nodes and constraints as edges
        """
        logger.info("Building constraint graph...")
        G = nx.Graph()
        
        # Get only numeric columns
        numeric_data = data.select_dtypes(include=[np.number])
        numeric_col_indices = [data.columns.get_loc(col) for col in numeric_data.columns]
        
        rows = len(data)
        cols = len(data.columns)
        
        # Create cell nodes (only for numeric columns)
        for i in range(rows):
            for j in numeric_col_indices:
                cell_id = f"cell_{i}_{j}"
                cell_value = data.iloc[i, j]
                
                # Skip non-numeric values
                if not isinstance(cell_value, (int, float, np.number)) or pd.isna(cell_value):
                    continue
                    
                is_primary = cell_id in primary_suppressions
                
                # Calculate suppression cost (based on information loss)
                # Higher values have higher suppression cost
                cost = float(cell_value) if not np.isnan(cell_value) else 1.0
                
                cell_info = CellInfo(
                    cell_id=cell_id,
                    row_idx=i,
                    col_idx=j,
                    value=cell_value,
                    is_primary_suppressed=is_primary,
                    suppression_cost=cost
                )
                
                self.cells[cell_id] = cell_info
                
                # Add node to graph with attributes
                G.add_node(
                    cell_id,
                    value=cell_value,
                    cost=cost,
                    is_primary=is_primary,
                    row=i,
                    col=j
                )
        
        # Add row constraints (cells in same row are additively related)
        # Only include numeric columns
        for i in range(rows):
            row_cells = [f"cell_{i}_{j}" for j in numeric_col_indices]
            # Only sum numeric columns
            row_total = numeric_data.iloc[i, :].sum()
            
            constraint = AdditiveConstraint(
                constraint_id=f"row_{i}",
                cell_ids=row_cells,
                total=row_total,
                constraint_type="row"
            )
            self.constraints.append(constraint)
            
            # Connect all cells in the row (complete subgraph)
            for idx1, cell1 in enumerate(row_cells):
                for cell2 in row_cells[idx1+1:]:
                    G.add_edge(cell1, cell2, constraint_type="row", constraint_id=f"row_{i}")
        
        # Add column constraints (only for numeric columns)
        for j in numeric_col_indices:
            col_cells = [f"cell_{i}_{j}" for i in range(rows)]
            # Get the position in numeric_data
            col_name = data.columns[j]
            col_total = numeric_data[col_name].sum()
            
            constraint = AdditiveConstraint(
                constraint_id=f"col_{j}",
                cell_ids=col_cells,
                total=col_total,
                constraint_type="column"
            )
            self.constraints.append(constraint)
            
            # Connect all cells in the column
            for idx1, cell1 in enumerate(col_cells):
                for cell2 in col_cells[idx1+1:]:
                    G.add_edge(cell1, cell2, constraint_type="column", constraint_id=f"col_{j}")
        
        self.constraint_graph = G
        logger.info(f"Constraint graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return G
    
    def solve_secondary_suppressions(self) -> Set[str]:
        """
        Solve for optimal secondary suppressions using integer programming
        
        Returns:
            Set of cell IDs that should be secondarily suppressed
        """
        logger.info("Solving for secondary suppressions...")
        
        if self.constraint_graph is None:
            raise ValueError("Constraint graph not built. Call build_constraint_graph first.")
        
        # Create solver instance
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            logger.warning("SCIP solver not available, using CBC")
            solver = pywraplp.Solver.CreateSolver('CBC')
        
        # Decision variables: x[cell_id] = 1 if cell should be suppressed
        suppress_vars = {}
        for cell_id, cell_info in self.cells.items():
            if cell_info.is_primary_suppressed:
                # Primary suppressions are fixed to 1
                suppress_vars[cell_id] = None  # Will handle separately
            else:
                # Binary variable for secondary suppression
                suppress_vars[cell_id] = solver.BoolVar(f'suppress_{cell_id}')
        
        # Objective: minimize total suppression cost
        objective = solver.Objective()
        for cell_id, var in suppress_vars.items():
            if var is not None:
                cost = self.cells[cell_id].suppression_cost
                objective.SetCoefficient(var, cost)
        objective.SetMinimization()
        
        # Constraints: protection constraints for each additive relationship
        # Each constraint must have enough suppressions to protect sensitive cells
        for constraint in self.constraints:
            # Count primary suppressions in this constraint
            primary_cells_in_constraint = [
                cid for cid in constraint.cell_ids 
                if self.cells[cid].is_primary_suppressed
            ]
            primary_count = len(primary_cells_in_constraint)
            
            # If there are primary suppressions, we need additional secondaries
            if primary_count > 0:
                # Build expression for secondary suppressions in this constraint
                suppression_terms = []
                for cid in constraint.cell_ids:
                    if suppress_vars[cid] is not None:
                        suppression_terms.append(suppress_vars[cid])
                
                if suppression_terms:  # Only add constraint if there are secondary variables
                    # Adaptive constraint: more primaries need more secondaries
                    # But ensure it's feasible (can't require more than available)
                    available_cells = len(suppression_terms)
                    
                    if primary_count == 1:
                        # Single primary: need at least 2 secondaries for protection
                        min_secondary = min(2, available_cells)
                    else:
                        # Multiple primaries: need at least 1 secondary per primary
                        # but cap at available cells minus 1 (to avoid forcing all)
                        min_secondary = min(primary_count, max(1, available_cells - 1))
                    
                    if min_secondary > 0 and min_secondary <= available_cells:
                        constraint_expr = solver.Sum(suppression_terms)
                        solver.Add(constraint_expr >= min_secondary)
                        logger.debug(
                            f"Constraint {constraint.constraint_id}: "
                            f"{primary_count} primaries, need >= {min_secondary} secondaries "
                            f"from {available_cells} available"
                        )
        
        # Solve the optimization problem
        logger.info(f"Running optimization solver with {solver.NumVariables()} variables and {solver.NumConstraints()} constraints...")
        status = solver.Solve()
        
        secondary_suppressions = set()
        
        # Map status codes to readable messages
        status_messages = {
            pywraplp.Solver.OPTIMAL: "Optimal solution found",
            pywraplp.Solver.FEASIBLE: "Feasible solution found (not proven optimal)",
            pywraplp.Solver.INFEASIBLE: "Problem is infeasible",
            pywraplp.Solver.UNBOUNDED: "Problem is unbounded",
            pywraplp.Solver.ABNORMAL: "Solver terminated abnormally",
            pywraplp.Solver.NOT_SOLVED: "Problem not solved"
        }
        
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            status_msg = status_messages.get(status, f"Unknown status {status}")
            logger.info(f"{status_msg}. Objective value: {solver.Objective().Value()}")
            
            for cell_id, var in suppress_vars.items():
                if var is not None and var.solution_value() > 0.5:
                    secondary_suppressions.add(cell_id)
            
            logger.info(f"Found {len(secondary_suppressions)} secondary suppressions")
        else:
            status_msg = status_messages.get(status, f"Unknown status {status}")
            logger.error(f"Solver failed: {status_msg}")
            logger.error(f"Number of constraints with primaries: {sum(1 for c in self.constraints if any(self.cells[cid].is_primary_suppressed for cid in c.cell_ids))}")
            
            # If infeasible, relax constraints and try again
            if status == pywraplp.Solver.INFEASIBLE:
                logger.warning("Problem infeasible - this may indicate conflicting constraints or insufficient cells")
                logger.warning("Falling back to simple heuristic suppression...")
                return self._heuristic_secondary_suppression()
            
            raise RuntimeError(f"Solver failed: {status_msg}")
        
        return secondary_suppressions
    
    def _heuristic_secondary_suppression(self) -> Set[str]:
        """
        Heuristic fallback method for secondary suppressions
        Used when optimization problem is infeasible
        
        Returns:
            Set of cell IDs for secondary suppression
        """
        logger.info("Using heuristic secondary suppression method...")
        secondary_suppressions = set()
        
        # For each constraint with primary suppressions, 
        # add the cheapest non-primary cells until we have enough
        for constraint in self.constraints:
            # Find primary suppressions in this constraint
            primary_in_constraint = [
                cid for cid in constraint.cell_ids
                if self.cells[cid].is_primary_suppressed
            ]
            
            if len(primary_in_constraint) > 0:
                # Find non-suppressed cells in this constraint
                available_cells = [
                    (cid, self.cells[cid].suppression_cost)
                    for cid in constraint.cell_ids
                    if not self.cells[cid].is_primary_suppressed
                    and cid not in secondary_suppressions
                ]
                
                # Sort by cost (cheapest first)
                available_cells.sort(key=lambda x: x[1])
                
                # Add the cheapest 2 cells as secondary suppressions
                for cid, _ in available_cells[:2]:
                    secondary_suppressions.add(cid)
        
        logger.info(f"Heuristic method found {len(secondary_suppressions)} secondary suppressions")
        return secondary_suppressions
    
    def apply_suppressions(
        self,
        data: pd.DataFrame,
        primary_cells: Set[str],
        secondary_cells: Set[str],
        suppress_value: str = "X"
    ) -> Tuple[pd.DataFrame, Set[str]]:
        """
        Apply suppressions to the data table
        
        Args:
            data: Original data table
            primary_cells: Primary suppressed cells
            secondary_cells: Secondary suppressed cells
            suppress_value: Value to use for suppressed cells (not used, kept for compatibility)
            
        Returns:
            Tuple of (DataFrame with original values, Set of suppressed cell coordinates)
        """
        logger.info("Applying suppressions to table...")
        # Keep original data - don't replace with 'X'
        result = data.copy()
        
        # Return both the data and the set of suppressed cells
        # The frontend will handle the visual highlighting
        all_suppressions = primary_cells.union(secondary_cells)
        
        logger.info(f"Marked {len(all_suppressions)} cells for suppression")
        return result, all_suppressions
    
    def run_hypercube_suppression(
        self,
        data: pd.DataFrame,
        sensitive_cols: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Complete hypercube suppression pipeline
        
        Args:
            data: Input table as pandas DataFrame
            sensitive_cols: Optional list of sensitive column names
            
        Returns:
            Tuple of (suppressed_data, statistics_dict)
        """
        logger.info("Starting hypercube suppression pipeline...")
        
        # Step 1: Identify primary suppressions
        primary_cells = self.identify_primary_suppressions(data, sensitive_cols)
        
        # Step 2: Build constraint graph
        self.build_constraint_graph(data, primary_cells)
        
        # Step 3: Solve for secondary suppressions
        secondary_cells = self.solve_secondary_suppressions()
        
        # Step 4: Apply suppressions (returns data + suppressed cells list)
        suppressed_data, suppressed_cells = self.apply_suppressions(data, primary_cells, secondary_cells)
        
        # Convert primary cells to coordinate format
        primary_coords = []
        for cell_id in primary_cells:
            parts = cell_id.split("_")
            if len(parts) == 3:
                primary_coords.append({"row": int(parts[1]), "col": int(parts[2])})
        
        # Convert secondary cells to coordinate format
        secondary_coords = []
        for cell_id in secondary_cells:
            parts = cell_id.split("_")
            if len(parts) == 3:
                secondary_coords.append({"row": int(parts[1]), "col": int(parts[2])})
        
        # Step 5: Compile statistics
        statistics = {
            "total_cells": data.shape[0] * data.shape[1],
            "primary_suppressions": len(primary_cells),
            "secondary_suppressions": len(secondary_cells),
            "total_suppressions": len(primary_cells) + len(secondary_cells),
            "suppression_rate": (len(primary_cells) + len(secondary_cells)) / (data.shape[0] * data.shape[1]),
            "method": "hypercube",
            "primary_cells": primary_coords,
            "secondary_cells": secondary_coords,
            "protection_rules": {
                "min_frequency": self.protection_rules.min_frequency,
                "dominance_n": self.protection_rules.dominance_n,
                "dominance_k": self.protection_rules.dominance_k
            }
        }
        
        logger.info("Hypercube suppression complete!")
        logger.info(f"Statistics: {statistics}")
        
        return suppressed_data, statistics


# Convenience function for direct use
def hypercube_suppress(
    data: pd.DataFrame,
    protection_rules: Optional[ProtectionRules] = None,
    sensitive_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict]:
    """
    Apply hypercube secondary suppression to a data table
    
    Args:
        data: Input table as pandas DataFrame
        protection_rules: Protection rules configuration
        sensitive_cols: Optional list of sensitive column names
        
    Returns:
        Tuple of (suppressed_data, statistics_dict)
    """
    engine = HypercubeEngine(protection_rules)
    return engine.run_hypercube_suppression(data, sensitive_cols)
