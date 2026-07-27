from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime


class TaskRecord(BaseModel):
    task_id: str
    model_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime