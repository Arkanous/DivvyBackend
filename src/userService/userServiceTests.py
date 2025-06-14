import unittest
from unittest.mock import MagicMock, patch
import firebase_admin
from firebase_admin import credentials, firestore, auth 
import google.cloud.firestore
from flask import Flask, make_response, jsonify
import sys
import os

# Bad practice but tests won't work without it because Python Modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from userService.user_utils import (get_user, upsert_user)


class TestUserService(unittest.TestCase):
    """
    Unit tests for the user service (routes and utility functions).
    """

    def setUp(self):
        """
        Set up mocks for Firebase Admin SDK, Firestore, and Firebase Auth.
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

        self.app = Flask(__name__)
        self.app.config['FIRESTORE_DB'] = self.mock_db
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.request_context = MagicMock()

        self.mock_auth = MagicMock()
        self.auth_patch = patch('firebase_admin.auth', self.mock_auth)
        self.auth_patch.start()

    def tearDown(self):
        """
        Clean up mocks.
        """
        self.initialize_app_patch.stop()
        self.firestore_client_patch.stop()
        self.auth_patch.stop()

    def test_get_user_success(self):
        """
        Test successful retrieval of a user.
        """
        self.mock_document_snapshot.exists = True
        self.mock_document_snapshot.to_dict.return_value = {'email': 'test@example.com', 'name': 'Test User'}
        result = get_user(self.mock_db, 'user123')
        self.assertDictEqual(result, {'email': 'test@example.com', 'name': 'Test User'})
        self.mock_db.collection.assert_called_once_with('users')
        self.mock_collection.document.assert_called_once_with('user123')
        self.mock_document.get.assert_called_once()

    def test_get_user_not_found(self):
        """
        Test retrieval of a non-existent user.
        """
        self.mock_document_snapshot.exists = False
        result = get_user(self.mock_db, 'user123')
        self.assertIsNone(result)
        self.mock_db.collection.assert_called_once_with('users')
        self.mock_collection.document.assert_called_once_with('user123')
        self.mock_document.get.assert_called_once()

    def test_get_user_failure(self):
        """
        Test failure to retrieve a user due to an exception.
        """
        self.mock_document.get.side_effect = Exception('Failed to get user')
        result = get_user(self.mock_db, 'user123')
        self.assertDictEqual(result[0].get_json(), {'error': "Could not get user"})
        self.assertEqual(result[1], 500)

    def test_upsert_user_success(self):
        """
        Test successful creation/update of a user
        """
        result = upsert_user(self.mock_db,
                             {'email': 'fake@divvy.com',
                                      'houseID': 'asdkfnxc',
                                      'id': 'fakeID'})
        self.assertDictEqual(result.get_json(), {'id': 'fakeID'})
        self.mock_db.collection.assert_called_once_with('users')
        self.mock_collection.document.assert_called_once_with('fakeID')
        self.mock_document.set.assert_called_once_with({'email': 'fake@divvy.com',
                                                        'houseID': 'asdkfnxc',
                                                        'id': 'fakeID'})        
    
    def test_upsert_user__failure(self):
        """
        Test failure to create/update user due to an exception
        """
        self.mock_document.set.side_effect = Exception('Failed to create user')
        result = upsert_user(self.mock_db,
                             {'email': 'fake@divvy.com',
                                      'houseID': 'asdkfnxc',
                                      'id': 'fakeID'})
        self.assertDictEqual(result[0].get_json(), {'error': 'Could not upsert user'})
        self.assertEqual(result[1], 500)
        self.mock_db.collection.assert_called_once_with('users')
        self.mock_collection.document.assert_called_once_with('fakeID')
        self.mock_document.set.assert_called_once_with({'email': 'fake@divvy.com',
                                                        'houseID': 'asdkfnxc',
                                                        'id': 'fakeID'})

if __name__ == '__main__':
     unittest.main()
