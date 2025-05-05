import unittest
from unittest.mock import MagicMock, patch
import firebase_admin
from firebase_admin import credentials, firestore, auth  # Import auth
import google.cloud.firestore # Import google.cloud.firestore

# Assuming your user_routes.py and utils/user_utils.py are in the same directory
# as your test file, or adjust the import paths accordingly.
from user_routes import (user_bp, get_user_route, create_user_route)
from user_utils import (get_user, create_user)


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

        self.app = MagicMock()
        self.app.config = {'FIRESTORE_DB': self.mock_db}
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
        self.assertEqual(result, {'email': 'test@example.com', 'name': 'Test User'})
        self.mock_collection.document.assert_called_once_with('user123')
        self.mock_document.get.assert_called_once()

    def test_get_user_not_found(self):
        """
        Test retrieval of a non-existent user.
        """
        self.mock_document_snapshot.exists = False
        result = get_user(self.mock_db, 'user123')
        self.assertIsNone(result)

    def test_get_user_failure(self):
        """
        Test failure to retrieve a user due to an exception.
        """
        self.mock_document.get.side_effect = Exception('Failed to get user')
        result = get_user(self.mock_db, 'user123')
        self.assertIsNone(result)

    def test_create_user_success(self):
        """
        Test successful creation of a user.
        """
        result = create_user(self.mock_db, 'user123', 'test@example.com', 'Test User')
        self.assertTrue(result)
        self.mock_collection.document.assert_called_once_with('user123')
        self.mock_document.set.assert_called_once_with({
            'email': 'test@example.com',
            'name': 'Test User',
        })

    def test_create_user_failure(self):
        """
        Test failure to create a user due to an exception.
        """
        self.mock_document.set.side_effect = Exception('Failed to create user')
        result = create_user(self.mock_db, 'user123', 'test@example.com', 'Test User')
        self.assertFalse(result)

    def test_get_user_route_success(self):
        """
        Test successful retrieval of a user via the route.
        """
        self.mock_document_snapshot.exists = True
        self.mock_document_snapshot.to_dict.return_value = {'email': 'test@example.com', 'name': 'Test User'}

        with self.app.test_request_context('/users/user123', method='GET'):
            response = get_user_route('user123')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), {'email': 'test@example.com', 'name': 'Test User'})
            self.mock_collection.document.assert_called_once_with('user123')
            self.mock_document.get.assert_called_once()

    def test_get_user_route_not_found(self):
        """
        Test retrieval of a non-existent user via the route.
        """
        self.mock_document_snapshot.exists = False
        with self.app.test_request_context('/users/user123', method='GET'):
            response = get_user_route('user123')
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.get_json(), {'error': 'User not found'})

    def test_get_user_route_exception(self):
        """
        Test exception during user retrieval via the route.
        """
        self.mock_document.get.side_effect = Exception('Simulated error')
        with self.app.test_request_context('/users/user123', method='GET'):
            response = get_user_route('user123')
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.get_json(), {'error': 'Error getting user: Simulated error'})

    def test_create_user_route_success(self):
        """
        Test successful creation of a user via the route.
        """
        mock_auth_user = MagicMock()
        mock_auth_user.uid = 'new_user_id'
        self.mock_auth.create_user.return_value = mock_auth_user

        with patch('user_utils.create_user', return_value=True):
            with self.app.test_request_context(
                '/users',
                method='POST',
                json={'email': 'test@example.com', 'password': 'password123', 'name': 'Test User'},
            ):
                response = create_user_route()
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.get_json(), {'message': 'User created successfully', 'user_id': 'new_user_id'})
                self.mock_auth.create_user.assert_called_once_with(email='test@example.com', password='password123')

    def test_create_user_route_missing_data(self):
        """
        Test creating a user with missing data via the route.
        """
        with self.app.test_request_context(
            '/users',
            method='POST',
            json={'email': 'test@example.com', 'password': 'password123'},
        ):
            response = create_user_route()
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json(), {'error': 'Email, password, and name are required'})
            self.mock_auth.create_user.assert_not_called()

    def test_create_user_route_auth_error(self):
        """
        Test error during Firebase Auth user creation via the route.
        """
        self.mock_auth.create_user.side_effect = Exception('Authentication error')
        with self.app.test_request_context(
            '/users',
            method='POST',
            json={'email': 'test@example.com', 'password': 'password123', 'name': 'Test User'},
        ):
            response = create_user_route()
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.get_json(), {'error': 'Failed to create user: Authentication error'})

    def test_create_user_route_firestore_error(self):
        """
        Test error during Firestore user creation via the route.
        """
        mock_auth_user = MagicMock()
        mock_auth_user.uid = 'new_user_id'
        self.mock_auth.create_user.return_value = mock_auth_user
        with patch('user_utils.create_user', return_value=False):
            with self.app.test_request_context(
                '/users',
                method='POST',
                json={'email': 'test@example.com', 'password': 'password123', 'name': 'Test User'},
            ):
                response = create_user_route()
                self.assertEqual(response.status_code, 500)
                self.assertEqual(response.get_json(), {'error': 'User creation failed in Firestore'})
                self.mock_auth.delete_user.assert_called_once_with('new_user_id')

    def test_create_user_route_firestore_error_delete_user_error(self):
        """
        Test error during Firestore user creation and error during Firebase Auth user deletion via the route.
        """
        mock_auth_user = MagicMock()
        mock_auth_user.uid = 'new_user_id'
        self.mock_auth.create_user.return_value = mock_auth_user
        with patch('user_utils.create_user', return_value=False):
            self.mock_auth.delete_user.side_effect = Exception("Delete error")
            with self.app.test_request_context(
                '/users',
                method='POST',
                json={'email': 'test@example.com', 'password': 'password123', 'name': 'Test User'},
            ):
                response = create_user_route()
                self.assertEqual(response.status_code, 500)
                self.assertEqual(response.get_json(), {'error': 'User creation failed in Firestore'})
                self.mock_auth.delete_user.assert_called_once_with('new_user_id')

if __name__ == '__main__':
     unittest.main()
