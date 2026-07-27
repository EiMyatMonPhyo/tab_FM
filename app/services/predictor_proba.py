import joblib
import tabfm
from app.database.mongodb import models_collection
from fastapi import HTTPException

def load_trained_model(model_path: str):

    model = joblib.load(model_path)
    return model 


async def predict_proba_model(
    X,
    model_id: str
):

    # find model metadata
    model_record = await models_collection.find_one(
        {
            "model_id": model_id
        }
    )

    if not model_record:
        raise ValueError(
            f"Model not found: {model_id}"
        )

    if model_record["task_type"] == "regression" or model_record["task_type"] != "classification":
        raise HTTPException(
            status_code=400,
            detail="predict_proba is only available for classification models."
        )

    model_path = model_record["model_path"]


    # load fitted model
    trained_model = load_trained_model(
        model_path
    )


    # probability prediction
    probabilities = trained_model.predict_proba(X)


    return {
        "status": "success",
        "model_id": model_id,
        "rows": len(X),
        "probabilities": probabilities.tolist()
    }