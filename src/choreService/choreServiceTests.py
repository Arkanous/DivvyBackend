import sys 
# Adding userService and utils
sys.path.append('../')
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
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
    get_chore_instances_by_house,
    get_current_day_chore_instances_by_user
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

        self.assertEqual(result, ({'error': 'Could not upsert chore instance'}, 500))

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

    def test_get_chore_instances_by_user_success(self):
        data = {
            'user_id': 'user123',
            'house_id': 'house456'
        }

        mock_doc1 = MagicMock()
        mock_doc1.to_dict.return_value = {'id': 'inst1', 'assignee': 'user123'}

        mock_doc2 = MagicMock()
        mock_doc2.to_dict.return_value = {'id': 'inst2', 'assignee': 'user123'}

        mock_query = MagicMock()
        mock_query.get.return_value = [mock_doc1, mock_doc2]

        chore_instances_mock = MagicMock()
        chore_instances_mock.where.return_value = mock_query

        house_ref_mock = MagicMock()
        house_ref_mock.collection.return_value = chore_instances_mock

        houses_mock = MagicMock()
        houses_mock.document.return_value = house_ref_mock

        self.mock_db.collection.return_value = houses_mock

        result = get_chore_instances_by_user(self.mock_db, data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 'inst1')
        self.assertEqual(result[1]['id'], 'inst2')

    def test_get_chore_instances_by_user_failure(self):
        data = {
            'user_id': 'user123',
            'house_id': 'house456'
        }
        self.mock_db.collection.side_effect = Exception("DB Error")
        result = get_chore_instances_by_user(self.mock_db, data)
        self.assertEqual(result, [])

    def test_get_chore_instances_by_house_success(self):
        data = {'house_id': 'house456'}

        mock_doc1 = MagicMock()
        mock_doc1.to_dict.return_value = {'id': 'inst1'}

        mock_doc2 = MagicMock()
        mock_doc2.to_dict.return_value = {'id': 'inst2'}

        chore_instances_collection = MagicMock()
        chore_instances_collection.get.return_value = [mock_doc1, mock_doc2]

        house_doc = MagicMock()
        house_doc.collection.return_value = chore_instances_collection

        houses_collection = MagicMock()
        houses_collection.document.return_value = house_doc

        self.mock_db.collection.return_value = houses_collection

        result = get_chore_instances_by_house(self.mock_db, data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 'inst1')
        self.assertEqual(result[1]['id'], 'inst2')

    def test_get_chore_instances_by_house_failure(self):
        data = {
            'house_id': 'house456'
        }

        self.mock_db.collection.side_effect = Exception("DB Error")
        result = get_chore_instances_by_house(self.mock_db, data)
        self.assertEqual(result, [])

    @patch('choreService.chore_utils.datetime')
    def test_get_current_day_chore_instances_by_user_success(self, mock_datetime):
        fixed_now = datetime(2025, 5, 31, 10, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.datetime = MagicMock(side_effect=lambda *args, **kwargs: datetime(*args, **kwargs))
        mock_datetime.datetime.now.return_value = fixed_now
        mock_datetime.timezone = timezone

        data = {
            'user_id': 'user_today',
            'house_id': 'house_daily'
        }

        due_today_str = datetime(2025, 5, 31, 15, 0, 0, tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        mock_doc_today = MagicMock()
        mock_doc_today.to_dict.return_value = {'id': 'inst_today', 'assignee': 'user_today', 'dueDate': due_today_str}

        due_yesterday_str = datetime(2025, 5, 30, 10, 0, 0, tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        mock_doc_yesterday = MagicMock()
        mock_doc_yesterday.to_dict.return_value = {'id': 'inst_yesterday', 'assignee': 'user_today', 'dueDate': due_yesterday_str}

        due_tomorrow_str = datetime(2025, 6, 1, 9, 0, 0, tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        mock_doc_tomorrow = MagicMock()
        mock_doc_tomorrow.to_dict.return_value = {'id': 'inst_tomorrow', 'assignee': 'user_today', 'dueDate': due_tomorrow_str}

        mock_query_where_assignee = MagicMock()
        mock_query_where_start_date = MagicMock()
        mock_query_final = MagicMock()

        self.mock_chore_instances_collection.where.return_value = mock_query_where_assignee
        mock_query_where_assignee.where.return_value = mock_query_where_start_date
        mock_query_where_start_date.where.return_value = mock_query_final

        mock_query_final.get.return_value = [mock_doc_today]

        result = get_current_day_chore_instances_by_user(self.mock_db, data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'inst_today')
        self.assertEqual(result[0]['assignee'], 'user_today')
        self.assertEqual(result[0]['dueDate'], due_today_str)


    @patch('choreService.chore_utils.datetime')
    def test_get_current_day_chore_instances_by_user_failure(self, mock_datetime):
        fixed_now = datetime(2025, 5, 31, 10, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.datetime = MagicMock(side_effect=lambda *args, **kwargs: datetime(*args, **kwargs))
        mock_datetime.datetime.now.return_value = fixed_now
        mock_datetime.timezone = timezone

        data = {
            'user_id': 'user_fail',
            'house_id': 'house_fail'
        }

        self.mock_db.collection.side_effect = Exception("Firestore Connection Error")

        result = get_current_day_chore_instances_by_user(self.mock_db, data)

        self.assertEqual(result, [])
        
if __name__ == '__main__':
    unittest.main()