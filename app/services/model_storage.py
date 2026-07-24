from datetime import datetime

from app.database.mongodb import models_collection


async def save_model_record(
    model_id: str,
    user_id: str,
    filename: str,
    model_path: str,
    task_type: str
):

    document = {
        "model_id": model_id,
        "user_id": user_id,
        "filename": filename,
        "model_path": model_path,
        "task_type": task_type,
        "created_at": datetime.utcnow()
    }

    await models_collection.insert_one(document)



async def get_model_record(model_id: str):

    return await models_collection.find_one(
        {
            "model_id": model_id
        }
    )