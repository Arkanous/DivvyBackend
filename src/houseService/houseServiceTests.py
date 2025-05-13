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

from flask import jsonify
from app import app

# Bad practice but tests won't work without it because Python Modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from userService.user_utils import get_user 
# Lines needed for Aiden's local version
# from src.houseService.house_routes import (house_bp, create_house, create_house_route, get_house_route, get_houses_by_user_route, add_member_to_house_route)
# from src.houseService.house_utils import (

# Lines needed for Tony's local version
from houseService.house_routes import (house_bp, create_house, create_house_route, get_house_route, get_houses_by_user_route, add_member_to_house_route)
from houseService.house_utils import (
    create_house,
    get_house,
    add_member_to_house,
    get_houses_by_user,
)


class TestHouseService(unittest.TestCase):
    """
    Unit tests for the house service (routes and utility functions).
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
        self.get_user_patch = patch('userService.user_utils.get_user', self.mock_get_user)
        self.get_user_patch.start()

    def tearDown(self):
        """
        Clean up mocks.
        """
        self.initialize_app_patch.stop()
        self.firestore_client_patch.stop()
        self.auth_patch.stop()
        self.get_user_patch.stop()

    def test_create_house_success(self):
        with app.app_context():
            """
            Test successful creation of a house.
            """
            self.mock_document.id = 'new_house_id'
            result = create_house(self.mock_db, {
                'id': 'new_house_id', 
                'name': 'Test House',
                'members': ['user123'],
                'dateCreated': firestore.SERVER_TIMESTAMP,
                'imageID': 'abc123',
                'joinCode': 'meaningless'
            })
            self.assertEqual(result, 'new_house_id')
            self.mock_collection.document.assert_called_once()
            self.mock_document.set.assert_called_once_with({
                'id': 'new_house_id',
                'name': 'Test House',
                'members': ['user123'],
                'dateCreated': firestore.SERVER_TIMESTAMP,
                'imageID': 'abc123',
                'joinCode': 'meaningless'
            })

    def test_create_house_failure(self):
        with app.app_context():
            """
            Test failure to create a house.
            """
            self.mock_document.set.side_effect = Exception('Failed to create house')
            result = create_house(self.mock_db, {'id': 'exid'})
            self.assertIsNone(result)

    def test_get_house_success(self):
        with app.app_context():
            """
            Test successful retrieval of a house.
            """
            self.mock_document_snapshot.exists = True
            self.mock_document_snapshot.to_dict.return_value = {'name': 'Test House', 'members': ['user123']}
            result = get_house(self.mock_db, 'house123')
            self.assertEqual(result, {'name': 'Test House', 'members': ['user123']})
            self.mock_collection.document.assert_called_once_with('house123')
            self.mock_document.get.assert_called_once()

    def test_get_house_not_found(self):
        """
        Test retrieval of a non-existent house.
        """
        self.mock_document_snapshot.exists = False
        result = get_house(self.mock_db, 'house123')
        self.assertIsNone(result)

    def test_get_house_failure(self):
        """
        Test failure to retrieve a house due to an exception.
        """
        self.mock_document.get.side_effect = Exception('Failed to get house')
        result = get_house(self.mock_db, 'house123')
        self.assertIsNone(result)

    def test_add_member_to_house_success(self):
        """
        Test successfully adding a member to a house.
        """
        result = add_member_to_house(self.mock_db, 'house123', 'user456')
        self.assertTrue(result)
        self.mock_collection.document.assert_called_once_with('house123')
        self.mock_document.update.assert_called_once_with({'members': firestore.ArrayUnion(['user456'])})

    def test_add_member_to_house_failure(self):
        """
        Test failure to add a member to a house due to an exception.
        """
        self.mock_document.update.side_effect = Exception('Failed to add member')
        result = add_member_to_house(self.mock_db, 'house123', 'user456')
        self.assertFalse(result)

    def test_get_houses_by_user_success(self):
        """
        Test getting houses by user id
        """
        mock_query = MagicMock()
        self.mock_collection.where.return_value = mock_query
        mock_query_result = [
            MagicMock(to_dict=lambda: {"house_name": "House1"}),
            MagicMock(to_dict=lambda: {"house_name": "House2"}),
        ]
        mock_query.get.return_value = mock_query_result

        result = get_houses_by_user(self.mock_db, "user1")

        self.assertEqual(result, [{"house_name": "House1"}, {"house_name": "House2"}])
        self.mock_collection.where.assert_called_once_with('members', 'array_contains', 'user1')
        mock_query.get.assert_called_once()

    def test_get_houses_by_user_exception(self):
        """
        Test get_houses_by_user raises an exception
        """
        self.mock_collection.where.side_effect = Exception("Failed to get houses")
        result = get_houses_by_user(self.mock_db, "user1")
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
