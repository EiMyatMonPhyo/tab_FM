import os
import uuid
from pathlib import Path
import joblib
import tabfm
import torch
import asyncio
from typing import Any
from fastapi import BackgroundTasks

from app.services.task_storage import save_task_record, update_task_record_sync
from app.services.model_storage import save_model_record

MODEL_DIR = Path("saved_models")
MODEL_DIR.mkdir(exist_ok=True)

def _heavy_fit_worker(
    task_id: str,
    X: Any,
    y: Any,
    task_type: str,
    file_name: str,
    model_id: str,
    user_id: str
):
    try:
        update_task_record_sync(
            task_id=task_id,
            status="processing"
        )

        # Select execution device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load base TabFM model according to task type
        if task_type == "classification":
            model = tabfm.tabfm_v1_0_0_pytorch.load(
                model_type="classification",
                device=device,
                dtype=torch.bfloat16
            )
            tabFmModel = tabfm.TabFMClassifier(model=model)

        elif task_type == "regression":
            model = tabfm.tabfm_v1_0_0_pytorch.load(
                model_type="regression",
                device=device,
                dtype=torch.bfloat16
            )
            tabFmModel = tabfm.TabFMRegressor(model=model)

        else:
            raise ValueError("Unsupported task type.")

        ##############################
        cuda_available = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"

        print("=" * 50)
        print(f" PyTorch CUDA Available : {cuda_available}")
        print(f" Execution Device       : {device_name}")

        if hasattr(tabFmModel, "device"):
            print(f" Model Device           : {tabFmModel.device}")
        elif hasattr(tabFmModel, "model") and hasattr(tabFmModel.model, "device"):
            print(f" Model Device           : {tabFmModel.model.device}")
        print("=" * 50)
        ##############################
        # Train model
        tabFmModel.fit(X, y)

        # Save fitted model
        model_filename = f"{model_id}.joblib"
        model_path = MODEL_DIR / model_filename

        joblib.dump(
            tabFmModel,
            model_path
        )

        save_model_record(
            model_id=model_id,
            user_id=user_id,
            filename=file_name,
            model_path=str(model_path),
            task_type=task_type
        )

        result_payload = {
            "status": "success",
            "model_id": model_id,
            "model_path": str(model_path),
            "task_type": task_type,
            "file_name": file_name,
            "rows": len(X)
        }

        update_task_record_sync(
            task_id=task_id,
            status="completed",
            result=result_payload
        )

    except Exception as e:
        print("TRAINING ERROR : ", str(e))
        update_task_record_sync(
            task_id=task_id,
            status="failed",
            error=str(e)
        )

async def _run_fit_background(
    task_id: str,
    X: Any,
    y: Any,
    task_type: str,
    file_name: str,
    model_id: str,
    user_id: str
):
    try:
        await asyncio.to_thread(
            _heavy_fit_worker,
            task_id,
            X,
            y,
            task_type,
            file_name,
            model_id,
            user_id
        )

    except Exception as e:
        print("BACKGROUND FIT ERROR : ", str(e))
        update_task_record_sync(
            task_id=task_id,
            status="failed",
            error=str(e)
        )

async def train_model(
    X: Any,
    y: Any,
    task_type: str,
    file_name: str,
    model_id: str,
    user_id: str,
    background_tasks: BackgroundTasks
):
    task_id = str(uuid.uuid4())

    await save_task_record(
        task_id=task_id,
        model_id=model_id,
        status="pending"
    )

    background_tasks.add_task(
        _run_fit_background,
        task_id,
        X,
        y,
        task_type,
        file_name,
        model_id,
        user_id
    )

    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Model training task started."
    }

