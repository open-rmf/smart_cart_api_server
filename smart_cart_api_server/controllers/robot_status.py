from smart_cart_api_server.models.robot_status import RobotStatus
from smart_cart_api_server.controllers.task_status import get_task_status
from api_server.models.rmf_api.fleet_state import FleetState
import aiohttp
import datetime
import json
from fastapi import HTTPException
from urllib.parse import urljoin

async def get_robot_status(
    robot_id: str,
    api_server="http://localhost:8000/",
    headers: dict[str, str] | None = None,
) -> None | RobotStatus:
    """
    Retrieve robot status given robot_id
    """
    headers = headers or {}
    curr_robot = None
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(urljoin(api_server, "fleets")) as response:

            fleets = json.loads(await response.text())

            for fleet in fleets:
                fleet_state = FleetState.parse_obj(fleet)
                if robot_id in fleet_state.robots:
                    curr_robot = fleet_state.robots[robot_id]

        if curr_robot is None:
            print (f"Could not get robot {robot_id}")
            return None

        assigned_task = None

        current_location = None
        travelling_to = None
        if curr_robot.task_id:
            print("Retrieving task")
            assigned_task = await get_task_status(
                curr_robot.task_id, api_server, headers
            )
            if (
                assigned_task is not None
                and assigned_task.currentLocationIndex is not None
            ):
                current_location = assigned_task.destinations[
                    assigned_task.currentLocationIndex
                ]
            if (
                assigned_task is not None
                and assigned_task.travellingToIndex is not None
            ):
                travelling_to = assigned_task.destinations[
                    assigned_task.travellingToIndex
                ]
            print("Got location")

        return RobotStatus(
            dateTime=datetime.datetime.now(),
            robotId=robot_id,
            batteryPercentage=int(curr_robot.battery * 100),
            robotState=curr_robot.status.value,
            currentLocation=current_location,
            travellingTo=travelling_to,
            task=assigned_task,
        )
