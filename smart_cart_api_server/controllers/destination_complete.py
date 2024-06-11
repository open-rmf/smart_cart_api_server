import aiohttp
import json

from fastapi import HTTPException
from api_server.models.alerts import AlertRequest
from smart_cart_api_server.controllers.robot_status import get_robot_status
from urllib.parse import urljoin


# Placeholder for RMF communication function
async def notify_rmf_destination_complete(cart_id: str, destination: str, success: bool, api_server: str):
    # Get task based on robot ID
    status = await get_robot_status(cart_id, api_server)
    if status is None:
        raise  HTTPException(status_code=500, detail=f"Failed to get cart ID")

    async with aiohttp.ClientSession() as session:

        if status.task.taskId is None:
            raise  HTTPException(status_code=500, detail=f"No task underway")

        #post_body = {"task_id": status.task.taskId, "location": destination, "success": success}
        async with session.get(urljoin(api_server, f"alerts/requests/task/{status.task.taskId}")) as response:

            if response.status != 200:
                raise HTTPException(status_code=500, detail=f"got error from remote server")

            alerts = json.loads(await response.text())
            if len(alerts) == 0:
                raise HTTPException(status_code=500, detail=f"Cart is not currently waiting")
            alert = AlertRequest.parse_obj(alerts[0])

            success = "success" if success else "fail"
            async with session.post(urljoin(api_server, f"alerts/request/{alert.id}/respond?response={success}")) as response:
                if response.status != 201:
                    raise  HTTPException(status_code=500, detail=f"got error from remote server")
            return
