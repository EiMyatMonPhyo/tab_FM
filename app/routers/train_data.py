from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
import pandas as pd
from pandas.api.types import is_numeric_dtype
from app.services.trainer import train_model    
from app.services.model_id_generator import generate_model_id

router = APIRouter(
    prefix="/train-data",
    tags=["Training"]
)


@router.post("/")
async def train_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    task_type: str = Form(...)
):
    """
    task_type:
        - classification
        - regression
    """

    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported."
        )

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)

    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="File is empty."
        )

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    if task_type == "regression":
        # the last column should not contain null
        if y.isnull().any():
            raise HTTPException(
                status_code=400,
                detail="The last column contains null values."
            )

        # the last column should contain numeric type only
        if not is_numeric_dtype(y):
            raise HTTPException(
                status_code=400,
                detail="The last column must contain numeric values for regression."
            )

    # generate model_id
    model_id = generate_model_id(
        user_id=user_id,
        filename=file.filename,
        method= "train"
    )


    result = await train_model(
        X=X,
        y=y,
        task_type=task_type,
        file_name=file.filename,
        model_id=model_id,
        user_id= user_id,
        background_tasks=background_tasks
    )

    return result