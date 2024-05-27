from api_server.models.rmf_api.task_state import TaskState, Status
from smart_cart_api_server.models.task_status import TaskStatus, TaskDestination
import json
import datetime
from parse import parse

def parse_task_status(task_state: str) -> TaskStatus:
    """
    This function parses a task state coming in from a json string into the robots current location.
    Note: This function makes some pretty strong assumptions about the task structure. Namely that:
    - Every "Perform Action" is a pickup/dropoff location
    - All  pickups/drop offs can be gathered by the GoToPlace command.
    """
    tasks = json.loads(task_state)
    state = TaskState.model_validate(tasks[0])

    locations = []
    loc_idxs = {}
    next_loc_idx = {}
    for p in sorted(state.phases.keys()):
        ### LOTS OF MAGIC
        x = json.loads(str(state.phases[p].detail)[6:-1])[0]
        if x["category"] == "Perform action":
            res = parse("Performing action wait_until at waypoint [[place:{place}]]", x["detail"])
            loc_idxs[p] = len(locations)
            locations.append(TaskDestination(
                name=res["place"],
                compartment=None,
                action="dropoff"
            ))
        else:
            next_loc_idx[p] = len(locations)


    current_location = None
    traveling_to = None

    if state.status == Status.underway and state.active is not None:
        #hack
        st = str(state.active)[5:]
        detail = json.loads(str(state.phases[st].detail)[6:-1])[0]
        if detail["category"] == "Perform action":
            current_location = loc_idxs[st]
        else:
            next_idx = next_loc_idx[st]
            if next_idx < len(locations):
                traveling_to = next_idx

    return TaskStatus(
        taskId=state.booking.id,
        dateTime=datetime.datetime.fromtimestamp(
            state.unix_millis_start_time, tz=datetime.timezone.utc),
        robotId=state.assigned_to.name,
        fleetId=state.assigned_to.group,
        cartId=state.assigned_to.name, # For now only use cart_id
        destinations=locations,
        currentLocationIndex=current_location,
        travellingToIndex=traveling_to,
        authorizedDepartures=[],
        unauthorizedDepartures=[],
        status=state.status
    )