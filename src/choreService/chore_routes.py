import sys 
# Adding userService and utils
sys.path.append('../')
from flask import Blueprint, request, jsonify, current_app
from choreService.chore_utils import (
    create_chore,
    generate_chore_instances,
    get_chore_instances_by_user,
    get_chore_instance,
    update_chore_instance,
    get_chores_by_house,
)
import sys
import os

# Bad practice but tests won't work without it because Python Modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from userService.user_utils import get_user
from utils.firebase_utils import get_firestore_db
from datetime import datetime

chore_bp = Blueprint('chore_routes', __name__)


@chore_bp.route('', methods=['POST'])
def create_chore_route():
    """
    Creates a new chore.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    try:
        data = request.get_json()
        house_id = data.get('house_id')
        description = data.get('description')
        assigned_to = data.get('assigned_to')
        schedule_type = data.get('schedule_type')
        schedule_data = data.get('schedule_data')
        created_by = data.get('created_by')
        subgroup_id = data.get('subgroup_id')

        if not house_id or not description or not assigned_to or not schedule_type or not created_by:
            return jsonify({'error': 'House ID, description, assigned_to, schedule_type, and created_by are required'}), 400

        # Validate assigned_to user IDs
        for user_id in assigned_to:
            if not get_user(db, user_id):
                return jsonify({'error': f'Invalid user ID: {user_id}'}), 400

        chore_id = create_chore(db, house_id, description, assigned_to, schedule_type, schedule_data, created_by, subgroup_id)
        if chore_id:
            return jsonify({'message': 'Chore created successfully', 'chore_id': chore_id}), 201
        else:
            return jsonify({'error': 'Failed to create chore'}), 500
    except Exception as e:
        return jsonify({'error': f'Error creating chore: {e}'}), 500


@chore_bp.route('/<chore_id>/instances', methods=['POST'])
def generate_chore_instances_route(chore_id):
    """
    Generates chore instances for a given chore.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    try:
        data = request.get_json()
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Start date and end date are required'}), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format.  Use %Y-%m-%d'}), 400

        instance_ids = generate_chore_instances(db, chore_id, start_date, end_date)
        if instance_ids:
            return jsonify({'message': 'Chore instances generated successfully', 'instance_ids': instance_ids}), 201
        else:
            return jsonify({'error': 'Failed to generate chore instances'}), 500
    except Exception as e:
        return jsonify({'error': f'Error generating chore instances: {e}'}), 500


@chore_bp.route('/user/<user_id>/instances', methods=['GET'])
def get_chore_instances_by_user_route(user_id):
    """
    Retrieves chore instances for a specific user within a date range.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Start date and end date are required'}), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format.  Use %Y-%m-%d'}), 400

        instances = get_chore_instances_by_user(db, user_id, start_date, end_date)
        return jsonify(instances), 200
    except Exception as e:
        return jsonify({'error': f'Error getting chore instances: {e}'}), 500


@chore_bp.route('/instances/<instance_id>', methods=['GET'])
def get_chore_instance_route(instance_id):
    """
    Retrieves a specific chore instance.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    instance = get_chore_instance(db, instance_id)
    if instance:
        return jsonify(instance), 200
    else:
        return jsonify({'error': 'Chore instance not found'}), 404


@chore_bp.route('/instances/<instance_id>', methods=['PUT'])
def update_chore_instance_route(instance_id):
    """
    Updates a chore instance (e.g., to mark it as completed).
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided for update'}), 400

        if update_chore_instance(db, instance_id, data):
            return jsonify({'message': 'Chore instance updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update chore instance'}), 500
    except Exception as e:
        return jsonify({'error': f'Error updating chore instance: {e}'}), 500

@chore_bp.route('/house/<house_id>', methods=['GET'])
def get_chores_by_house_route(house_id):
    """
    Retrieves all chores for a given house.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    chores = get_chores_by_house(db, house_id)
    return jsonify(chores), 200