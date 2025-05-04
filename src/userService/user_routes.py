from flask import Blueprint, request, jsonify, current_app
from user_utils import get_user, create_user
from firebase_admin import auth

user_bp = Blueprint('user_routes', __name__)


@user_bp.route('/<user_id>', methods=['GET'])
def get_user_route(user_id):
    """
    Retrieves a user by their ID.  This route assumes that the user_id is the
    same as the Firebase Auth UID.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    user_data = get_user(db, user_id)
    if user_data:
        return jsonify(user_data), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@user_bp.route('', methods=['POST'])
def create_user_route():
    """
    Creates a new user.  This route handles both creating the user in Firebase
    Authentication *and* storing additional user data in Firestore.
    """
    db = current_app.config['FIRESTORE_DB']
    if not db:
        return jsonify({'error': 'Firestore not initialized'}), 500

    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400

        # create the user in Firebase Authentication
        try:
            user = auth.create_user(
                email=email,
                password=password,
            )
        except Exception as e:
            print(f"Error creating user in Firebase Auth: {e}")
            return jsonify({'error': f'Failed to create user: {e}'}), 500

        # create the user document in Firestore
        user_id = user.uid
        if create_user(db, user_id, email, name):
            return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
        else:
            #  TODO: delete user verificaiton and concurrency edge cases
            try:
                auth.delete_user(user_id)
                print(f"Deleted Firebase Auth user {user_id} due to Firestore creation failure.")
            except Exception as e:
                print(f"Error deleting Firebase Auth user {user_id}: {e}")
            return jsonify({'error': 'User creation failed in Firestore'}), 500

    except Exception as e:
        return jsonify({'error': f'Error creating user: {e}'}), 500