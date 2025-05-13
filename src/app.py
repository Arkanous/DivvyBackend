# IGNORE THIS FOR NOW

from flask import Flask, request, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import timedelta
import os
import sys
from dotenv import load_dotenv

from flask_cors import CORS

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
        Creates a new house in the database's house collection.
        Request body example:
            {'house_id': '1',
                'house_name': 'New House',
                'creator_user_id': 'u123'}.
        If house_id already exists in the database, its data will be
        overwritten.
    """
    try:
        data = request.get_json()
        house_id = data.get('house_id')
        house_name = data.get('house_name')
        creator_user_id = data.get('creator_user_id')

        if not house_id or not house_name or not creator_user_id:
            return jsonify({'error': 'House ID and name, and creator user ID are required'}), 400

        HOUSES.document(house_id).set(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/get-house-<house_id>', methods=['GET'])
def get_house_route(house_id):
    """
        Retrieves a house document from the database's house collection.
        Request body example:
            {'house_id': '1'}
        If the ID does not exist in the database, returns a house_id of -1.
    """
    try:     
        doc_ref = HOUSES.document(house_id)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify(doc.to_dict())
        else:
            return jsonify({"house_id": "-1"})
    except Exception as e:
        return f"An Error Occured: {e}"

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
