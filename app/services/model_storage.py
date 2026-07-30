from datetime import datetime

from app.database.mongodb import models_collection


def save_model_record(
    model_id: str,
    user_id: str,
    filename: str,
    model_path: str,
    task_type: str,
    column_names: list[str],
    num_columns: int,
    num_rows: int
):

    document = {
        "model_id": model_id,
        "user_id": user_id,
        "filename": filename,
        "model_path": model_path,
        "task_type": task_type,
        "column_names": column_names,
        "num_columns": num_columns,
        "num_rows": num_rows,
        "created_at": datetime.utcnow()
    }

    models_collection.insert_one(document)



def get_model_record(model_id: str):

    return models_collection.find_one(
        {
            "model_id": model_id
        }
    )

def update_model_record(
    model_id: str,
    user_id: str,
    filename: str,
    model_path: str,
    task_type: str,
    column_names: list[str],
    num_columns: int,
    num_rows: int
):

    models_collection.update_one(
        {
            "model_id": model_id
        },
        {
            "$set": {
                "user_id": user_id,
                "filename": filename,
                "model_path": model_path,
                "task_type": task_type,
                "column_names": column_names,
                "num_columns": num_columns,
                "num_rows": num_rows,
                "updated_at": datetime.utcnow()
            }
        }
    )