from api_server.models.rmf_api.task_state import TaskState, Status
from smart_cart_api_server.models.task_status import TaskStatus, TaskDestination
import json
import datetime
import aiohttp
from parse import parse
from fastapi import HTTPException
from urllib.parse import urljoin

async def get_task_status(
    task_id: str, api_server: str, headers: dict[str, str]
) -> TaskStatus | None:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(urljoin(api_server, f"tasks?task_id={task_id}")) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=500, detail=f"got error from remote server"
                )

            assigned_task = parse_task_status(await response.text())

            return assigned_task


def parse_task_status(task_state: str) -> TaskStatus | None:
    """
    This function parses a task state coming in from a json string into the robots current location.
    Note: This function makes some pretty strong assumptions about the task structure. Namely that:
    - Every "Perform Action" is a pickup/dropoff location
    - The "Perform Action" provides a way to
    """
    tasks = json.loads(task_state)

    if len(tasks) == 0:
        return None

    state = TaskState.parse_obj(tasks[0])

    locations = []
    loc_idxs = {}
    next_loc_idx = {}

    task_type = ""
    key_values = [x.split("=", 1) for x in state.booking.labels]
    for k, v in key_values:
        if k == "task_type":
            task_type = v

    if task_type not in ["single-pickup-multi-dropoff", "multi-pickup-single-dropoff"]:
        print("Invalid task type")
        return None

    if state.phases is None:
        return TaskStatus(
            taskId=state.booking.id,
            dateTime=datetime.datetime.fromtimestamp(
                state.unix_millis_start_time, tz=datetime.timezone.utc
            ),
            robotId=state.assigned_to.name,
            fleetId=state.assigned_to.group,
            cartId=state.assigned_to.name,  # For now only use cart_id
            destinations=locations,
            currentLocationIndex=None,
            travellingToIndex=None,
            authorizedDepartures=[],
            unauthorizedDepartures=[],
            status=state.status.value,
            taskType=task_type
        )

    for p in sorted(state.phases.keys()):
        ### LOTS OF MAGIC
        x = json.loads(state.phases[p].detail.__root__)[0]
        if x["category"] == "Perform action":
            res = parse(
                "Performing action wait_until at waypoint [[place:{place}]]",
                x["detail"],
            )
            loc_idxs[p] = len(locations)
            locations.append(
                TaskDestination(name=res["place"], compartment=None, action="pickup")
            )
        else:
            next_loc_idx[p] = len(locations)

    if task_type == "single-pickup-multi-dropoff":
        for i in range(1, len(locations)):
           locations[i].action = "dropoff"
    else:
        locations[-1].action = "dropoff"

    current_location = None
    traveling_to = None

    if state.status == Status.underway and state.active is not None:
        # hack
        st = str(state.active.__root__)
        detail = json.loads(state.phases[st].detail.__root__)[0]
        if detail["category"] == "Perform action":
            current_location = loc_idxs[st]
        else:
            next_idx = next_loc_idx[st]
            if next_idx < len(locations):
                traveling_to = next_idx

    return TaskStatus(
        taskId=state.booking.id,
        dateTime=datetime.datetime.fromtimestamp(
            state.unix_millis_start_time, tz=datetime.timezone.utc
        ),
        robotId=state.assigned_to.name,
        fleetId=state.assigned_to.group,
        cartId=state.assigned_to.name,  # For now only use cart_id
        destinations=locations,
        currentLocationIndex=current_location,
        travellingToIndex=traveling_to,
        authorizedDepartures=[],
        unauthorizedDepartures=[],
        status=str(state.status.value),
        taskType = task_type
    )
