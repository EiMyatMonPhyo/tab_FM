import os
from pathlib import Path
import joblib
import tabfm
from tabfm import tabfm_v1_0_0_pytorch

from app.services.model_storage import save_model_record

MODEL_DIR = Path("saved_models")
MODEL_DIR.mkdir(exist_ok=True)

async def train_model(
    X,
    y,
    task_type: str,
    file_name: str,
    model_id: str,
    user_id: str
):
    """
    Train a TabFM model.

    Later this function will:
    - load base model
    - create classifier/regressor
    - fit
    - save trained model
    - save metadata to DB
    """

    # Load TabFM model
    if task_type == "classification":
        model = tabfm_v1_0_0_pytorch.load(
            model_type="classification",
            device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            dtype=torch.bfloat16
        )
        tabFmModel = tabfm.TabFMClassifier(model=model)

    elif task_type == "regression":
        model = tabfm_v1_0_0_pytorch.load(
            model_type="regression",
            device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            dtype=torch.bfloat16
        )
        tabFmModel = tabfm.TabFMRegressor(model=model)

    else:
        raise ValueError("Unsupported task type.")

    # trained model
    tabFmModel.fit(X, y)

    # TODO
    # save fitted model (inside saved_models)
    model_filename = f"{model_id}.joblib"

    model_path = MODEL_DIR / model_filename


    joblib.dump(
        tabFmModel,
        model_path
    )

    # TODO
    # save metadata to database
    # model_id + model file path (may be together with CSV file name) so that /predict can find from db with csv filename or may be find with model unique name
    await save_model_record(
        model_id=model_id,
        user_id=user_id,
        filename=file_name,
        model_path=str(model_path),
        task_type=task_type
    )
    return {
        "status": "success",
        "model_id": model_id,
        "model_path": str(model_path),
        "task_type": task_type,
        "file_name": file_name,
        "rows": len(X)
    }