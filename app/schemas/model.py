from pydantic import BaseModel
from datetime import datetime


class ModelRecord(BaseModel):
    model_id: str
    user_id: str
    filename: str
    model_path: str
    task_type: str
    created_at: datetime