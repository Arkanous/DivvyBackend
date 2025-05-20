from flask import jsonify
from firebase_admin import firestore


def create_house(db, data):
    try:
        HOUSES = db.collection('houses')
        house_id = data.get('id')
        house_name = data.get('name')
        members = data.get('members')
        dateCreated = data.get('dateCreated')
        imageID = data.get('imageID')
        joinCode = data.get('joinCode')

        house_data = {
            'id': house_id,
            'name': house_name,
            'members': members,
            'dateCreated': dateCreated,
            'imageID': imageID,
            'joinCode': joinCode
        }

        # if not house_id or not house_name or not creator_user_id:
        #     return jsonify({'error': 'House ID and name, and creator user ID are required'}), 400

        HOUSES.document(house_id).set(data)
        return jsonify({"id": str(house_id)}) 
    except Exception as e:
        print(f"Error creating house: {e}")
        return None

def get_house(db, house_id):
    """
    Retrieves a house document from Firestore.

    Args:
        HOUSES: The Firestore database's houses collection.
        house_id (str): The ID of the house to retrieve.

    Returns:
        dict: The house data, or None if the house doesn't exist or an error occurs.
    """   
    try:
        HOUSES = db.collection('houses')
        house_ref = HOUSES.document(house_id)
        house = house_ref.get()
        if house.exists:
            return house.to_dict()
        else:
            return jsonify({'error': 'House with code {join_code} not found'}), 400
    except Exception as e:
        return jsonify({'error': 'e'}), 400


# Old Methods - need to be updated eventually

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
    

# coll_ref is the collection reference to delete
def delete_collection(coll_ref, batch_size=50):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id}')
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)
