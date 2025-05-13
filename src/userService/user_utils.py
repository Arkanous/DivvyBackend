import firebase_admin
from firebase_admin import credentials, firestore

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

def create_user(db, user_id, email, name):
    """
    Creates a new user document in the 'users' collection.  This is in *addition*
    to the user created by Firebase Authentication.  You'll need to do this
    after a user successfully signs up via Firebase Auth.

    Args:
        db (firestore.Client): The Firestore client.
        user_id (str): The unique ID of the user (from Firebase Auth).
        email (str): The user's email address.
        name (str): The user's name.

    Returns:
        bool: True on success, False on error.
    """
    try:
        user_ref = db.collection('users').document(user_id)
        user_data = {
            'email': email,
            'name': name
            # TODO: other fields and stuff
        }
        user_ref.set(user_data)
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False