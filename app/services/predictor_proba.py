import uuid
import joblib
import asyncio
from typing import Any
from fastapi import BackgroundTasks, HTTPException
import torch

from app.services.task_storage import save_task_record, get_task_record, update_task_record_sync
from app.database.mongodb import models_collection
def load_trained_model(model_path: str):

    model = joblib.load(model_path)
    return model 

def _heavy_predict_proba_worker(
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

        trained_model = load_trained_model(model_path)
        print("TRAINED MODEL : ", trained_model)

        ##############################
        cuda_available = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"
        
        print("=" * 50)
        print(f" PyTorch CUDA Available : {cuda_available}")
        print(f" Execution Device       : {device_name}")
        
        # If TabFM/PyTorch model has a .device attribute or parameters:
        if hasattr(trained_model, "device"):
            print(f" Model Device           : {trained_model.device}")
        elif hasattr(trained_model, "model") and hasattr(trained_model.model, "device"):
            print(f" Model Device           : {trained_model.model.device}")
        print("=" * 50)
        ##############################


        probabilities = trained_model.predict_proba(X)
        print("PROBABILITIES : ", probabilities)

        result_payload = {
            "status": "success",
            "model_id": model_id,
            "rows": len(X),
            "probabilities": probabilities.tolist()
        }

        update_task_record_sync(
            task_id=task_id,
            status="completed",
            result=result_payload
        )

    except Exception as e:
        print("PREDICT PROBA ERROR : ", str(e))
        update_task_record_sync(
            task_id=task_id,
            status="failed",
            error=str(e)
        )

async def _run_predict_proba_background(
    task_id: str,
    X: Any,
    model_id: str
):
    try:
        model_record = await models_collection.find_one({"model_id": model_id})

        if not model_record:
            update_task_record_sync(
                task_id=task_id,
                status="failed",
                error=f"Model not found: {model_id}"
            )
            return

        if model_record.get("task_type") == "regression" or model_record.get("task_type") != "classification":
            print ("task type : ", model_record.get("task_type"))
            print ("regression is not supported for classification model")
            update_task_record_sync(
                task_id=task_id,
                status="failed",
                error="predict_proba is only available for classification models."
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

        await asyncio.to_thread(_heavy_predict_proba_worker, task_id, X, model_record)

    except Exception as e:
        print("BACKGROUND PREDICT PROBA ERROR : ", str(e))
        update_task_record_sync(
            task_id=task_id,
            status="failed",
            error=str(e)
        )
    
async def predict_proba_model(
    X,
    model_id: str,
    background_tasks: BackgroundTasks
):

    model_record = await models_collection.find_one({"model_id": model_id})

    if not model_record:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {model_id}"
        )

    if model_record.get("task_type") == "regression" or model_record.get("task_type") != "classification":
        raise HTTPException(
            status_code=400,
            detail="predict_proba is only available for classification models."
        )

    task_id = str(uuid.uuid4())

    await save_task_record(
        task_id=task_id,
        model_id=model_id,
        status="pending"
    )

    background_tasks.add_task(
        _run_predict_proba_background,
        task_id,
        X,
        model_id
    )
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Probability prediction task started."
    }
    

    