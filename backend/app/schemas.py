# For Pydantic models if you want to use strong type validation for FastAPI

from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    pass  # Define request schema here

class AnalyzeResponse(BaseModel):
    rows: int
    columns: int
    column_names: List[str]
    sample_head: list

# Add more models as needed