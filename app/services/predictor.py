import uuid
import joblib
from typing import Any
from fastapi import BackgroundTasks
import asyncio

from app.services.task_storage import save_task_record, get_task_record, update_task_record_sync
from app.database.mongodb import models_collection

def load_trained_model(model_path: str):

    model = joblib.load(model_path)

    return model
def _heavy_predict_worker(
    task_id: str,
    X: Any,
    model_record: dict
):
    """
    Synchronous CPU-bound worker receiving the resolved model_record dict.
    """
    try:
        update_task_record_sync(
            task_id=task_id,
            status="processing"
        )

        model_id = model_record.get("model_id")
        model_path = model_record.get("model_path")
        print("MODEL PATH AT : ", model_path)

        trainedModel = load_trained_model(model_path)
        print("TRAINED MODEL : ", trainedModel)

        predictions = trainedModel.predict(X)
        print("PREDICTION : ", predictions)

        result_payload = {
            "status": "success",
            "model_id": model_id,
            "rows": len(X),
            "predictions": predictions.tolist()
        }

        update_task_record_sync(
            task_id=task_id,
            status="completed",
            result=result_payload
        )

    except Exception as e:
        print("PREDICTION ERROR : ", str(e))
        update_task_record_sync(
            task_id=task_id,
            status="failed",
            error=str(e)
        )


async def _run_predict_background(
    task_id: str,
    X: Any,
    model_id: str
):
    """
    1. Awaits the async MongoDB find_one call.
    2. Passes the fetched record to the heavy CPU worker thread.
    """
    try:
        # Await the model record on the main async event loop
        model_record = await models_collection.find_one({"model_id": model_id})

        if not model_record:
            update_task_record_sync(
                task_id=task_id,
                status="failed",
                error=f"Model not found: {model_id}"
            )
            return

        # Pass the resolved model_record dictionary to the background worker thread
        await asyncio.to_thread(_heavy_predict_worker, task_id, X, model_record)

    except Exception as e:
        print("BACKGROUND PREDICT ERROR : ", str(e))
        update_task_record_sync(
            task_id=task_id,
            status="failed",
            error=str(e)
        )
        
async def predict_model(
    X: Any,
    model_id: str,
    background_tasks: BackgroundTasks
):

    task_id = str(uuid.uuid4())

    await save_task_record(
        task_id=task_id,
        model_id=model_id,
        status="pending"
    )

    background_tasks.add_task(
        _run_predict_background,
        task_id,
        X,
        model_id
    )

    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Prediction task started."
    }


async def get_predict_status(task_id: str):

    task_record = await get_task_record(task_id)

    if not task_record:
        return {
            "status": "failed",
            "error": f"Task ID not found: {task_id}"
        }

    status = task_record.get("status", "pending")

    if status == "completed":
        return {
            "task_id": task_id,
            "status": "completed",
            "result": task_record.get("result")
        }

    elif status == "failed":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": task_record.get("error")
        }

    return {
        "task_id": task_id,
        "status": status,
        "message": "Prediction is still running..."
    }


# import tabfm
# import joblib
# from app.database.mongodb import models_collection

# def load_trained_model(model_path: str):

#     model = joblib.load(model_path)

#     return model

# async def predict_model(
#     X,
#     model_id: str
# ):
#     """
#     This function will:

#     1. Find model using model_id
#     2. Load trained model
#     3. Predict
#     """


#     # find model from model_id 
#     model_record = await models_collection.find_one(
#         {
#             "model_id": model_id
#         }
#     )

#     if not model_record:
#         raise ValueError(
#             f"Model not found: {model_id}"
#         )

#     model_path = model_record["model_path"]
#     print ("MODEL PATH AT : ", model_path)

#     # Load trained model
#     trainedModel = load_trained_model(
#         model_path
#     )

#     print ("TRAINED MODEL : ", trainedModel)
#     #
#     # Predict
#     predictions = trainedModel.predict(X)

#     print ("PREDICTION : ", predictions)

#     return {
#         "status": "success",
#         "model_id": model_id,
#         "rows": len(X),
#         "predictions": predictions.tolist()
#     }