from datetime import datetime
from typing import Any, Dict, Optional
from app.database.mongodb import tasks_collection

async def save_task_record(
    task_id: str,
    model_id: str,
    status: str = "pending"
):

    document = {
        "task_id": task_id,
        "model_id": model_id,
        "status": status,
        "result": None,
        "error": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    await tasks_collection.insert_one(document)


async def get_task_record(task_id: str):

    return await tasks_collection.find_one(
        {
            "task_id": task_id
        }
    )


def update_task_record_sync(
    task_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):

    tasks_collection.update_one(
        {"task_id": task_id},
        {
            "$set": {
                "status": status,
                "result": result,
                "error": error,
                "updated_at": datetime.utcnow()
            }
        }
    )