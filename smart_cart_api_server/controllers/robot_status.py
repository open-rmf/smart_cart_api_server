from smart_cart_api_server.models.robot_status import RobotStatus
from smart_cart_api_server.controllers.task_status import parse_task_status
from api_server.models.rmf_api.task_state import TaskState
from api_server.models.rmf_api.fleet_state import FleetState
import aiohttp
import datetime
import json



async def get_robot_status(robot_id: str, api_server = "http://localhost:8000/") -> RobotStatus:
    """
    Retrieve robot status given robot_id
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_server}fleets") as response:
            fleets = json.loads(await response.text())
            curr_robot = None
            for fleet in fleets:
                fleet_state = FleetState.parse_obj(fleet)
                if robot_id in fleet_state.robots:
                    curr_robot = fleet_state.robots[robot_id]

        if curr_robot is None:
            return None

        assigned_task = None

        if curr_robot.task_id:
            async with session.get(f"{api_server}tasks?task_id={curr_robot.task_id}") as response:
                assigned_task = parse_task_status(await response.text())

        return RobotStatus(
            dateTime=datetime.datetime.now(),
            robotId=robot_id,
            batteryPercentage=int(curr_robot.battery * 100),
            robotState= curr_robot.status,
            currentLocation=None,
            travellingTo=None,
            task=assigned_task
        )