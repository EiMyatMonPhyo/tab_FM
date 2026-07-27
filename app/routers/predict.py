from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
import pandas as pd

from app.services.predictor import predict_model, get_predict_status
from app.services.model_id_generator import generate_model_id

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.post("/")
async def predict(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...)
):

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    df = pd.read_csv(file.file)

    # model_id to be used
    model_id = generate_model_id(
        user_id=user_id,
        filename=file.filename
    )

    result = await predict_model(
        X=df,
        model_id=model_id,
        background_tasks=background_tasks
    )

    return result


@router.get("/status/{task_id}")
async def predict_status(task_id: str):

    result = await get_predict_status(task_id)

    return result
