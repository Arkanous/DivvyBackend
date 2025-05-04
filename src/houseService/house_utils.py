# houseService/house_utils.py
from firebase_admin import firestore

def create_house(db, house_name, creator_user_id):
    """
    Creates a new house in Firestore.

    Args:
        db (firestore.Client): The Firestore client.
        house_name (str): The name of the house.
        creator_user_id (str): The ID of the user creating the house.

    Returns:
        str: The ID of the newly created house, or None on error.
    """
    try:
        house_ref = db.collection('houses').document()
        house_id = house_ref.id
        house_data = {
            'name': house_name,
            'members': [creator_user_id],
            'created_at': firestore.SERVER_TIMESTAMP,
            'creator_user_id': creator_user_id,
        }
        house_ref.set(house_data)
        return house_id
    except Exception as e:
        print(f"Error creating house: {e}")
        return None



def get_house(db, house_id):
    """
    Retrieves a house document from Firestore.

    Args:
        db (firestore.Client): The Firestore client.
        house_id (str): The ID of the house to retrieve.

    Returns:
        dict: The house data, or None if the house doesn't exist or an error occurs.
    """
    try:
        house_ref = db.collection('houses').document(house_id)
        doc = house_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"House with ID {house_id} not found.")
            return None
    except Exception as e:
        print(f"Error getting house: {e}")
        return None


def add_member_to_house(db, house_id, user_id):
    """
    Adds a user to an existing house.

    Args:
        db (firestore.Client): The Firestore client.
        house_id (str): The ID of the house.
        user_id (str): The ID of the user to add.

    Returns:
        bool: True on success, False on error.
    """
    try:
        house_ref = db.collection('houses').document(house_id)
        house_ref.update({'members': firestore.ArrayUnion([user_id])})
        return True
    except Exception as e:
        print(f"Error adding member to house: {e}")
        return False

def get_houses_by_user(db, user_id):
    """
    Retrieves all houses a user is a member of

    Args:
        db (firestore.Client): the Firestore Client
        user_id (str): the id of the user

    Returns:
        list(dict): A list of house dictionaries
    """
    try:
        houses = []
        houses_ref = db.collection('houses')
        query = houses_ref.where('members', 'array_contains', user_id)
        results = query.get()
        for house in results:
            houses.append(house.to_dict())
        return houses
    except Exception as e:
        print(f"Error getting houses for user {user_id}: {e}")
        return []
