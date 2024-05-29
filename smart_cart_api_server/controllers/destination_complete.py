import aiohttp
from fastapi import HTTPException
from smart_cart_api_server.controllers.robot_status import get_robot_status

# Placeholder for RMF communication function
async def notify_rmf_destination_complete(cart_id: str, destination: str, success: bool, api_server: str):
    # Get task based on robot ID
    status = await get_robot_status(cart_id, api_server)
    if status is None:
        raise  HTTPException(status_code=500, detail=f"Failed to get cart ID")

    async with aiohttp.ClientSession() as session:
        post_body = {"task_id": status.task.taskId, "location": destination, "success": success}
        async with session.post(f"{api_server}tasks/location_complete", data=post_body) as response:
            if response.status != 200:
                raise  HTTPException(status_code=500, detail=f"got error from remote server")

            return
