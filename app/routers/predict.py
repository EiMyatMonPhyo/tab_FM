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

    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported."
        )

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)

    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)

    # model_id to be used
    model_id = generate_model_id(
        user_id=user_id,
        filename=file.filename,
        method= "test"
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
