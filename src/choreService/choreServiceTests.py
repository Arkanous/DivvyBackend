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

# from userService.user_utils import get_user
# from choreService.chore_routes import (chore_bp, create_chore_route, create_chore, get_chore_instances_by_user_route, generate_chore_instances_route)
from choreService.chore_utils import (
    upsert_chore,
    upsert_chore_instance,
    get_chore_instances_by_user,
)
from flask import Flask


class TestChoreService(unittest.TestCase):
    """
    Unit tests for the chore service (routes and utility functions).
    """

    def setUp(self):
        # Mock Firestore client and collections
        self.mock_db = MagicMock()
        self.mock_houses_collection = MagicMock()
        self.mock_house_doc = MagicMock()
        self.mock_chore_instances_collection = MagicMock()
        self.mock_chore_instance_doc = MagicMock()
        self.mock_chores_collection = MagicMock()
        self.mock_chore_doc = MagicMock()

        # Setup collection/document chaining mocks
        self.mock_db.collection.return_value = self.mock_houses_collection
        self.mock_houses_collection.document.return_value = self.mock_house_doc
        self.mock_house_doc.collection.side_effect = lambda name: {
            'choreInstances': self.mock_chore_instances_collection,
            'chores': self.mock_chores_collection
        }[name]

        self.mock_chore_instances_collection.document.return_value = self.mock_chore_instance_doc
        self.mock_chores_collection.document.return_value = self.mock_chore_doc

    @patch('choreService.chore_utils.jsonify')
    def test_upsert_chore_instance_success(self, mock_jsonify):
        data = {'id': 'inst1', 'choreID': 'ch1'}
        mock_jsonify.side_effect = lambda x: x  # return argument for easy checking

        result = upsert_chore_instance(self.mock_db, data, 'house1')

        self.mock_db.collection.assert_called_with('houses')
        self.mock_houses_collection.document.assert_called_with('house1')
        self.mock_house_doc.collection.assert_called_with('choreInstances')
        self.mock_chore_instances_collection.document.assert_called_with('inst1')
        self.mock_chore_instance_doc.set.assert_called_with(data)
        self.assertEqual(result, {'id': 'inst1'})

    @patch('choreService.chore_utils.jsonify')
    def test_upsert_chore_instance_failure(self, mock_jsonify):
        data = {'id': 'inst1'}
        self.mock_chore_instances_collection.document.side_effect = Exception('fail')
        mock_jsonify.side_effect = lambda x, code=None: (x, code) if code else x

        result = upsert_chore_instance(self.mock_db, data, 'house1')

        self.assertEqual(result, ({'error': 'Could not upsert chore instance'}, 400))

    @patch('choreService.chore_utils.jsonify')
    def test_upsert_chore_success(self, mock_jsonify):
        data = {'id': 'ch1', 'name': 'Clean'}
        mock_jsonify.side_effect = lambda x: x

        result = upsert_chore(self.mock_db, data, 'house1')

        self.mock_db.collection.assert_called_with('houses')
        self.mock_houses_collection.document.assert_called_with('house1')
        self.mock_house_doc.collection.assert_called_with('chores')
        self.mock_chores_collection.document.assert_called_with('ch1')
        self.mock_chore_doc.set.assert_called_with(data)
        self.assertEqual(result, {'id': 'ch1'})

    @patch('choreService.chore_utils.jsonify')
    def test_upsert_chore_failure(self, mock_jsonify):
        data = {'id': 'ch1'}
        self.mock_chores_collection.document.side_effect = Exception('fail')
        mock_jsonify.side_effect = lambda x, code=None: (x, code) if code else x

        result = upsert_chore(self.mock_db, data, 'house1')

        self.assertEqual(result, ({'error': 'Could not upsert chore'}, 400))

    def test_get_chore_instances_by_user_success(self):
        # setup mock query results
        mock_instance1 = MagicMock()
        mock_instance1.to_dict.return_value = {'id': 'inst1', 'assignee': 'user1'}
        mock_instance2 = MagicMock()
        mock_instance2.to_dict.return_value = {'id': 'inst2', 'assignee': 'user1'}

        mock_collection = MagicMock()
        mock_collection.where.return_value.get.return_value = [mock_instance1, mock_instance2]

        self.mock_db.collection.return_value = mock_collection

        results = get_chore_instances_by_user(self.mock_db, 'user1')

        self.mock_db.collection.assert_called_with('choreInstances')
        mock_collection.where.assert_called_with('assignee', '==', 'user1')
        self.assertEqual(results, [{'id': 'inst1', 'assignee': 'user1'}, {'id': 'inst2', 'assignee': 'user1'}])

    def test_get_chore_instances_by_user_failure(self):
        mock_collection = MagicMock()
        mock_collection.where.side_effect = Exception('fail')
        self.mock_db.collection.return_value = mock_collection

        results = get_chore_instances_by_user(self.mock_db, 'user1')
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()