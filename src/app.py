# IGNORE THIS FOR NOW

from flask import Flask, request, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import timedelta
import os
import sys
from dotenv import load_dotenv
from flask_cors import CORS

from houseService.house_utils import create_house, get_house
from userService.user_utils import upsert_user
from choreService.chore_utils import upsert_chore

# Load .env file variables
load_dotenv()

# Create app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
CORS(app)       # needed to send POST/GET requests from flutter

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Adjust session expiration as needed
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Can be 'Strict', 'Lax', or 'None'

# Firebase Admin SDK setup
cred = credentials.Certificate("firebase-auth.json")
initialize_app(cred)
db = firestore.client()

# Primary db collection. The other collection is the "holding area" for new users.
HOUSES = db.collection('houses')


# /// Public Routes /// #
@app.route('/')
def home():
    return "Hello, Divvy App Gateway!"

@app.route('/upsert-chore', methods=['POST'])
def upsert_chore_route():
    """
        Creates a new chore under a house in the database's house
        collection. If the chore already exists, then non-empty fields
        will be updated instead.
        The houseID field must be a valid house ID.
        The choreID field must be non-empty.
        Request body example:
            {'houseID': 'aslkdf',
                'choreID': '12lcxzv',
                'assignees': [
                    'asdnzxvcie'],
                'description': 'A useful desc.',
                'emoji': '\ud83e\uddb8',
                'frequencyDays': [3,7],
                'frequencyPattern': 'weekly',
                'name': 'choreName',
                'startDate': '"Thu, 01 May 2025 07:00:00 GMT'
            }
    """
    data = request.get_json()
    return upsert_chore(db, data)

@app.route('/upsert-user', methods=['POST'])
def upsert_user_route():
    """
        Creates a new user in the database's user collection.
        If the user already exists, then non-empty fields will be
        updated instead.
        The id field must be non-empty.
        Request body example:
            {'email': 'example@gmail.com',
                'houseID': 'alskdjfl',
                'id': 'NisesS
            }
        If id already exists in the database, its data will be
        overwritten.
    """
    data = request.get_json()
    return upsert_user(db, data)

@app.route('/delete-user-<user_id>', methods=['POST'])
def delete_user_route(user_id):
    """
        Deletes a user in the database's user collection.
        The id field must be non-empty.
        Request body example:
            {'email': 'example@gmail.com',
                'houseID': 'alskdjfl',
                'id': 'NisesS
            }
    """
    USERS = db.collection('users')
    user_ref = USERS.document(user_id)
    user_ref.delete()
    return user_id

@app.route('/add-house', methods=['POST'])
def create_house_route():
    """
        Creates a new house in the database's houses collection.
        Request body example:
            {'house_id': '1',
                'house_name': 'New House',
                'creator_user_id': 'u123'}
        If house_id already exists in the database, its data will be
        overwritten.
    """
    data = request.get_json()
    return create_house(db, data)

@app.route('/get-house-<house_id>', methods=['GET'])
def get_house_route(house_id):
    """
        Retrieves a house document from the database's houses collection.
        If the ID does not exist in the database, returns None.
    """
    return get_house(db, house_id)

@app.route('/get-user-<user_id>', methods=['GET'])
def get_user_route(user_id):
    """
        Retrieves a user's house from the database's users collection.
        If the user ID does not exist in the database, returns None.
    """
    USERS = db.collection('users')
    user_ref = USERS.document(user_id)
    user = user_ref.get()
    if user.exists:
        return user.to_dict()
    else:
        return jsonify({'error': 'User with ID {user_id} not found'}), 400

@app.route('/get-house-<house_id>-chores', methods=['GET'])
def get_house_chores_route(house_id):
    """
        Retrieves a house's chores collection.
        Returns None if house_id is not in the database.
    """
    house_ref = HOUSES.document(house_id)
    chores = house_ref.collection('chores').stream()
    chore_list = {

    }
    for chore in chores:
        chore_list[chore.id] = chore.to_dict()

    return chore_list

@app.route('/get-house-<house_id>-chore-instances', methods=['GET'])
def get_house_chore_instances_routes(house_id):
    """
        Retrieves a house's chore instances collection.
        Returns None if house_id is not in the database.
    """
    house_ref = HOUSES.document(house_id)
    choreInstances = house_ref.collection('choreInstances').stream()
    chore_instance_list = {

    }
    for instance in choreInstances:
        chore_instance_list[instance.id] = instance.to_dict()

    return chore_instance_list

@app.route('/get-house-<house_id>-members', methods=['GET'])
def get_house_members_routes(house_id):
    """
        Retrieves a house's members collection.
        Returns None if house_id is not in the database.
    """
    house_ref = HOUSES.document(house_id)
    members = house_ref.collection('members').stream()
    members_list = {

    }
    for member in members:
        members_list[member.id] = member.to_dict()

    return members_list

@app.route('/get-house-<house_id>-subgroups', methods=['GET'])
def get_house_subgroups_routes(house_id):
    """
        Retrieves a house's subgroups collection.
        Returns None if house_id is not in the database.
    """
    house_ref = HOUSES.document(house_id)
    subgroups = house_ref.collection('subgroups').stream()
    subgroups_list = {

    }
    for subgroup in subgroups:
        subgroups_list[subgroup.id] = subgroup.to_dict()

    return subgroups_list

# /// END Public Routes /// #

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


# TODO: Implement a variation of the below to handle errors.
# # Initialize Firebase
# if initialize_firebase():
#     db = get_firestore_db()
#     app.config['FIRESTORE_DB'] = db 
# else:
#     print("Failed to initialize Firebase.  Application may not function correctly.")


# @app.route('/')
# def hello():
#     return "Hello, Divvy App Gateway!"


# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)
