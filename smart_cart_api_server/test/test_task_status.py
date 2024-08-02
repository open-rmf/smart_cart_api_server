import json
import unittest
from smart_cart_api_server.controllers.task_status import parse_task_status
from smart_cart_api_server.models.task_status import TaskDestination


class TestDataSummary(unittest.TestCase):
    def test_parse_completed_task_status(self):
        test_string = {
            'active': 2,
            'assigned_to':
            {
                'group': 'mir_mc_cssd',
                'name': 'cssdmir001'
            },
            'booking':
            {
                'id': 'compose.dispatch-16',
                'unix_millis_earliest_start_time': 0,
                'labels': [
                    '{\"description\":{\"task_type\":\"single-pickup-multi-dropoff\"}}'
                ]
            },
            'category': 'rmf_milkrun_delivery',
            'completed': [1, 2],
            'detail': '',
            'estimate_millis': 0,
            'original_estimate_millis': 60000,
            'pending': [],
            'phases': {
                '1': {'category': 'Sequence', 'detail': '[{"category":"Go to [place:MB_B1_Part_A_Entry]","detail":"Moving the robot from [place:MC_CSSD_Charger_1] to [place:MB_B1_Part_A_Entry]"}]', 'estimate_millis': 4, 'events': {'0': {'deps': [1], 'detail': '', 'id': 0, 'name': 'Sequence', 'status': 'completed'},
                    '1': {'deps': [2], 'detail': 'Moving the robot from [place:MC_CSSD_Charger_1] to [place:MB_B1_Part_A_Entry]', 'id': 1, 'name': 'Go to [place:MB_B1_Part_A_Entry]', 'status': 'completed'},
                    '2': {'deps': [], 'detail': '', 'id': 2, 'name': 'Move to [place:MB_B1_Part_A_Entry] < 181.669 -59.4866  -1.5708> through 3 points', 'status': 'completed'}}, 'final_event_id': 0, 'id': 1, 'original_estimate_millis': 53450, 'unix_millis_finish_time': 1949330, 'unix_millis_start_time': 1894190},
                '2': {'category': 'Sequence', 'detail': '[{"category":"Perform action","detail":"Performing action wait_until at waypoint [[place:MB_B1_Part_A_Entry]]"}]', 'estimate_millis': 50200, 'events': {'0': {'deps': [1], 'detail': '', 'id': 0, 'name': 'Sequence', 'status': 'completed'},
                                                                                                                                                                                                                 '1': {'deps': [], 'detail': 'Performing action wait_until at waypoint [[place:MB_B1_Part_A_Entry]]', 'id': 1, 'name': 'Perform action', 'status': 'completed'}},
                'final_event_id': 0, 'id': 2, 'original_estimate_millis': 60000, 'unix_millis_finish_time': 1959130, 'unix_millis_start_time': 1949330
                    }
                },
                'status': 'completed',
                'unix_millis_finish_time': 1959130,
                'unix_millis_start_time': 1894210
            }
        task_status = parse_task_status(json.dumps([test_string]))
        self.assertEqual(task_status.authorizedDepartures, [])
        self.assertEqual(task_status.destinations, []) # Only 1 end location
        self.assertEqual(task_status.cartId, "cssdmir001")
        self.assertEqual(task_status.status, "completed")
        self.assertEqual(task_status.currentLocationIndex, None)
        self.assertEqual(task_status.travellingToIndex, None)

    def test_parse_underway_last_item_task_status(self):
        test_string = {'active': 2, 'assigned_to': {'group': 'mir_mc_cssd', 'name': 'cssdmir001'}, 'booking': {'id': 'compose.dispatch-16', 'unix_millis_earliest_start_time': 0, 'labels': ['{\"description\":{\"task_type\":\"single-pickup-multi-dropoff\"}}']}, 'category': 'rmf_milkrun_delivery', 'completed': [1], 'detail': '', 'estimate_millis': 50660, 'original_estimate_millis': 60000, 'pending': [], 'phases': {'1': {'category': 'Sequence', 'detail': '[{"category":"Go to [place:MB_B1_Part_A_Entry]","detail":"Moving the robot from [place:MC_CSSD_Charger_1] to [place:MB_B1_Part_A_Entry]"}]', 'estimate_millis': 4, 'events': {'0': {'deps': [1], 'detail': '', 'id': 0, 'name': 'Sequence', 'status': 'completed'}, '1': {'deps': [2], 'detail': 'Moving the robot from [place:MC_CSSD_Charger_1] to [place:MB_B1_Part_A_Entry]', 'id': 1, 'name': 'Go to [place:MB_B1_Part_A_Entry]', 'status': 'completed'}, '2': {'deps': [], 'detail': '', 'id': 2, 'name': 'Move to [place:MB_B1_Part_A_Entry] < 181.669 -59.4866  -1.5708> through 3 points', 'status': 'completed'}}, 'final_event_id': 0, 'id': 1, 'original_estimate_millis': 53450, 'unix_millis_finish_time': 1949330, 'unix_millis_start_time': 1894190}, '2': {'category': 'Sequence', 'detail': '[{"category":"Perform action","detail":"Performing action wait_until at waypoint [[place:MB_B1_Part_A_Entry]]"}]', 'estimate_millis': 50660, 'events': {'0': {'deps': [1], 'detail': '', 'id': 0, 'name': 'Sequence', 'status': 'underway'}, '1': {'deps': [], 'detail': 'Performing action wait_until at waypoint [[place:MB_B1_Part_A_Entry]]', 'id': 1, 'name': 'Perform action', 'status': 'underway'}}, 'final_event_id': 0, 'id': 2, 'original_estimate_millis': 60000, 'unix_millis_start_time': 1949330}}, 'status': 'underway', 'unix_millis_finish_time': 2009330, 'unix_millis_start_time': 1894210}
        task_status = parse_task_status(json.dumps([test_string]))
        self.assertEqual(task_status.authorizedDepartures, [])
        self.assertEqual(task_status.destinations, [TaskDestination(name='MB_B1_Part_A_Entry', compartment=None, action='pickup', staging=True)])
        self.assertEqual(task_status.cartId, "cssdmir001")
        self.assertEqual(task_status.status, "underway")
        self.assertEqual(task_status.currentLocationIndex, 0)
        self.assertEqual(task_status.travellingToIndex, None)

    def test_parse_underway_travelling_task_status(self):
        test_string = {'active': 1, 'assigned_to': {'group': 'mir_mc_cssd', 'name': 'cssdmir001'}, 'booking': {'id': 'compose.dispatch-16', 'unix_millis_earliest_start_time': 0, 'labels': ['{\"description\":{\"task_type\":\"single-pickup-multi-dropoff\"}}']}, 'category': 'rmf_milkrun_delivery', 'completed': [], 'detail': '', 'estimate_millis': 109421, 'original_estimate_millis': 60000, 'pending': [2], 'phases': {'1': {'category': 'Sequence', 'detail': '[{"category":"Go to [place:MB_B1_Part_A_Entry]","detail":"Moving the robot from [place:MC_CSSD_Charger_1] to [place:MB_B1_Part_A_Entry]"}]', 'estimate_millis': 49421, 'events': {'0': {'deps': [1], 'detail': '', 'id': 0, 'name': 'Sequence', 'status': 'underway'}, '1': {'deps': [2], 'detail': 'Moving the robot from [place:MC_CSSD_Charger_1] to [place:MB_B1_Part_A_Entry]', 'id': 1, 'name': 'Go to [place:MB_B1_Part_A_Entry]', 'status': 'underway'}, '2': {'deps': [], 'detail': '', 'id': 2, 'name': 'Move to [place:MB_B1_Part_A_Entry] < 181.669 -59.4866  -1.5708> through 3 points', 'status': 'underway'}}, 'final_event_id': 0, 'id': 1, 'original_estimate_millis': 53450, 'unix_millis_start_time': 1894190}, '2': {'category': 'Sequence', 'detail': '[{"category":"Perform action","detail":"Performing action wait_until at waypoint [[place:MB_B1_Part_A_Entry]]"}]', 'estimate_millis': 60000, 'id': 2}}, 'status': 'underway', 'unix_millis_finish_time': 2004631, 'unix_millis_start_time': 1894210}
        task_status = parse_task_status(json.dumps([test_string]))
        self.assertEqual(task_status.authorizedDepartures, [])
        self.assertEqual(task_status.destinations, [TaskDestination(name='MB_B1_Part_A_Entry', compartment=None, action='pickup', staging=True)])
        self.assertEqual(task_status.cartId, "cssdmir001")
        self.assertEqual(task_status.status, "underway")
        self.assertEqual(task_status.currentLocationIndex, None)
        self.assertEqual(task_status.travellingToIndex, 0)

    def test_parse_queued_travelling_task_status(self):
        test_string = {'assigned_to': {'group': 'mir_mc_cssd', 'name': 'cssdmir001'}, 'booking': {'id': 'compose.dispatch-16', 'unix_millis_earliest_start_time': 0, 'labels': ['{\"description\":{\"task_type\":\"single-pickup-multi-dropoff\"}}']}, 'category': 'rmf_milkrun_delivery', 'detail': '', 'original_estimate_millis': 108086, 'status': 'queued', 'unix_millis_finish_time': 2000256, 'unix_millis_start_time': 1892170}
        task_status = parse_task_status(json.dumps([test_string]))
        self.assertEqual(task_status.authorizedDepartures, [])
        self.assertEqual(task_status.destinations, [])
        self.assertEqual(task_status.cartId, "cssdmir001")
        self.assertEqual(task_status.status, "queued")
        self.assertEqual(task_status.currentLocationIndex, None)
        self.assertEqual(task_status.travellingToIndex, None)
