"""
τ-ARGUS Format Handlers
=======================

This module provides parsers and exporters for all τ-ARGUS file formats,
enabling full batch mode compatibility with existing τ-ARGUS workflows.

Supported Formats:
- .asc: Fixed-width ASCII microdata
- .rda: Metadata definitions
- .tab: Tabulated (pre-aggregated) data
- .hrc: Hierarchical structures
- .hst: A priori protection specifications
- .arb: Batch command files
- .sbs: Eurostat SBS output format

Author: Foteini
Date: January 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Variable:
    """Represents a variable definition from .rda metadata"""
    name: str
    start: int  # 1-indexed position in file
    length: int
    decimals: int = 0
    type: str = "EXPLANATORY"  # EXPLANATORY, RESPONSE, SHADOW, WEIGHT, HOLDING
    codelist: Optional[str] = None
    hierarchical: bool = False
    hierarchy_file: Optional[str] = None
    missing_values: List[str] = None
    
    def __post_init__(self):
        if self.missing_values is None:
            self.missing_values = []


@dataclass
class MetadataSpec:
    """Complete metadata specification from .rda file"""
    separator: str = ","
    variables: List[Variable] = None
    data_file: Optional[str] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = []


class TauArgusFormatHandler:
    """
    Handler for all τ-ARGUS file formats
    
    This class provides static methods to parse input formats and
    export output formats compatible with τ-ARGUS.
    """
    
    @staticmethod
    def parse_microdata_asc(
        asc_file: Path, 
        rda_file: Path
    ) -> pd.DataFrame:
        """
        Parse fixed-format .asc microdata using .rda metadata
        
        The .asc format is a fixed-width ASCII file where each variable
        occupies a specific column range. The .rda metadata file defines
        these column positions and variable properties.
        
        Example .asc:
        ```
        tr1 A001 01 1.0 26.5
        tr2 B002 02 3.3 96781.3
        tr3 A001 01 1.0 484.8
        ```
        
        Args:
            asc_file: Path to .asc data file
            rda_file: Path to .rda metadata file
            
        Returns:
            DataFrame with columns matching variable definitions
            
        Raises:
            FileNotFoundError: If files don't exist
            ValueError: If metadata is invalid
        """
        logger.info(f"Parsing microdata: {asc_file}")
        
        # 1. Parse .rda to get column specifications
        metadata = TauArgusFormatHandler.parse_metadata_rda(rda_file)
        
        # 2. Build colspecs for read_fwf
        colspecs = []
        names = []
        dtypes = {}
        converters = {}
        
        for var in metadata.variables:
            # Convert 1-indexed to 0-indexed and create range
            start = var.start - 1
            end = start + var.length
            colspecs.append((start, end))
            names.append(var.name)
            
            # Determine data type
            if var.decimals > 0:
                dtypes[var.name] = float
            elif var.type in ['RESPONSE', 'SHADOW', 'WEIGHT']:
                dtypes[var.name] = float
            else:
                dtypes[var.name] = str
            
            # Handle missing values
            if var.missing_values:
                def make_converter(missing_vals):
                    def converter(x):
                        x = x.strip()
                        if x in missing_vals:
                            return np.nan
                        return x
                    return converter
                converters[var.name] = make_converter(var.missing_values)
        
        # 3. Read fixed-width format
        df = pd.read_fwf(
            asc_file,
            colspecs=colspecs,
            names=names,
            dtype=dtypes,
            converters=converters if converters else None
        )
        
        logger.info(f"Loaded {len(df)} records with {len(df.columns)} variables")
        return df
    
    @staticmethod
    def parse_metadata_rda(rda_file: Path) -> MetadataSpec:
        """
        Parse .rda metadata file
        
        Format example:
        ```
        <SEPARATOR> ","
        <VARIABLE>
        Name=IndustryCode
        StartingPosition=6
        FieldLength=6
        Type=EXPLANATORY
        Codelist=industry_codes.txt
        Hierarchical=TRUE
        HierarchyFile=industry.hrc
        </VARIABLE>
        <VARIABLE>
        Name=Region
        StartingPosition=13
        FieldLength=2
        Type=EXPLANATORY
        </VARIABLE>
        <VARIABLE>
        Name=Var1
        StartingPosition=23
        FieldLength=10
        Decimals=1
        Type=RESPONSE
        </VARIABLE>
        ```
        
        Args:
            rda_file: Path to .rda metadata file
            
        Returns:
            MetadataSpec object with all variable definitions
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format is invalid
        """
        logger.info(f"Parsing metadata: {rda_file}")
        
        if not Path(rda_file).exists():
            raise FileNotFoundError(f"Metadata file not found: {rda_file}")
        
        metadata = MetadataSpec()
        current_variable = None
        in_variable_block = False
        
        with open(rda_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('//') or line.startswith('\\\\'):
                    continue
                
                # Handle XML-style tags
                if line.startswith('<'):
                    if line.upper().startswith('<SEPARATOR>'):
                        # Extract separator: <SEPARATOR> ","
                        match = re.search(r'<SEPARATOR>\s*["\']?([^"\']+)["\']?', line, re.IGNORECASE)
                        if match:
                            metadata.separator = match.group(1)
                    
                    elif line.upper() == '<VARIABLE>':
                        in_variable_block = True
                        current_variable = Variable(name="", start=0, length=0)
                    
                    elif line.upper() == '</VARIABLE>':
                        if current_variable and current_variable.name and current_variable.start > 0:
                            metadata.variables.append(current_variable)
                        in_variable_block = False
                        current_variable = None
                    
                    continue
                
                # Parse variable attributes
                if in_variable_block and current_variable:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        if key.upper() == 'NAME':
                            current_variable.name = value
                        elif key.upper() in ['STARTINGPOSITION', 'START']:
                            current_variable.start = int(value)
                        elif key.upper() in ['FIELDLENGTH', 'LENGTH']:
                            current_variable.length = int(value)
                        elif key.upper() == 'DECIMALS':
                            current_variable.decimals = int(value)
                        elif key.upper() == 'TYPE':
                            current_variable.type = value.upper()
                        elif key.upper() == 'CODELIST':
                            current_variable.codelist = value
                        elif key.upper() == 'HIERARCHICAL':
                            current_variable.hierarchical = value.upper() in ['TRUE', 'YES', '1']
                        elif key.upper() in ['HIERARCHYFILE', 'HIERARCHICAL_FILE']:
                            current_variable.hierarchy_file = value
                        elif key.upper() == 'MISSING':
                            # Handle missing value codes
                            current_variable.missing_values = [v.strip() for v in value.split(',')]
        
        if not metadata.variables:
            raise ValueError(f"No variables found in metadata file: {rda_file}")
        
        logger.info(f"Parsed {len(metadata.variables)} variable definitions")
        return metadata
    
    @staticmethod
    def parse_tabulated_tab(tab_file: Path) -> pd.DataFrame:
        """
        Parse semicolon-separated .tab tabulated data
        
        Format:
        ```
        IndustryCode;Region;Frequency;TopN;Var1
        "Total";"Total";42723;11395;86700593
        "103";"Total";3209;;3209
        "103";"NR";-;;-
        ```
        
        Args:
            tab_file: Path to .tab file
            
        Returns:
            DataFrame with tabulated data
        """
        logger.info(f"Parsing tabulated data: {tab_file}")
        
        df = pd.read_csv(
            tab_file,
            sep=';',
            quotechar='"',
            na_values=['-', ''],
            keep_default_na=True
        )
        
        logger.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
        return df
    
    @staticmethod
    def parse_hierarchy_hrc(hrc_file: Path) -> Dict[str, Dict]:
        """
        Parse .hrc hierarchy definition file
        
        Format:
        ```
        @1           # Level 1 (Region)
         @2          # Level 2 (NR = North)
          01         # Leaf code
          02
         @2.5        # Level 2 (OS = East)
          03
          04
        @1.5         # Level 1 (South)
         05
         06
        ```
        
        The @ prefix indicates a parent node (subtotal)
        Indentation determines hierarchy level
        
        Args:
            hrc_file: Path to .hrc file
            
        Returns:
            Dict mapping codes to their hierarchy information:
            {
                '01': {'parent': '@2', 'level': 0, 'is_total': False},
                '@2': {'parent': '@1', 'level': 1, 'is_total': True},
                ...
            }
        """
        logger.info(f"Parsing hierarchy: {hrc_file}")
        
        hierarchy = {}
        parent_stack = []  # Stack of (indent_level, code)
        
        with open(hrc_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Count leading spaces for indent level
                stripped = line.lstrip()
                if not stripped or stripped.startswith('//'):
                    continue
                
                indent = len(line) - len(stripped)
                code = stripped.strip()
                
                is_total = code.startswith('@')
                
                # Pop stack until we find appropriate parent level
                while parent_stack and parent_stack[-1][0] >= indent:
                    parent_stack.pop()
                
                parent_code = parent_stack[-1][1] if parent_stack else None
                level = len(parent_stack)
                
                hierarchy[code] = {
                    'parent': parent_code,
                    'level': level,
                    'is_total': is_total,
                    'children': []
                }
                
                # Add to parent's children
                if parent_code:
                    hierarchy[parent_code]['children'].append(code)
                
                # Push current node if it's a total (can have children)
                if is_total:
                    parent_stack.append((indent, code))
        
        logger.info(f"Parsed hierarchy with {len(hierarchy)} nodes")
        return hierarchy
    
    @staticmethod
    def parse_apriori_hst(hst_file: Path) -> Dict[str, str]:
        """
        Parse .hst a priori protection file
        
        Format:
        ```
        <code1>,<code2>,...,<status>
        
        Example:
        103,01,u        # Force unsafe
        103,02,s        # Force safe
        103,03,p        # Protect (infinite cost)
        ```
        
        Status codes:
        - s/S: Safe (force publication)
        - u/U: Unsafe (force suppression)
        - p/P: Protected (infinite cost, never suppress)
        
        Args:
            hst_file: Path to .hst file
            
        Returns:
            Dict mapping cell coordinates to status:
            {
                '103,01': 'unsafe',
                '103,02': 'safe',
                '103,03': 'protected'
            }
        """
        logger.info(f"Parsing a priori specifications: {hst_file}")
        
        apriori = {}
        
        with open(hst_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 2:
                    logger.warning(f"Line {line_num}: Invalid format, skipping")
                    continue
                
                status_code = parts[-1].upper()
                coords = ','.join(parts[:-1])
                
                if status_code == 'S':
                    apriori[coords] = 'safe'
                elif status_code == 'U':
                    apriori[coords] = 'unsafe'
                elif status_code == 'P':
                    apriori[coords] = 'protected'
                else:
                    logger.warning(f"Line {line_num}: Unknown status '{status_code}', skipping")
        
        logger.info(f"Loaded {len(apriori)} a priori specifications")
        return apriori
    
    @staticmethod
    def export_sbs_format(
        data: pd.DataFrame,
        output_file: Path,
        status_column: str = 'status',
        explanatory_vars: List[str] = None,
        response_var: str = None,
        shadow_var: str = None
    ):
        """
        Export protected table in Eurostat SBS format
        
        Format:
        ```
        "Code1","Code2",Value,Shadow,Status
        "Total","Total",86700593,38157,V
        "103","NR",-,-,D
        ```
        
        Status codes:
        - V: Visitable (safe to publish)
        - A: Primary unsafe (frequency rule)
        - B: Primary unsafe (dominance rule)
        - F: Primary unsafe (p-percent rule)
        - D: Secondary suppressed
        - X: Manually protected
        
        Args:
            data: DataFrame with protected table
            output_file: Path to output .sbs file
            status_column: Name of status column in data
            explanatory_vars: List of explanatory variable names
            response_var: Name of response variable
            shadow_var: Name of shadow variable (optional)
        """
        logger.info(f"Exporting SBS format: {output_file}")
        
        # Determine columns if not specified
        if explanatory_vars is None:
            # Use all non-numeric columns as explanatory
            explanatory_vars = data.select_dtypes(exclude=[np.number]).columns.tolist()
    
    # Convenience wrapper methods with simpler names
    @staticmethod
    def parse_tab_file(tab_file: str) -> pd.DataFrame:
        """Convenience wrapper for parse_tabulated_tab"""
        return TauArgusFormatHandler.parse_tabulated_tab(Path(tab_file))
    
    @staticmethod
    def parse_rda_file(rda_file: str) -> MetadataSpec:
        """Convenience wrapper for parse_metadata_rda"""
        return TauArgusFormatHandler.parse_metadata_rda(Path(rda_file))
    
    @staticmethod
    def parse_hrc_file(hrc_file: str) -> Dict[str, Dict]:
        """Convenience wrapper for parse_hierarchy_hrc"""
        return TauArgusFormatHandler.parse_hierarchy_hrc(Path(hrc_file))
    
    @staticmethod
    def parse_hst_file(hst_file: str) -> Dict[str, str]:
        """Convenience wrapper for parse_apriori_hst"""
        return TauArgusFormatHandler.parse_apriori_hst(Path(hst_file))
    
    @staticmethod
    def parse_asc_file(asc_file: str, rda_file: str) -> pd.DataFrame:
        """Convenience wrapper for parse_microdata_asc"""
        return TauArgusFormatHandler.parse_microdata_asc(Path(asc_file), Path(rda_file))
        
        if response_var is None:
            # Use first numeric column as response
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            response_var = numeric_cols[0] if numeric_cols else None
        
        # Build output columns
        output_cols = explanatory_vars.copy()
        if response_var:
            output_cols.append(response_var)
        if shadow_var and shadow_var in data.columns:
            output_cols.append(shadow_var)
        if status_column in data.columns:
            output_cols.append(status_column)
        
        # Write with quotes around string columns
        output_data = data[output_cols].copy()
        
        # Convert status to SBS codes if needed
        if status_column in output_data.columns:
            status_map = {
                'safe': 'V',
                'primary_frequency': 'A',
                'primary_dominance': 'B',
                'primary_p_percent': 'F',
                'secondary': 'D',
                'protected': 'X'
            }
            output_data[status_column] = output_data[status_column].map(
                lambda x: status_map.get(x, x) if pd.notna(x) else 'V'
            )
        
        # Write CSV with specific format
        output_data.to_csv(
            output_file,
            index=False,
            quoting=1,  # Quote all non-numeric fields
            na_rep='-'
        )
        
        logger.info(f"Exported {len(output_data)} rows to SBS format")


# TODO: Implement batch file parser next
# This will be in a separate file: batch_parser.py
