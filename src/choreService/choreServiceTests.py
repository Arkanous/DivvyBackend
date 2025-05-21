import sys 
# Adding userService and utils
sys.path.append('../')
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
import sys
import os

# Bad practice but tests won't work without it because Python Modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from userService.user_utils import get_user
from choreService.chore_utils import (
    upsert_chore,
    upsert_chore_instance,
    get_chore_instances_by_user,
    get_chore_instance,
    update_chore_instance,
    get_chores_by_house,
)
from flask import Flask


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
        
        self.mock_subcollection = MagicMock()
        self.mock_subdocument = MagicMock()
        self.mock_document.collection.return_value = self.mock_subcollection
        self.mock_subcollection.document.return_value = self.mock_subdocument

        self.mock_document_snapshot = MagicMock()
        self.mock_document.get.return_value = self.mock_document_snapshot

        self.app = Flask(__name__)
        self.app.config['FIRESTORE_DB'] = self.mock_db
        self.app_context = self.app.app_context() 
        self.app_context.push()
        self.request_context = MagicMock()

        self.mock_auth = MagicMock()
        self.auth_patch = patch('firebase_admin.auth', self.mock_auth)
        self.auth_patch.start()

        self.mock_get_user = MagicMock()
        self.get_user_patch = patch('src.userService.user_utils.get_user', self.mock_get_user)
        self.get_user_patch.start()

    def tearDown(self):
        """
        Clean up mocks.
        """
        self.initialize_app_patch.stop()
        self.firestore_client_patch.stop()
        self.get_user_patch.stop()

    def test_upsert_chore_success(self):
        """
        Test successful creation/update of a chore
        """
        result = upsert_chore(self.mock_db, 
                              {'id': 'fakeChoreID',
                               'assignees': [
                                    'asdnzxvcie'],
                                'description': 'A useful desc.',
                                'emoji': '<emojiHere>',
                                'frequencyDays': ['3','7'],
                                'frequencyPattern': 'weekly',
                                'name': 'choreName',
                                'startDate': 'Thu, 01 May 2025 07:00:00 GMT'},
                              'fakeHouseID')
        self.assertDictEqual(result.get_json(), {'id': 'fakeChoreID'})
        self.mock_db.collection.assert_called_once_with('houses')
        self.mock_collection.document.assert_called_once_with('fakeHouseID')
        self.mock_document.collection.assert_called_once_with('chores')
        self.mock_subcollection.document.assert_called_once_with('fakeChoreID')
        self.mock_subdocument.set.assert_called_once_with({'id': 'fakeChoreID',
                                                            'assignees': [
                                                                'asdnzxvcie'],
                                                            'description': 'A useful desc.',
                                                            'emoji': '<emojiHere>',
                                                            'frequencyDays': ['3','7'],
                                                            'frequencyPattern': 'weekly',
                                                            'name': 'choreName',
                                                            'startDate': 'Thu, 01 May 2025 07:00:00 GMT'})


    def test_upsert_chore_failure(self):
        """
        Test failure to create/update a chore
        """
        self.mock_subdocument.set.side_effect = Exception('Failed to create chore')
        result = upsert_chore(self.mock_db, 
                              {'id': 'fakeChoreID',
                               'assignees': [
                                    'asdnzxvcie'],
                                'description': 'A useful desc.',
                                'emoji': '<emojiHere>',
                                'frequencyDays': ['3','7'],
                                'frequencyPattern': 'weekly',
                                'name': 'choreName',
                                'startDate': 'Thu, 01 May 2025 07:00:00 GMT'},
                              'fakeHouseID')
        self.assertDictEqual(result[0].get_json(), {'error': 'Could not upsert chore'})
        self.assertEqual(result[1], 500)
    
    def test_upsert_chore_instance_success(self):
        """
        Test successful creation/upsert of a chore instance
        """
        result = upsert_chore(self.mock_db, 
                              {'id': 'fakeChoreInstID',
                                'assignee': 'asdnzxvcie',
                                'choreID': 'zxcvoiwen',
                                'dueDate': 'Thu, 01 May 2025 07:00:00 GMT',
                                'isDone': False},
                              'fakeHouseID')
        self.assertDictEqual(result.get_json(), {'id': 'fakeChoreInstID'})
        self.mock_db.collection.assert_called_once_with('houses')
        self.mock_collection.document.assert_called_once_with('fakeHouseID')
        self.mock_document.collection.assert_called_once_with('chores')
        self.mock_subcollection.document.assert_called_once_with('fakeChoreInstID')
        self.mock_subdocument.set.assert_called_once_with({'id': 'fakeChoreInstID',
                                                            'assignee': 'asdnzxvcie',
                                                            'choreID': 'zxcvoiwen',
                                                            'dueDate': 'Thu, 01 May 2025 07:00:00 GMT',
                                                            'isDone': False})


    def test_upsert_chore_instance_failure(self):
        """
        Test failure to create/update a chore instance
        """
        self.mock_subdocument.set.side_effect = Exception('Failed to create chore instance')
        result = upsert_chore_instance(self.mock_db, 
                              {'id': 'fakeChoreInstID',
                                'assignee': 'asdnzxvcie',
                                'choreID': 'zxcvoiwen',
                                'dueDate': 'Thu, 01 May 2025 07:00:00 GMT',
                                'isDone': False},
                              'fakeHouseID')
        self.assertDictEqual(result[0].get_json(), {'error': 'Could not upsert chore instance'})
        self.assertEqual(result[1], 500)
    
    


    # def test_generate_chore_instances_success(self):
    #     """
    #     Test successful generation of chore instances.
    #     """
    #     self.mock_document_snapshot.exists = True
    #     self.mock_document_snapshot.to_dict.return_value = {
    #         'schedule_type': 'weekly',
    #         'schedule_data': {'day_of_week': 0},
    #         'assigned_to': ['user123', 'user456'],
    #     }
    #     self.mock_document.id = 'instance1'
    #     self.mock_collection.document.return_value = self.mock_document

    #     start_date = datetime(2024, 1, 1)
    #     end_date = datetime(2024, 1, 31)
    #     result = generate_chore_instances(self.mock_db, 'chore123', start_date, end_date)
    #     self.assertIsInstance(result, list)
    #     for item in result:
    #         self.assertIsInstance(item, str)

    # def test_generate_chore_instances_chore_not_found(self):
    #     """
    #     Test when the chore is not found.
    #     """
    #     self.mock_document_snapshot.exists = False
    #     start_date = datetime(2024, 1, 1)
    #     end_date = datetime(2024, 1, 31)
    #     result = generate_chore_instances(self.mock_db, 'chore123', start_date, end_date)
    #     self.assertEqual(result, [])

    # def test_generate_chore_instances_invalid_schedule_type(self):
    #     """
    #     Test with an invalid schedule type.
    #     """
    #     self.mock_document_snapshot.exists = True
    #     self.mock_document_snapshot.to_dict.return_value = {
    #         'schedule_type': 'invalid',
    #         'schedule_data': {},
    #         'assigned_to': ['user123']
    #     }
    #     start_date = datetime(2024, 1, 1)
    #     end_date = datetime(2024, 1, 31)
    #     result = generate_chore_instances(self.mock_db, 'chore123', start_date, end_date)
    #     self.assertEqual(result, [])

    # TODO: Currently non-functional, needs to be fixed after get_chore_instances_by_user()
    # is updated to fit new schema.
    # def test_get_chore_instances_by_user_success(self):
    #     """
    #     Test successful retrieval of chore instances for a user.
    #     """
    #     mock_query = MagicMock()
    #     self.mock_collection.where.return_value = mock_query
    #     mock_query_result = [
    #         MagicMock(to_dict=lambda: {'chore_id': 'chore1', 'date': datetime(2024, 1, 15)}),
    #         MagicMock(to_dict=lambda: {'chore_id': 'chore2', 'date': datetime(2024, 1, 20)}),
    #     ]
    #     mock_query.get.return_value = mock_query_result
    #     start_date = datetime(2024, 1, 1)
    #     end_date = datetime(2024, 1, 31)
    #     result = get_chore_instances_by_user(self.mock_db, 'user123', start_date, end_date)
    #     self.assertEqual(result, [
    #         {'chore_id': 'chore1', 'date': datetime(2024, 1, 15)},
    #         {'chore_id': 'chore2', 'date': datetime(2024, 1, 20)},
    #     ])

    # def test_get_chore_instances_by_user_no_instances(self):
    #     """
    #     Test when there are no chore instances for the user in the given range.
    #     """
    #     mock_query = MagicMock()
    #     self.mock_collection.where.return_value = mock_query
    #     mock_query.get.return_value = []
    #     start_date = datetime(2024, 1, 1)
    #     end_date = datetime(2024, 1, 31)
    #     result = get_chore_instances_by_user(self.mock_db, 'user123', start_date, end_date)
    #     self.assertEqual(result, [])

    # def test_get_chore_instances_by_user_exception(self):
    #     """
    #     Test the case where an exception is raised during the query.
    #     """
    #     mock_query = MagicMock()
    #     self.mock_collection.where.return_value = mock_query
    #     mock_query.get.side_effect = Exception("Simulated error")
    #     start_date = datetime(2024, 1, 1)
    #     end_date = datetime(2024, 1, 31)
    #     result = get_chore_instances_by_user(self.mock_db, 'user123', start_date, end_date)
    #     self.assertEqual(result, [])

    # def test_get_chore_instance_success(self):
    #     """
    #     Test successful retrieval of a chore instance.
    #     """
    #     self.mock_document_snapshot.exists = True
    #     self.mock_document_snapshot.to_dict.return_value = {'chore_id': 'chore123', 'date': datetime(2024, 1, 15)}
    #     result = get_chore_instance(self.mock_db, 'instance123')
    #     self.assertEqual(result, {'chore_id': 'chore123', 'date': datetime(2024, 1, 15)})

    # def test_get_chore_instance_not_found(self):
    #     """
    #     Test when the chore instance is not found.
    #     """
    #     self.mock_document_snapshot.exists = False
    #     result = get_chore_instance(self.mock_db, 'instance123')
    #     self.assertIsNone(result)

    # def test_get_chore_instance_exception(self):
    #     """
    #     Test the case where an exception is raised.
    #     """
    #     self.mock_document.get.side_effect = Exception("Simulated error")
    #     result = get_chore_instance(self.mock_db, 'instance123')
    #     self.assertIsNone(result)

    # def test_update_chore_instance_success(self):
    #     """
    #     Test successful update of a chore instance.
    #     """
    #     result = update_chore_instance(self.mock_db, 'instance123', {'completed': True})
    #     self.assertTrue(result)
    #     self.mock_collection.document.assert_called_once_with('instance123')
    #     self.mock_document.update.assert_called_once_with({'completed': True})

    # def test_update_chore_instance_exception(self):
    #     """
    #     Test the case where an exception is raised during the update.
    #     """
    #     self.mock_document.update.side_effect = Exception("Simulated error")
    #     result = update_chore_instance(self.mock_db, 'instance123', {'completed': True})
    #     self.assertFalse(result)

    # def test_get_chores_by_house_success(self):
    #     """
    #     Test successful retrieval of chores for a house.
    #     """
    #     mock_query = MagicMock()
    #     self.mock_collection.where.return_value = mock_query
    #     mock_query_result = [
    #         MagicMock(to_dict=lambda: {'chore_id': 'chore1', 'description': ' уборка'}),
    #         MagicMock(to_dict=lambda: {'chore_id': 'chore2', 'description': ' готовка'}),
    #     ]
    #     mock_query.get.return_value = mock_query_result
    #     result = get_chores_by_house(self.mock_db, 'house123')
    #     self.assertEqual(result, [
    #         {'chore_id': 'chore1', 'description': ' уборка'},
    #         {'chore_id': 'chore2', 'description': ' готовка'},
    #     ])
    #     self.mock_collection.where.assert_called_once_with('house_id', '==', 'house123')

    # def test_get_chores_by_house_no_chores(self):
    #     """
    #     Test when there are no chores for the house.
    #     """
    #     mock_query = MagicMock()
    #     self.mock_collection.where.return_value = mock_query
    #     mock_query.get.return_value = []
    #     result = get_chores_by_house(self.mock_db, 'house123')
    #     self.assertEqual(result, [])

    # def test_get_chores_by_house_exception(self):
    #     """
    #     Test the case where an exception is raised.
    #     """
    #     mock_query = MagicMock()
    #     self.mock_collection.where.return_value = mock_query
    #     mock_query.get.side_effect = Exception("Simulated error")
    #     result = get_chores_by_house(self.mock_db, 'house123')
    #     self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
