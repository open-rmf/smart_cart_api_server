from api_server.models.rmf_api.task_state import TaskState
from smart_cart_api_server.models.task_status import TaskStatus, TaskDestination
import json
import datetime
from parse import parse

def parse_task_status(task_state: str) -> TaskStatus:
    tasks = json.loads(task_state)
    state = TaskState.model_validate(tasks[0])

    locations = []
    loc_idxs = {}
    for p in sorted(state.phases.keys()):
        ### LOTS OF MAGIC
        x = json.loads(str(state.phases[p].detail)[6:-1])[0]
        if x["category"] == "Perform action":
            res = parse("Performing action wait_until at waypoint [[place:{place}]]", x["detail"])
            loc_idxs[len(locations)] = res["place"]
            locations.append(TaskDestination(
                name=res["place"],
                compartment=None,
                action="dropoff"
            ))


    current_location = None
    if state.status == "underway" and state.active is not None:
        #hack
        st = str(state.active)[5:]
        if isinstance(state.phases[st].detail, str) and state.phases[st].detail.startswith("Performing action"):
            current_location =int(st)

    return TaskStatus(
        taskId=state.booking.id,
        dateTime=datetime.datetime.fromtimestamp(
            state.unix_millis_start_time, tz=datetime.timezone.utc),
        robotId=state.assigned_to.name,
        fleetId=state.assigned_to.group,
        cartId=state.assigned_to.name, # For now only use cart_id
        destinations=locations,
        currentLocationIndex=current_location,
        #travellingToIndex=,
        authorizedDepartures=[],
        unauthorizedDepartures=[],
        status=state.status
    )