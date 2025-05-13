import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
import firebase_admin
from firebase_admin import credentials, firestore, auth 
from flask import Flask

import sys
import os

# Bad practice but tests won't work without it because Python Modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from utils.firebase_utils import get_firestore_db

class TestFirebaseUtils(unittest.TestCase):
    """
    Unit tests for the firebase_utils.py module.
    """

    def setUp(self):
        """
        Set up mocks for Firebase Admin SDK and Firestore.  This is crucial
        to avoid actually connecting to a real Firebase database during tests.
        """
        self.initialize_app_patch = patch('firebase_admin.initialize_app')
        self.mock_initialize_app = self.initialize_app_patch.start()

        self.mock_firestore_client = MagicMock()

        self.firestore_client_patch = patch('firebase_admin.firestore.client', return_value=self.mock_firestore_client)
        self.mock_firestore_client_instance = self.firestore_client_patch.start()

        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.request_context = MagicMock()

        self.mock_auth = MagicMock()
        self.auth_patch = patch('firebase_admin.auth', self.mock_auth)
        self.auth_patch.start()

        # store the patched functions, and unpatch them in tearDown
        self.get_firestore_db_patch = patch('src.utils.firebase_utils.get_firestore_db', return_value=self.mock_firestore_client)
        self.get_firestore_db_patch.start()

    def tearDown(self):
        """
        Clean up the mocks after each test.  This is important to prevent
        interference between tests.
        """
        self.initialize_app_patch.stop()
        self.firestore_client_patch.stop()
        self.get_firestore_db_patch.stop()

    # NOT BEING USED because firebase_utils.py is not currently being used. Will be re-implemented
    # when firebase_utils.py is updated.
    # def test_get_firestore_db_success(self):
    #     """
    #     Test successful retrieval of the Firestore client.
    #     """
    #     with patch('firebase_admin._apps', [MagicMock()]):
    #         db = get_firestore_db()
    #         self.assertEqual(db, self.mock_firestore_client)

    # def test_get_firestore_db_failure(self):
    #     """
    #     Test failure to retrieve the Firestore client when Firebase is not initialized.
    #     """
    #     with patch('firebase_admin._apps', []):
    #         db = get_firestore_db()
    #         self.assertIsNone(db)

if __name__ == "__main__":
     unittest.main()