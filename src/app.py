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

@app.route('/add-house', methods=['POST'])
def create_house_route():
    """
        Creates a new house in the database's houses collection.
        Request body example:
            {'house_id': '1',
                'house_name': 'New House',
                'creator_user_id': 'u123'}.
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
        print(f"User with ID {user_id} not found.")
        return None

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
    


# /// END Public Routes /// #

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

# -----

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
