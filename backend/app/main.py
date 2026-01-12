from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import json

from .hypercube import hypercube_suppress, ProtectionRules

app = FastAPI(
    title="SPAAS Modernized API",
    description="Statistical Package for Automated Anonymization Software - Modern Python Implementation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SPAAS Modernized Backend is running."}

@app.post("/analyze/")
async def analyze_table(file: UploadFile = File(...)):
    """Analyze uploaded table and return basic statistics"""
    contents = await file.read()
    filename = file.filename.lower()

    # Decide how to load based on file extension
    if filename.endswith('.csv'):
        # CSV: decode bytes to string
        s = str(contents, 'utf-8')
        df = pd.read_csv(StringIO(s))
    elif filename.endswith('.xlsx'):
        # Excel: read directly from bytes
        df = pd.read_excel(BytesIO(contents))
    else:
        raise HTTPException(status_code=400, detail="File must be a CSV or Excel (.xlsx) file")

    # Solution: Replace NaN with None for JSON compatibility
    sample_head = df.head().replace({np.nan: None}).to_dict(orient="records")
    
    info = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),
        "sample_head": sample_head
    }
    return info


@app.post("/suppress/hypercube/")
async def hypercube_suppression(
    file: UploadFile = File(...),
    min_frequency: int = 3,
    dominance_n: int = 1,
    dominance_k: float = 80.0,
    p_percent: float = 10.0
):
    """
    Apply hypercube secondary suppression to uploaded table
    
    Parameters:
    - file: CSV or Excel file containing the data table
    - min_frequency: Minimum frequency threshold (default: 3)
    - dominance_n: Number of top contributors for dominance rule (default: 1)
    - dominance_k: Percentage threshold for dominance (default: 80.0)
    - p_percent: P-percent rule threshold (default: 10.0)
    
    Returns:
    - JSON with suppressed table and statistics
    """
    try:
        # Read uploaded file
        contents = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            s = str(contents, 'utf-8')
            df = pd.read_csv(StringIO(s))
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV or Excel (.xlsx) file"
            )
        
        # Create protection rules from parameters
        protection_rules = ProtectionRules(
            min_frequency=min_frequency,
            dominance_n=dominance_n,
            dominance_k=dominance_k,
            p_percent=p_percent
        )
        
        # Apply hypercube suppression
        suppressed_data, statistics = hypercube_suppress(
            data=df,
            protection_rules=protection_rules
        )
        
        # Convert suppressed data to JSON-compatible format
        suppressed_json = suppressed_data.replace({np.nan: None}).to_dict(orient="records")
        
        result = {
            "status": "success",
            "method": "hypercube",
            "statistics": statistics,
            "suppressed_data": suppressed_json,
            "column_names": suppressed_data.columns.tolist()
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing table: {str(e)}"
        )


@app.post("/suppress/hypercube/download/")
async def hypercube_suppression_download(
    file: UploadFile = File(...),
    min_frequency: int = Form(3),
    dominance_n: int = Form(1),
    dominance_k: float = Form(80.0),
    p_percent: float = Form(10.0),
    output_format: str = Form("csv")
):
    """
    Apply hypercube suppression and download result as file with red highlighting
    
    Parameters:
    - file: CSV or Excel file containing the data table
    - min_frequency: Minimum frequency threshold (default: 3)
    - dominance_n: Number of top contributors for dominance rule (default: 1)
    - dominance_k: Percentage threshold for dominance (default: 80.0)
    - p_percent: P-percent rule threshold (default: 10.0)
    - output_format: Output format ('csv' or 'excel')
    
    Returns:
    - Downloadable file with suppressed data (red cells in Excel)
    """
    try:
        # Read uploaded file
        contents = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            s = str(contents, 'utf-8')
            df = pd.read_csv(StringIO(s))
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV or Excel (.xlsx) file"
            )
        
        # Apply hypercube suppression
        protection_rules = ProtectionRules(
            min_frequency=min_frequency,
            dominance_n=dominance_n,
            dominance_k=dominance_k,
            p_percent=p_percent
        )
        suppressed_data, statistics = hypercube_suppress(
            data=df,
            protection_rules=protection_rules
        )
        
        # Get primary and secondary cell coordinates
        primary_coords = set()
        for cell in statistics.get('primary_cells', []):
            primary_coords.add((cell['row'], cell['col']))
        
        secondary_coords = set()
        for cell in statistics.get('secondary_cells', []):
            secondary_coords.add((cell['row'], cell['col']))
        
        # Generate downloadable file
        if output_format == "csv":
            stream = StringIO()
            suppressed_data.to_csv(stream, index=False)
            return StreamingResponse(
                iter([stream.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=suppressed_data.csv"}
            )
        elif output_format == "excel":
            # Export with color formatting
            from openpyxl import Workbook
            from openpyxl.styles import Font
            
            wb = Workbook()
            ws = wb.active
            
            # Write headers
            for c_idx, col_name in enumerate(suppressed_data.columns, 1):
                ws.cell(row=1, column=c_idx, value=str(col_name))
            
            # Write data with color formatting
            for r_idx in range(len(suppressed_data)):
                for c_idx in range(len(suppressed_data.columns)):
                    value = suppressed_data.iloc[r_idx, c_idx]
                    
                    # Convert to Excel-friendly format
                    if pd.isna(value):
                        cell_value = None
                    elif isinstance(value, (int, float, np.number)):
                        cell_value = float(value)
                    else:
                        cell_value = str(value)
                    
                    cell = ws.cell(row=r_idx+2, column=c_idx+1, value=cell_value)
                    
                    # Apply colors
                    if (r_idx, c_idx) in primary_coords:
                        cell.font = Font(color="0000FF", bold=True)  # Blue for primary
                    elif (r_idx, c_idx) in secondary_coords:
                        cell.font = Font(color="FF0000", bold=True)  # Red for secondary
            
            stream = BytesIO()
            wb.save(stream)
            excel_bytes = stream.getvalue()
            
            from fastapi.responses import Response
            return Response(
                content=excel_bytes,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=suppressed_data.xlsx"}
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="output_format must be 'csv' or 'excel'"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing table: {str(e)}"
        )
