# IGNORE THIS FOR NOW

from flask import Flask, request, jsonify, make_response
from firebase_admin import credentials, firestore, initialize_app
from datetime import timedelta
import os
import sys
from dotenv import load_dotenv
from flask_cors import CORS
from google.cloud.firestore_v1 import FieldFilter

from houseService.house_utils import create_house, delete_collection, get_house
from userService.user_utils import upsert_user
from choreService.chore_utils import upsert_chore, upsert_chore_instance


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
USERS = db.collection('users')


# /// Public Routes /// #
@app.route('/')
def home():
    return "Hello, Divvy App Gateway!"

@app.route('/upsert-member-<house_id>', methods=['POST'])
def upsert_member_route(house_id):
    """
        Adds an existing user as a member to a house in the database's
        house collection. If the member already exists, then non-empty
        fields will be updated instead.
        The houseID field must be a valid house ID.
        The id field must be non-empty.
        Request body example:
            {'houseID': 'aslkdf',
                'id': 'zoiwern',
                'chores': [
                    'asdnzxpow8cx'],
                'dateJoined': 'Thu, 01 May 2025 07:00:00 GMT',
                'email': 'example@divvy.com',
                'name': 'a Name',
                'onTimePct': '82',
                'profilePicture': 'lightGreen',
                'subgroups': [
                    'zxc0923n']
            }
    """
    data = request.get_json()
    # TODO: check to make sure the user exists already
    try:
        house_ref = HOUSES.document(house_id)
        member_id = data.get('id')
        house_ref.collection('members').document(member_id).set(data)
        return jsonify({'id': member_id})
    except Exception as e:
        print(f"Error creating/updating user: {e}")
        return jsonify({'error': 'Member could not be added: {e}'}), 400

@app.route('/upsert-chore-instance-<house_id>', methods=['POST'])
def upsert_chore_instance_route(house_id):
    """
        Creates a new chore instance under a house in the database's
        house collection. If the chore instance already exists, then
        non-empty fields will be updated instead.
        The houseID field must be a valid house ID.
        The choreID field must a valid (super) chore ID of that house.
        The id field must be non-empty.
    """
    data = request.get_json()
    return upsert_chore_instance(db, data, house_id)

@app.route('/upsert-chore-<house_id>', methods=['POST'])
def upsert_chore_route(house_id):
    """
        Creates a new chore under a house in the database's house
        collection. If the chore already exists, then non-empty fields
        will be updated instead.
        The houseID field must be a valid house ID.
        The id field must be non-empty.
        Request body example:
            {
                'id': '12lcxzv',
                'assignees': [
                    'asdnzxvcie'],
                'description': 'A useful desc.',
                'emoji': '<emojiHere>',
                'frequencyDays': ['3','7'],
                'frequencyPattern': 'weekly',
                'name': 'choreName',
                'startDate': 'Thu, 01 May 2025 07:00:00 GMT'
            }
    """
    data = request.get_json()
    return upsert_chore(db, data, house_id)

@app.route('/upsert-subgroup-<house_id>', methods=['POST'])
def upsert_subgroup_route(house_id):
    """
        Creates a new subgroup under a house in the database's house
        collection. If the subgroup already exists, then non-empty fields
        will be updated instead.
    """
    try:
        data = request.get_json()
        house_ref = HOUSES.document(house_id)
        sub_ref = house_ref.collection('subgroups')
        sub_ref.document(data.get('id')).set(data)
        return jsonify({'id': data.get('id')})              # TODO: implement jsonify on all returns for routes and add 400 code on error.
    except Exception as e:
        return jsonify({'error': 'Subgroup could not be added'}), 400
    

@app.route('/upsert-swap-<house_id>', methods=['POST'])
def upsert_swap_route(house_id):
    """
        Creates a new swap under a house in the database's house
        collection. If the swap already exists, then non-empty fields
        will be updated instead.
    """
    try:
        data = request.get_json()
        house_ref = HOUSES.document(house_id)
        swap_ref = house_ref.collection('swaps')
        swap_ref.document(data.get('id')).set(data)
        return jsonify({'id': data.get('id')}) 
    except Exception as e:
        return jsonify({'error': 'Swap could not be added'}), 400


@app.route('/upsert-house', methods=['POST'])
def upsert_house_route():
    """
        Updates house data. If the house already exists, then non-empty fields
        will be updated instead.
    """
    try:
        data = request.get_json()
        house_ref = HOUSES.document(data.get('id'))
        house_ref.set(data)
        return jsonify({'id': data.get('id')}) 
    except Exception as e:
        return jsonify({'error': 'House could not be updated'}), 400
    

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
                'id': 'NisesS'
            }
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
    user_ref = USERS.document(user_id)
    user_ref.delete()
    return jsonify({"id": str(user_id)}) 

@app.route('/delete-chore-<house_id>', methods=['POST'])
def delete_chore_route(house_id):
    """
        Deletes a chore in the database's house collection.
        The id field must be non-empty.
    """
    data = request.get_json()
    house_ref = HOUSES.document(house_id)
    chore_ref = house_ref.collection('chores').document(data.get('id'))
    chore_ref.delete()
    return jsonify({"id": str(data.get('id'))}) 

@app.route('/delete-chore-instance-<house_id>', methods=['POST'])
def delete_chore_instance_route(house_id):
    """
        Deletes a chore instance in the database's house collection.
        The id field must be non-empty.
    """
    data = request.get_json()
    house_ref = HOUSES.document(house_id)
    chore_ref = house_ref.collection('choreInstances').document(data.get('id'))
    chore_ref.delete()
    return jsonify({"id": str(data.get('id'))}) 

