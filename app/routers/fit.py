from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd

from app.services.trainer import train_model    
from app.services.model_id_generator import generate_model_id

router = APIRouter(
    prefix="/fit",
    tags=["Training"]
)


@router.post("/")
async def fit(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    task_type: str = Form(...)
):
    """
    task_type:
        - classification
        - regression
    """

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    # read file and convert to df
    df = pd.read_csv(file.file)

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # generate model_id
    model_id = generate_model_id(
        user_id=user_id,
        filename=file.filename
    )


    result = await train_model(
        X=X,
        y=y,
        task_type=task_type,
        file_name=file.filename,
        model_id=model_id,
        user_id= user_id
    )

    return result