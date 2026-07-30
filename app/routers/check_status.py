from app.services.status_checker import get_status
from fastapi import APIRouter

router = APIRouter(
    prefix="/check-status",
    tags=["Checking Status"]
)

@router.get("/{task_id}")
async def get_task_status(task_id: str):

    result = await get_status(task_id)

    return result
