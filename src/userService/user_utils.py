import firebase_admin
from firebase_admin import credentials, firestore
from flask import jsonify

def get_user(db, user_id):
    """
    Retrieves a user document from Firestore.  This assumes you have a 'users'
    collection to store user data (which is separate from Firebase Auth).

    Args:
        db (firestore.Client): The Firestore client.
        user_id (str): The ID of the user to retrieve.

    Returns:
        dict: The user data, or None if the user doesn't exist or an error occurs.
    """
    try:
        user_ref = db.collection('users').document(user_id)
        doc = user_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"User with ID {user_id} not found.")
            return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    

def upsert_user(db, data):
    try:
        USERS = db.collection('users')
        user_ref = USERS.document(data.get('id'))

        user_ref.set(data)
        return jsonify({"id": data.get('id')}) 
    except Exception as e:
        print(f"Error creating user: {e}")
        return None