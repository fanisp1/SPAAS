from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import numpy as np
from io import StringIO, BytesIO

app = FastAPI(title="SPAAS Modernized API")

@app.get("/")
def read_root():
    return {"message": "SPAAS Modernized Backend is running."}

@app.post("/analyze/")
async def analyze_table(file: UploadFile = File(...)):
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