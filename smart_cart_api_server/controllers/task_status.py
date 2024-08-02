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

def show_last_destination(current_idx, travelling_idx, locations):
    if current_idx is not None and current_idx + 1 == len(locations):
        return True
    elif travelling_idx is not None and travelling_idx + 1 == len(locations):
        return True
    return False


def parse_task_status(task_state: str) -> TaskStatus | None:
    """
    This function parses a task state coming in from a json string into the robots current location.
    Note: This function makes some pretty strong assumptions about the task structure. Namely that:
    - Every "Perform Action" is a pickup/dropoff location
    - The "Perform Action" provides a way to
    """
    tasks = json.loads(task_state)

    if len(tasks) == 0:
        print("No tasks found")
        return None

    state = TaskState.parse_obj(tasks[0])

    locations = []
    loc_idxs = {}
    next_loc_idx = {}

    task_type = ""
    compartments = []
    for label in state.booking.labels:
        label_json = json.loads(label)
        if "description" not in label_json:
            continue

        label_description = label_json["description"]
        if "task_type" in label_description:
            task_type = label_description["task_type"]
        if "compartments" in label_description:
            compartments = label_description["compartments"].split(",")

    if task_type == "":
        print("No booking labels available to parse")
        return None

    if task_type not in ["single-pickup-multi-dropoff", "multi-pickup-single-dropoff"]:
        print("Invalid task type")
        return None

    if state.phases is None:
        return TaskStatus(
            taskId=state.booking.id,
            dateTime=datetime.datetime.now(),
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
    for p in sorted(state.phases.keys(), key=lambda x: int(x)):
        ### LOTS OF MAGIC
        x = json.loads(state.phases[p].detail.__root__)[0]
        if x["category"] == "Perform action":
            res = parse(
                "Performing action wait_until at waypoint [[place:{place}]]",
                x["detail"],
            )
            loc_idxs[p] = len(locations)
            compartment = None if len(compartments) <= len(locations) else compartments[len(locations)]
            locations.append(
                TaskDestination(name=res["place"], compartment=compartment, action="pickup", staging=False)
            )
        else:
            next_loc_idx[p] = len(locations)

    # These workflows are extremely specific to the task types
    if task_type == "single-pickup-multi-dropoff":
        # First pickup and final dropoff will notify the smart cart to wait
        # indefinitely
        locations[0].staging = True
        locations[-1].staging = True
        for i in range(1, len(locations)):
           locations[i].action = "dropoff"
    elif task_type == "multi-pickup-single-dropoff":
        # Final dropoff will notify the smart cart to wait indefinitely
        locations[-1].action = "dropoff"
        locations[-1].staging = True

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
        dateTime=datetime.datetime.now(),
        robotId=state.assigned_to.name,
        fleetId=state.assigned_to.group,
        cartId=state.assigned_to.name,  # For now only use cart_id
        destinations=locations[:-1] if not show_last_destination(current_location, traveling_to, locations) else locations, # For now assume end location is the last location.
        currentLocationIndex=current_location,
        travellingToIndex=traveling_to,
        authorizedDepartures=[],
        unauthorizedDepartures=[],
        status=str(state.status.value),
        taskType = task_type
    )
