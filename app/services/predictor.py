import uuid
import joblib
from typing import Any
from fastapi import BackgroundTasks
import asyncio
import torch

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

        ##############################
        cuda_available = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"
        
        print("=" * 50)
        print(f" PyTorch CUDA Available : {cuda_available}")
        print(f" Execution Device       : {device_name}")
        
        # If TabFM/PyTorch model has a .device attribute or parameters:
        if hasattr(trainedModel, "device"):
            print(f" Model Device           : {trainedModel.device}")
        elif hasattr(trainedModel, "model") and hasattr(trainedModel.model, "device"):
            print(f" Model Device           : {trainedModel.model.device}")
        print("=" * 50)
        ##############################


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

        # X test should contain all the columns in X train
        # Check input columns
        train_columns = model_record.get("column_names", [])        # train X
        test_columns = X.columns.tolist()           # test X

        print ("train_columns: ", train_columns )
        print ("test_columns: ", test_columns )

        missing_columns = [
            col for col in train_columns
            if col not in test_columns
        ]

        if missing_columns:
            update_task_record_sync(
                task_id=task_id,
                status="failed",
                error=(
                    f"Missing required columns: {missing_columns}"
                )
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
        "message": "Still running..."
    }

