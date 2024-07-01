import asyncio
import aiohttp
import json

from fastapi import HTTPException
from api_server.models.alerts import AlertRequest
from smart_cart_api_server.controllers.robot_status import get_robot_status
from urllib.parse import urljoin


async def notify_rmf_destination_complete(cart_id: str, destination: str, success: bool, api_server: str,  headers: dict[str, str] | None = None,):
    # Get task based on robot ID
    headers = headers or {}

    status = await get_robot_status(cart_id, api_server, headers)
    if status is None:
        raise  HTTPException(status_code=500, detail=f"Failed to get cart ID")

    async with aiohttp.ClientSession(headers=headers) as session:

        if status.task is None:
            print("No task found")
            raise  HTTPException(status_code=500, detail=f"No task underway")

        if status.task.taskId is None:
            print("No task id found")
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

        print(f"Location {status.task.currentLocationIndex+1}/{len(status.task.destinations)} completed")
        print(f"{status.task.destinations}")
        if status.task.currentLocationIndex + 1 == len(status.task.destinations):
            await asyncio.sleep(1.0)

            print(f"Last destination performing final checks {status.task.taskId}")
            retries = 0
            while retries < 3:
                retries += 1
                async with session.get(urljoin(api_server, f"alerts/requests/task/{status.task.taskId}")) as response:

                    if response.status != 200:
                        print("Invalid response")
                        raise  HTTPException(status_code=500, detail=f"got error from remote server")

                    alerts = json.loads(await response.text())
                    print(alerts)
                    if len(alerts) == 0:
                        print("Didn't get finishing request from cart")
                        await asyncio.sleep(2.0)
                        continue

                    alert = AlertRequest.parse_obj(alerts[0])

                    success = "success" if success else "fail"
                    async with session.post(urljoin(api_server, f"alerts/request/{alert.id}/respond?response={success}")) as response:
                        if response.status != 201:
                            print("Failed to respond to alert")
                            raise  HTTPException(status_code=500, detail=f"got error from remote server")
                    return

            print("Failed to get confirmation task")
            raise HTTPException(status_code=500, detail=f"got error from remote server")
