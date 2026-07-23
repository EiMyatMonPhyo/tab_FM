from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import StringIO

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)

@router.post("/")
async def predict(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))

    # TODO: Run tabFM model

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "predictions": []
    }