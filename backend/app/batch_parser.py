"""
Batch file parser for τ-ARGUS .arb files.

This module parses batch command files (.arb) used by τ-ARGUS for automated
table protection workflows.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import re


@dataclass
class SafetyRule:
    """Safety rule specification."""
    rule_type: str  # "Frequency" or "Dominance"
    parameters: List[Any]
    
    def __repr__(self):
        params = ','.join(str(p) for p in self.parameters)
        return f"{self.rule_type}({params})"


@dataclass
class BatchCommand:
    """Represents a single batch command."""
    command: str
    parameters: Dict[str, Any]
    
    def __repr__(self):
        return f"<{self.command}> {self.parameters}"


@dataclass
class BatchFile:
    """Parsed batch file structure."""
    commands: List[BatchCommand]
    microdata_file: Optional[str] = None
    table_data_file: Optional[str] = None
    metadata_file: Optional[str] = None
    table_spec: Optional[Dict[str, Any]] = None
    safety_rules: List[SafetyRule] = None
    suppression_method: Optional[str] = None
    output_file: Optional[str] = None
    output_format: Optional[str] = None
    
    def __post_init__(self):
        if self.safety_rules is None:
            self.safety_rules = []


class BatchParser:
    """Parser for τ-ARGUS batch files (.arb)."""
    
    COMMAND_PATTERN = re.compile(r'<(\w+)>\s*(.*?)(?=<|$)', re.DOTALL)
    
    @staticmethod
    def parse_file(file_path: Path) -> BatchFile:
        """
        Parse a batch file (.arb).
        
        Args:
            file_path: Path to .arb file
            
        Returns:
            BatchFile object with parsed commands
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return BatchParser.parse_content(content, base_path=file_path.parent)
    
    @staticmethod
    def parse_content(content: str, base_path: Optional[Path] = None) -> BatchFile:
        """
        Parse batch file content.
        
        Args:
            content: Raw .arb file content
            base_path: Base directory for resolving relative paths
            
        Returns:
            BatchFile object
        """
        # Remove comments (lines starting with //)
        lines = [line for line in content.split('\n') 
                 if not line.strip().startswith('//')]
        content = '\n'.join(lines)
        
        # Extract commands
        commands = []
        matches = BatchParser.COMMAND_PATTERN.finditer(content)
        
        for match in matches:
            cmd_name = match.group(1)
            cmd_content = match.group(2).strip()
            
            command = BatchParser._parse_command(cmd_name, cmd_content)
            commands.append(command)
        
        # Build BatchFile object
        return BatchParser._build_batch_file(commands, base_path)
    
    @staticmethod
    def _parse_command(cmd_name: str, cmd_content: str) -> BatchCommand:
        """Parse individual command."""
        parameters = {}
        
        if cmd_name in ['OPENMICRODATA', 'OPENTABLEDATA', 'OPENMETADATA']:
            # File path commands - extract quoted string
            match = re.search(r'"([^"]+)"', cmd_content)
            if match:
                parameters['file'] = match.group(1)
        
        elif cmd_name == 'SPECIFYTABLE':
            # Table specification: "ResponseVar" "Dim1" "Dim2" | "Shadow" | "Cost"
            parameters['spec'] = BatchParser._parse_table_spec(cmd_content)
        
        elif cmd_name == 'READTABLE':
            # READTABLE has optional parameter (1, 2, 1T, etc.)
            parameters['mode'] = cmd_content.strip() if cmd_content else '1'
        
        elif cmd_name == 'SAFETYRULE':
            # Parse safety rules
            parameters['rules'] = BatchParser._parse_safety_rules(cmd_content)
        
        elif cmd_name == 'SUPPRESS':
            # Suppression method with optional parameters
            parameters['method'] = BatchParser._parse_suppress(cmd_content)
        
        elif cmd_name == 'WRITETABLE':
            # Output specification
            parameters['output'] = BatchParser._parse_write_table(cmd_content)
        
        elif cmd_name == 'GOINTERACTIVE':
            # No parameters
            pass
        
        else:
            # Unknown command - store raw content
            parameters['raw'] = cmd_content
        
        return BatchCommand(command=cmd_name, parameters=parameters)
    
    @staticmethod
    def _parse_table_spec(spec_str: str) -> Dict[str, Any]:
        """
        Parse table specification.
        
        Format: "ResponseVar" "Dim1" "Dim2" | "Shadow" | "Cost"
        """
        result = {
            'response': None,
            'explanatory': [],
            'shadow': None,
            'cost': None,
            'weight': None,
            'holding': None
        }
        
        # Split by pipe to get sections
        sections = spec_str.split('|')
        
        # First section: dimensions
        dims_section = sections[0].strip()
        dims = re.findall(r'"([^"]+)"', dims_section)
        
        if dims:
            result['response'] = dims[0]
            result['explanatory'] = dims[1:] if len(dims) > 1 else []
        
        # Additional sections
        for i, section in enumerate(sections[1:], 1):
            vars_in_section = re.findall(r'"([^"]+)"', section)
            if vars_in_section:
                var_name = vars_in_section[0]
                # Try to determine variable type from position
                if i == 1:
                    result['shadow'] = var_name
                elif i == 2:
                    result['cost'] = var_name
                elif i == 3:
                    result['weight'] = var_name
        
        return result
    
    @staticmethod
    def _parse_safety_rules(rules_str: str) -> List[SafetyRule]:
        """
        Parse safety rules.
        
        Examples:
            Frequency(3,10)
            Dominance(1,85)
            P(15,3)
        """
        rules = []
        
        # Match rule patterns: RuleName(param1,param2,...)
        pattern = r'(\w+)\(([^)]+)\)'
        matches = re.finditer(pattern, rules_str)
        
        for match in matches:
            rule_type = match.group(1)
            params_str = match.group(2)
            
            # Parse parameters
            params = []
            for p in params_str.split(','):
                p = p.strip()
                try:
                    # Try int first
                    params.append(int(p))
                except ValueError:
                    try:
                        # Try float
                        params.append(float(p))
                    except ValueError:
                        # Keep as string
                        params.append(p)
            
            rules.append(SafetyRule(rule_type=rule_type, parameters=params))
        
        return rules
    
    @staticmethod
    def _parse_suppress(suppress_str: str) -> Dict[str, Any]:
        """
        Parse suppression method.
        
        Examples:
            HYPERCUBE
            GH(1,100,0,1)
            MOD(1,100)
        """
        result = {'method': None, 'parameters': []}
        
        # Check if method has parameters
        match = re.match(r'(\w+)(?:\(([^)]+)\))?', suppress_str.strip())
        if match:
            result['method'] = match.group(1)
            
            if match.group(2):
                # Parse parameters
                params = []
                for p in match.group(2).split(','):
                    p = p.strip()
                    try:
                        params.append(int(p))
                    except ValueError:
                        try:
                            params.append(float(p))
                        except ValueError:
                            params.append(p)
                result['parameters'] = params
        
        return result
    
    @staticmethod
    def _parse_write_table(output_str: str) -> Dict[str, str]:
        """
        Parse write table output specification.
        
        Example:
            Output="result.sbs"
            Format=SBS
        """
        result = {}
        
        # Extract key=value or key="value" pairs
        pattern = r'(\w+)=(?:"([^"]+)"|(\w+))'
        matches = re.finditer(pattern, output_str)
        
        for match in matches:
            key = match.group(1)
            value = match.group(2) if match.group(2) else match.group(3)
            result[key.lower()] = value
        
        return result
    
    @staticmethod
    def _build_batch_file(commands: List[BatchCommand], 
                         base_path: Optional[Path]) -> BatchFile:
        """Build BatchFile object from parsed commands."""
        batch = BatchFile(commands=commands)
        
        for cmd in commands:
            if cmd.command == 'OPENMICRODATA':
                file_path = cmd.parameters.get('file')
                batch.microdata_file = BatchParser._resolve_path(file_path, base_path)
            
            elif cmd.command == 'OPENTABLEDATA':
                file_path = cmd.parameters.get('file')
                batch.table_data_file = BatchParser._resolve_path(file_path, base_path)
            
            elif cmd.command == 'OPENMETADATA':
                file_path = cmd.parameters.get('file')
                batch.metadata_file = BatchParser._resolve_path(file_path, base_path)
            
            elif cmd.command == 'SPECIFYTABLE':
                batch.table_spec = cmd.parameters.get('spec')
            
            elif cmd.command == 'SAFETYRULE':
                batch.safety_rules = cmd.parameters.get('rules', [])
            
            elif cmd.command == 'SUPPRESS':
                suppress_info = cmd.parameters.get('method', {})
                batch.suppression_method = suppress_info.get('method')
            
            elif cmd.command == 'WRITETABLE':
                output_info = cmd.parameters.get('output', {})
                batch.output_file = output_info.get('output')
                batch.output_format = output_info.get('format', 'SBS')
        
        return batch
    
    @staticmethod
    def _resolve_path(file_path: str, base_path: Optional[Path]) -> str:
        """
        Resolve file path relative to base path.
        
        If path is absolute or base_path is None, return as-is.
        Otherwise, resolve relative to base_path.
        """
        if not file_path or not base_path:
            return file_path
        
        path = Path(file_path)
        
        # If absolute path, return as-is
        if path.is_absolute():
            return file_path
        
        # Resolve relative to base path
        resolved = (base_path / path).resolve()
        return str(resolved)


# Convenience function
def parse_batch_file(file_path: str) -> BatchFile:
    """
    Parse a batch file.
    
    Args:
        file_path: Path to .arb file (string or Path)
        
    Returns:
        BatchFile object
    """
    return BatchParser.parse_file(Path(file_path))
