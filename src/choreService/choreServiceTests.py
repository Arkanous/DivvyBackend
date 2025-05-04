import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

from choreService.chore_routes import (chore_bp, create_chore_route, create_chore, get_chore_instances_by_user_route, generate_chore_instances_route)
from choreService.chore_utils import (
    create_chore,
    generate_chore_instances,
    get_chore_instances_by_user,
    get_chore_instance,
    update_chore_instance,
    get_chores_by_house,
)


class TestChoreService(unittest.TestCase):
    """
    Unit tests for the chore service (routes and utility functions).
    """

    def setUp(self):
        """
        Set up mocks for Firebase Admin SDK and Firestore.
        """
        self.initialize_app_patch = patch('firebase_admin.initialize_app')
        self.mock_initialize_app = self.initialize_app_patch.start()

        self.mock_firestore_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_firestore_client.return_value = self.mock_db

        self.firestore_client_patch = patch('google.cloud.firestore.Client')
        self.firestore_client_patch.start().return_value = self.mock_firestore_client

        self.mock_collection = MagicMock()
        self.mock_document = MagicMock()
        self.mock_db.collection.return_value = self.mock_collection
        self.mock_collection.document.return_value = self.mock_document

        self.mock_document_snapshot = MagicMock()
        self.mock_document.get.return_value = self.mock_document_snapshot

        self.app = MagicMock()
        self.app.config = {'FIRESTORE_DB': self.mock_db}
        self.request_context = MagicMock()

        self.mock_auth = MagicMock()
        self.auth_patch = patch('firebase_admin.auth', self.mock_auth)
        self.auth_patch.start()

        self.mock_get_user = MagicMock()
        self.get_user_patch = patch('choreService.chore_utils.get_user', self.mock_get_user)
        self.get_user_patch.start()

    def tearDown(self):
        """
        Clean up mocks.
        """
        self.initialize_app_patch.stop()
        self.firestore_client_patch.stop()
        self.get_user_patch.stop()

    def test_create_chore_success(self):
        """
        Test successful creation of a chore.
        """
        self.mock_document.id = 'new_chore_id'
        result = create_chore(
            self.mock_db,
            'house123',
            ' уборка', # ngl I wonder what Firebase can and can't store
            ['user123', 'user456'],
            'weekly',
            {'day_of_week': 0},
            'user123',
            'subgroup789',
        )
        self.assertEqual(result, 'new_chore_id')
        self.mock_collection.document.assert_called_once()
        self.mock_document.set.assert_called_once_with({
            'house_id': 'house123',
            'description': ' уборка',
            'assigned_to': ['user123', 'user456'],
            'schedule_type': 'weekly',
            'schedule_data': {'day_of_week': 0},
            'created_at': firestore.SERVER_TIMESTAMP,
            'created_by': 'user123',
            'subgroup_id': 'subgroup789',
            'name': ' уборка',
            'is_active': True,
        })

    def test_create_chore_failure(self):
        """
        Test failure to create a chore.
        """
        self.mock_document.set.side_effect = Exception('Failed to create chore')
        result = create_chore(
            self.mock_db,
            'house123',
            ' уборка',
            ['user123', 'user456'],
            'weekly',
            {'day_of_week': 0},
            'user123',
            'subgroup789',
        )
        self.assertIsNone(result)

    def test_generate_chore_instances_success(self):
        """
        Test successful generation of chore instances.
        """
        self.mock_document_snapshot.exists = True
        self.mock_document_snapshot.to_dict.return_value = {
            'schedule_type': 'weekly',
            'schedule_data': {'day_of_week': 0},
            'assigned_to': ['user123', 'user456'],
        }
        self.mock_document.id = 'instance1'
        self.mock_collection.document.return_value = self.mock_document

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        result = generate_chore_instances(self.mock_db, 'chore123', start_date, end_date)
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, str)

    def test_generate_chore_instances_chore_not_found(self):
        """
        Test when the chore is not found.
        """
        self.mock_document_snapshot.exists = False
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        result = generate_chore_instances(self.mock_db, 'chore123', start_date, end_date)
        self.assertEqual(result, [])

    def test_generate_chore_instances_invalid_schedule_type(self):
        """
        Test with an invalid schedule type.
        """
        self.mock_document_snapshot.exists = True
        self.mock_document_snapshot.to_dict.return_value = {
            'schedule_type': 'invalid',
            'schedule_data': {},
            'assigned_to': ['user123']
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        result = generate_chore_instances(self.mock_db, 'chore123', start_date, end_date)
        self.assertEqual(result, [])

    def test_get_chore_instances_by_user_success(self):
        """
        Test successful retrieval of chore instances for a user.
        """
        mock_query = MagicMock()
        self.mock_collection.where.return_value = mock_query
        mock_query_result = [
            MagicMock(to_dict=lambda: {'chore_id': 'chore1', 'date': datetime(2024, 1, 15)}),
            MagicMock(to_dict=lambda: {'chore_id': 'chore2', 'date': datetime(2024, 1, 20)}),
        ]
        mock_query.get.return_value = mock_query_result
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        result = get_chore_instances_by_user(self.mock_db, 'user123', start_date, end_date)
        self.assertEqual(result, [
            {'chore_id': 'chore1', 'date': datetime(2024, 1, 15)},
            {'chore_id': 'chore2', 'date': datetime(2024, 1, 20)},
        ])

    def test_get_chore_instances_by_user_no_instances(self):
        """
        Test when there are no chore instances for the user in the given range.
        """
        mock_query = MagicMock()
        self.mock_collection.where.return_value = mock_query
        mock_query.get.return_value = []
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        result = get_chore_instances_by_user(self.mock_db, 'user123', start_date, end_date)
        self.assertEqual(result, [])

    def test_get_chore_instances_by_user_exception(self):
        """
        Test the case where an exception is raised during the query.
        """
        mock_query = MagicMock()
        self.mock_collection.where.return_value = mock_query
        mock_query.get.side_effect = Exception("Simulated error")
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        result = get_chore_instances_by_user(self.mock_db, 'user123', start_date, end_date)
        self.assertEqual(result, [])

    def test_get_chore_instance_success(self):
        """
        Test successful retrieval of a chore instance.
        """
        self.mock_document_snapshot.exists = True
        self.mock_document_snapshot.to_dict.return_value = {'chore_id': 'chore123', 'date': datetime(2024, 1, 15)}
        result = get_chore_instance(self.mock_db, 'instance123')
        self.assertEqual(result, {'chore_id': 'chore123', 'date': datetime(2024, 1, 15)})

    def test_get_chore_instance_not_found(self):
        """
        Test when the chore instance is not found.
        """
        self.mock_document_snapshot.exists = False
        result = get_chore_instance(self.mock_db, 'instance123')
        self.assertIsNone(result)

    def test_get_chore_instance_exception(self):
        """
        Test the case where an exception is raised.
        """
        self.mock_document.get.side_effect = Exception("Simulated error")
        result = get_chore_instance(self.mock_db, 'instance123')
        self.assertIsNone(result)

    def test_update_chore_instance_success(self):
        """
        Test successful update of a chore instance.
        """
        result = update_chore_instance(self.mock_db, 'instance123', {'completed': True})
        self.assertTrue(result)
        self.mock_collection.document.assert_called_once_with('instance123')
        self.mock_document.update.assert_called_once_with({'completed': True})

    def test_update_chore_instance_exception(self):
        """
        Test the case where an exception is raised during the update.
        """
        self.mock_document.update.side_effect = Exception("Simulated error")
        result = update_chore_instance(self.mock_db, 'instance123', {'completed': True})
        self.assertFalse(result)

    def test_get_chores_by_house_success(self):
        """
        Test successful retrieval of chores for a house.
        """
        mock_query = MagicMock()
        self.mock_collection.where.return_value = mock_query
        mock_query_result = [
            MagicMock(to_dict=lambda: {'chore_id': 'chore1', 'description': ' уборка'}),
            MagicMock(to_dict=lambda: {'chore_id': 'chore2', 'description': ' готовка'}),
        ]
        mock_query.get.return_value = mock_query_result
        result = get_chores_by_house(self.mock_db, 'house123')
        self.assertEqual(result, [
            {'chore_id': 'chore1', 'description': ' уборка'},
            {'chore_id': 'chore2', 'description': ' готовка'},
        ])
        self.mock_collection.where.assert_called_once_with('house_id', '==', 'house123')

    def test_get_chores_by_house_no_chores(self):
        """
        Test when there are no chores for the house.
        """
        mock_query = MagicMock()
        self.mock_collection.where.return_value = mock_query
        mock_query.get.return_value = []
        result = get_chores_by_house(self.mock_db, 'house123')
        self.assertEqual(result, [])

    def test_get_chores_by_house_exception(self):
        """
        Test the case where an exception is raised.
        """
        mock_query = MagicMock()
        self.mock_collection.where.return_value = mock_query
        mock_query.get.side_effect = Exception("Simulated error")
        result = get_chores_by_house(self.mock_db, 'house123')
        self.assertEqual(result, [])

    def test_create_chore_route_success(self):
        """
        Test successful creation of a chore via the route.
        """
        self.mock_document.id = 'new_chore_id'
        self.mock_get_user.return_value = {'user_id': 'user123'}

        with self.app.test_request_context(
            '/chores',
            method='POST',
            json={
                'house_id': 'house123',
                'description': ' уборка',
                'assigned_to': ['user123', 'user456'],
                'schedule_type': 'weekly',
                'schedule_data': {'day_of_week': 0},
                'created_by': 'user123',
                'subgroup_id': 'subgroup789',
            },
        ):
            response = create_chore_route()
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.get_json(), {'message': 'Chore created successfully', 'chore_id': 'new_chore_id'})
            self.mock_collection.document.assert_called_once()
            self.mock_document.set.assert_called_once_with({
                'house_id': 'house123',
                'description': ' уборка',
                'assigned_to': ['user123', 'user456'],
                'schedule_type': 'weekly',
                'schedule_data': {'day_of_week': 0},
                'created_at': firestore.SERVER_TIMESTAMP,
                'created_by': 'user123',
                'subgroup_id': 'subgroup789',
                'name': ' уборка',
                'is_active': True
            })

    def test_create_chore_route_missing_data(self):
        """
        Test creating a chore with missing data.
        """
        with self.app.test_request_context(
            '/chores',
            method='POST',
            json={
                'house_id': 'house123',
                'description': ' уборка',
                'assigned_to': ['user123', 'user456'],
                'schedule_type': 'weekly',
            },
        ):
            response = create_chore_route()
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.get_json(),
                {'error': 'House ID, description, assigned_to, schedule_type, and created_by are required'},
            )
            self.mock_collection.document.assert_not_called()

    def test_create_chore_route_invalid_user(self):
        """
        Test creating a chore with an invalid assigned_to user ID.
        """
        self.mock_get_user.return_value = None
        with self.app.test_request_context(
            '/chores',
            method='POST',
            json={
                'house_id': 'house123',
                'description': ' уборка',
                'assigned_to': ['invalid_user_id'],
                'schedule_type': 'weekly',
                'schedule_data': {'day_of_week': 0},
                'created_by': 'user123',
                'subgroup_id': 'subgroup789'
            },
        ):
            response = create_chore_route()
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json(), {'error': 'Invalid user ID: invalid_user_id'})
            self.mock_collection.document.assert_not_called()

    def test_create_chore_route_exception(self):
        """
        Test exception during chore creation.
        """
        self.mock_document.set.side_effect = Exception('Simulated error')
        self.mock_get_user.return_value = {'user_id': 'user123'}
        with self.app.test_request_context(
            '/chores',
            method='POST',
            json={
                'house_id': 'house123',
                'description': ' уборка',
                'assigned_to': ['user123', 'user456'],
                'schedule_type': 'weekly',
                'schedule_data': {'day_of_week': 0},
                'created_by': 'user123',
                'subgroup_id': 'subgroup789'
            },
        ):
            response = create_chore_route()
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.get_json(), {'error': 'Error creating chore: Simulated error'})

    def test_generate_chore_instances_route_success(self):
        """
        Test successful generation of chore instances via the route.
        """
        # Set up mocks
        self.mock_document_snapshot.exists = True
        self.mock_document_snapshot.to_dict.return_value = {
            'schedule_type': 'daily',
            'schedule_data': {},
            'assigned_to': ['user1', 'user2']
        }
        self.mock_document.id = 'instance1'

        with self.app.test_request_context(
            '/chores/chore123/instances',
            method='POST',
            json={'start_date': '2024-01-01', 'end_date': '2024-01-05'},
        ):
            response = generate_chore_instances_route('chore123')
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.get_json(), {'message': 'Chore instances generated successfully', 'instance_ids': ['instance1']})

    def test_generate_chore_instances_route_missing_data(self):
        """
        Test generating chore instances with missing data.
        """
        with self.app.test_request_context(
            '/chores/chore123/instances',
            method='POST',
            json={'start_date': '2024-01-01'},  # Missing end_date
        ):
            response = generate_chore_instances_route('chore123')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json(), {'error': 'Start date and end date are required'})

    def test_generate_chore_instances_route_invalid_date_format(self):
        """
        Test generating chore instances with an invalid date format.
        """
        with self.app.test_request_context(
            '/chores/chore123/instances',
            method='POST',
            json={'start_date': '01-01-2024', 'end_date': '05-01-2024'},
        ):
            response = generate_chore_instances_route('chore123')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json(), {'error': 'Invalid date format.  Use %Y-%m-%d'})

    def test_generate_chore_instances_route_exception(self):
        """
        Test exception during chore instance generation.
        """
        self.mock_document_snapshot.exists = True
        self.mock_document_snapshot.to_dict.return_value = {
            'schedule_type': 'daily',
            'schedule_data': {},
            'assigned_to': ['user1']
        }
        self.mock_collection.document.side_effect = Exception('Simulated error')
        with self.app.test_request_context(
            '/chores/chore123/instances',
            method='POST',
            json={'start_date': '2024-01-01', 'end_date': '2024-01-05'},
        ):
            response = generate_chore_instances_route('chore123')
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.get_json(), {'error': 'Error generating chore instances: Simulated error'})

    def test_get_chore_instances_by_user_route_success(self):
        """
        Test successful retrieval of chore instances for a user via the route.
        """
        mock_get_chore_instances_by_user_result = [
            {'chore_id': 'chore1', 'date': datetime(2024, 1, 15)},
            {'chore_id': 'chore2', 'date': datetime(2024, 1, 20)},
        ]
        with patch('utils.chore_utils.get_chore_instances_by_user', return_value=mock_get_chore_instances_by_user_result):
            with self.app.test_request_context('/chores/user/user123/instances?start_date=2024-01-01&end_date=2024-01-31', method='GET'):
                response = get_chore_instances_by_user_route('user123')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), [
                    {'chore_id': 'chore1', 'date': datetime(2024, 1, 15)},
                    {'chore_id': 'chore2', 'date': datetime(2024, 1, 20)},
                ])

    def test_get_chore_instances_by_user_route_missing_data(self):
        """
        Test retrieval of chore instances with missing date parameters.
        """
        with self.app.test_request_context('/chores/user/user123/instances?start_date=2024-01-01', method='GET'):
            response = get_chore_instances_by_user_route('user123')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json(), {'error': 'Start date and end date are required'})

    def test_get_chore_instances_by_user_route_invalid_date_format(self):
        """
        Test retrieval of chore instances with invalid date formats.
        """
        with self.app.test_request_context('/chores/user/user123/instances?start_date=01-01-2024&end_date=31-01-2024', method='GET'):
            response = get_chore_instances_by_user_route('user123')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json(), {'error': 'Invalid date format.  Use %Y-%m-%d'})
