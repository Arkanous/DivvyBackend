import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
import firebase_admin
from firebase_admin import credentials, firestore  # Import firestore
import os

# Assuming your firebase_utils.py is in the same directory as your test file.
# If not, you'll need to adjust the import path.
from utils import (
    initialize_firebase,
    get_firestore_db,
    create_house,
    get_house,
    add_member_to_house,
    get_houses_by_user,
    get_user,
    create_user,
    create_chore,
    generate_chore_instances,
    get_chore_instances_by_user,
    get_chore_instance,
    update_chore_instance,
    get_chores_by_house,
)

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

        # store the patched functions, and unpatch them in tearDown
        self.get_firestore_db_patch = patch('utils.firebase_utils.get_firestore_db', return_value=self.mock_firestore_client)
        self.get_firestore_db_patch.start()

    def tearDown(self):
        """
        Clean up the mocks after each test.  This is important to prevent
        interference between tests.
        """
        self.initialize_app_patch.stop()
        self.firestore_client_patch.stop()
        self.get_firestore_db_patch.stop()

    def test_get_firestore_db_success(self):
        """
        Test successful retrieval of the Firestore client.
        """
        with patch('firebase_admin._apps', [MagicMock()]):
            db = get_firestore_db()
            self.assertEqual(db, self.mock_firestore_client)

    def test_get_firestore_db_failure(self):
        """
        Test failure to retrieve the Firestore client when Firebase is not initialized.
        """
        with patch('firebase_admin._apps', []):
            db = get_firestore_db()
            self.assertIsNone(db)