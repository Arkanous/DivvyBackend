import sys 
# Adding userService and utils
sys.path.append('../')
from flask import Blueprint, request, jsonify, current_app
import sys
import os

# Bad practice but tests won't work without it because Python Modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from house_utils import create_house, get_house, add_member_to_house, get_houses_by_user 
from userService.user_utils import get_user 
from utils.firebase_utils import get_firestore_db

house_bp = Blueprint('house_routes', __name__)

@house_bp.route('', methods=['POST'])
def create_house_route():
    """
    Creates a new house.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    try:
        data = request.get_json()
        house_name = data.get('name')
        creator_user_id = data.get('creator_user_id')

        if not house_name or not creator_user_id:
            return jsonify({'error': 'House name and creator user ID are required'}), 400

        # verify that the creator_user_id exists.
        if not get_user(db, creator_user_id):
            return jsonify({'error': 'Invalid creator user ID'}), 400

        house_id = create_house(db, house_name, creator_user_id)
        if house_id:
            return jsonify({'message': 'House created successfully', 'house_id': house_id}), 201
        else:
            return jsonify({'error': 'Failed to create house'}), 500
    except Exception as e:
        return jsonify({'error': f'Error creating house: {e}'}), 500



@house_bp.route('/<house_id>', methods=['GET'])
def get_house_route(house_id):
    """
    Retrieves a house by its ID.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    house_data = get_house(db, house_id)
    if house_data:
        return jsonify(house_data), 200
    else:
        return jsonify({'error': 'House not found'}), 404



@house_bp.route('/<house_id>/members', methods=['POST'])
def add_member_to_house_route(house_id):
    """
    Adds a member to an existing house.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # verify that the user exists.
        if not get_user(db, user_id):
            return jsonify({'error': 'Invalid user ID'}), 400

        # verify that the house exists
        if not get_house(db, house_id):
            return jsonify({'error': 'Invalid house ID'}), 400
        
        if add_member_to_house(db, house_id, user_id):
            return jsonify({'message': 'Member added successfully'}), 200
        else:
            return jsonify({'error': 'Failed to add member'}), 500
    except Exception as e:
        return jsonify({'error': f'Error adding member: {e}'}), 500

@house_bp.route('/user/<user_id>', methods=['GET'])
def get_houses_by_user_route(user_id):
    """
    Retrieves all houses a user is a member of.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    # verify that the user exists.
    if not get_user(db, user_id):
        return jsonify({'error': 'Invalid user ID'}), 400

    houses = get_houses_by_user(db, user_id)
    return jsonify(houses), 200