from app.services.task_storage import get_task_record

async def get_status(task_id: str):

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

