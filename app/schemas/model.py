from pydantic import BaseModel
from datetime import datetime


class ModelRecord(BaseModel):
    model_id: str
    user_id: str
    filename: str
    model_path: str
    task_type: str,
    column_names: list[str],
    num_columns: int,
    num_rows: int
    created_at: datetime

