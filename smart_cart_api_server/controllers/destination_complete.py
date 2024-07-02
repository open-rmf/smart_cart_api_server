import asyncio
import aiohttp
import json

from fastapi import HTTPException
from api_server.models.alerts import AlertRequest, AlertResponse
from smart_cart_api_server.controllers.robot_status import get_robot_status
from urllib.parse import urljoin


async def notify_rmf_destination_complete(cart_id: str, destination: str, success: bool, api_server: str,  headers: dict[str, str] | None = None,):
    # Get task based on robot ID
    headers = headers or {}
    print("Notifying")

    status = await get_robot_status(cart_id, api_server, headers)
    if status is None:
        print("Could not get cart")
        raise  HTTPException(status_code=500, detail=f"Failed to get cart ID")

    print("Got status")

    async with aiohttp.ClientSession(headers=headers) as session:

        if status.task is None:
            print("No task found")
            raise  HTTPException(status_code=500, detail=f"No task underway")

        if status.task.taskId is None:
            print("No task id found")
            raise  HTTPException(status_code=500, detail=f"No task underway")

        print("Querying alerts")
        #post_body = {"task_id": status.task.taskId, "location": destination, "success": success}
        async with session.get(urljoin(api_server, f"alerts/requests/task/{status.task.taskId}")) as response:

            if response.status != 200:
                raise HTTPException(status_code=500, detail=f"got error from remote server")

            alerts = json.loads(await response.text())
            if len(alerts) == 0:
                print("No alert available")
                raise HTTPException(status_code=500, detail=f"Cart is not currently waiting")
            alert = AlertRequest.parse_obj(alerts[0])

            success = "success" if success else "fail"
            async with session.post(urljoin(api_server, f"alerts/request/{alert.id}/respond?response={success}")) as response:
                if response.status != 201:
                    print("Response was mpt ackmowledged")
                    raise  HTTPException(status_code=500, detail=f"got error from remote server")
        print("Responded to alert")
        print(f"Location {status.task.currentLocationIndex+1}/{len(status.task.destinations)} completed")
        print(f"{status.task.destinations}")
        if status.task.currentLocationIndex + 1 == len(status.task.destinations):
            # Get responded alerts
            all_ok = True
            do_check_on_last = True
            async with session.get(urljoin(api_server, f"alerts/requests/task/{status.task.taskId}?unresponded=false")) as response:
                alerts = json.loads(await response.text())
                for alert in alerts:
                    al = AlertRequest.parse_obj(alert)
                    alert_id = al.id
                    if al.title == "Robot is at final location, checking if all items have been delivered":
                        print("Found task alert check")
                        do_check_on_last = False
                    async with session.get(urljoin(api_server, f"alerts/request/{alert_id}/response")) as response:
                        alert_response_json = json.loads(await response.text())
                        alert_response = AlertResponse.parse_obj(alert_response_json)
                        if alert_response.response == "fail":
                            all_ok = False

            print(f"Last destination performing final checks {status.task.taskId}")
            retries = 0
            while retries < 3 and do_check_on_last:
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

                    success = "success" if all_ok else "fail"
                    async with session.post(urljoin(api_server, f"alerts/request/{alert.id}/respond?response={success}")) as response:
                        if response.status != 201:
                            print("Failed to respond to alert")
                            raise  HTTPException(status_code=500, detail=f"got error from remote server")
                    return

            if do_check_on_last:
                print("Failed to get confirmation task")
                raise HTTPException(status_code=500, detail=f"got error from remote server")