@app.route('/delete-subgroup-<house_id>', methods=['POST'])
def delete_subgroup_route(house_id):
    """
        Deletes a subgroup in the database's house collection.
        The id field must be non-empty.
    """
    data = request.get_json()
    house_ref = HOUSES.document(house_id)
    sub_ref = house_ref.collection('subgroups').document(data.get('id'))
    sub_ref.delete()
    return jsonify({"id": str(data.get('id'))}) 

@app.route('/delete-swap-<house_id>', methods=['POST'])
def delete_swap_route(house_id):
    """
        Deletes a swap in the database's house collection.
        The id field must be non-empty.
    """
    data = request.get_json()
    house_ref = HOUSES.document(house_id)
    sub_ref = house_ref.collection('swaps').document(data.get('id'))
    sub_ref.delete()
    return jsonify({"id": str(data.get('id'))}) 

@app.route('/delete-member-<house_id>', methods=['POST'])
def delete_member_route(house_id):
    """
        Deletes a memb er in the database's house collection.
        The id field must be non-empty.
    """
    data = request.get_json()
    house_ref = HOUSES.document(house_id)
    sub_ref = house_ref.collection('members').document(data.get('id'))
    sub_ref.delete()
    return jsonify({"id": str(data.get('id'))}) 

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


@app.route('/delete-house-<house_id>', methods=['POST'])
def delete_house_route(house_id):
    """
        Deletes a house in the database's House collection.
        Deletes all subcollections within.
        The id field must be non-empty.
    """
    house_ref = HOUSES.document(house_id)
    members_ref = house_ref.collection('members')
    delete_collection(members_ref)
    chore_inst_ref = house_ref.collection('choreInstances')
    delete_collection(chore_inst_ref)
    subgroups_ref = house_ref.collection('subgroups')
    delete_collection(subgroups_ref)
    chores_ref = house_ref.collection('chores')
    delete_collection(chores_ref)
    swaps_ref = house_ref.collection('swaps')
    delete_collection(swaps_ref)
    # finally, delete house
    house_ref.delete()
    return jsonify({"id": str(house_id)}) 

@app.route('/get-house-<house_id>', methods=['GET'])
def get_house_route(house_id):
    """
        Retrieves a house document from the database's houses collection.
        If the ID does not exist in the database, returns None.
    """
    return get_house(db, house_id)

@app.route('/get-house-join-<join_code>', methods=['GET'])
def get_house_join_route(join_code):
    """
        Retrieves a house document from the database's houses collection with
        the matching join code
    """
    house_query = HOUSES.where(filter=FieldFilter("joinCode", "==", join_code))
    house_docs = house_query.get()
    if house_docs:
        return house_docs[0].to_dict()
    else:
        return jsonify({'error': 'House with code {join_code} not found'}), 400

@app.route('/get-user-<user_id>', methods=['GET'])
def get_user_route(user_id):
    """
        Retrieves a user's house from the database's users collection.
        If the user ID does not exist in the database, returns None.
    """
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
    house = house_ref.get()
    if not house.exists:
        return jsonify({'error': 'House does not exist'}), 400
    chores = house_ref.collection('chores').stream()
    chore_list = {}
    for chore in chores:
        chore_list[chore.id] = chore.to_dict()

    return chore_list

@app.route('/get-house-<house_id>-swaps', methods=['GET'])
def get_house_swaps_route(house_id):
    """
        Retrieves a house's swaps collection.
        Returns None if house_id is not in the database.
    """
    house_ref = HOUSES.document(house_id)
    house = house_ref.get()
    if not house.exists:
        return jsonify({'error': 'House does not exist'}), 400
    swaps = house_ref.collection('swaps').stream()
    swaps_list = {}
    for swap in swaps:
        swaps_list[swap.id] = swap.to_dict()

    return swaps_list

@app.route('/get-house-<house_id>-chore-instances', methods=['GET'])
def get_house_chore_instances_routes(house_id):
    """
        Retrieves a house's chore instances collection.
        Returns None if house_id is not in the database.
    """
    house_ref = HOUSES.document(house_id)
    house = house_ref.get()
    if not house.exists:
        return jsonify({'error': 'House does not exist'}), 400
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
    house = house_ref.get()
    if not house.exists:
        return jsonify({'error': 'House does not exist'}), 400
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
    house = house_ref.get()
    if not house.exists:
        return jsonify({'error': 'House does not exist'}), 400
    subgroups = house_ref.collection('subgroups').stream()
    subgroups_list = {

    }
    for subgroup in subgroups:
        subgroups_list[subgroup.id] = subgroup.to_dict()

    return subgroups_list

@app.route('/get-house-<house_id>-subgroup-<subgroup_id>', methods=['GET'])
def get_house_subgroup_route(house_id, subgroup_id):
    """
        Retrieves a subgroup from a house
        Returns None if house_id or subgroup_id is not in the database. 
    """

    try:
        house_ref = HOUSES.document(house_id)
        house = house_ref.get()
        if not house.exists:
            return jsonify({'error': 'House does not exist'}), 400
        subgroup_ref = house_ref.collection('subgroups').document(subgroup_id)
        subgroup = subgroup_ref.get()
        if subgroup.exists:
            return subgroup.to_dict()
        return jsonify({'error': 'Subgroup not found'}), 400
    except Exception as e:
        return jsonify({'error': 'Subgroup not found'}), 400
    
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
