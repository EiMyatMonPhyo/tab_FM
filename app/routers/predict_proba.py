from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd

from app.services.predictor_proba import predict_proba_model
from app.services.model_id_generator import generate_model_id


router = APIRouter(
    prefix="/predict_proba",
    tags=["predict_proba"]
)


@router.post("/")
async def predict_proba(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )
  
    # read csv
    df = pd.read_csv(file.file)

    # generate same model id used in fit
    model_id = generate_model_id(
        user_id=user_id,
        filename=file.filename
    )


    result = await predict_proba_model(
        X=df,
        model_id=model_id
    )

    return result