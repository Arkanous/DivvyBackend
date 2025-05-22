from firebase_admin import firestore
from datetime import datetime
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from flask import jsonify

# /// Chore Utility Functions /// #
    # Primarily called by app.py's public routes

def upsert_chore(db, data, house_id):
    try:
        HOUSES = db.collection('houses')
        house_ref = HOUSES.document(house_id)

        CHORES = house_ref.collection('chores')
        chore_ref = CHORES.document(data.get('id'))
        chore_ref.set(data)
        return jsonify({'id': data.get('id')}) 
    except Exception as e:
        print(f"Error creating/updating chore: {e}")
        return jsonify({'error': 'Could not upsert chore'}), 500

def upsert_chore_instance(db, data, house_id):
    # TODO: lots to do here, but definitely need to make sure that choreID is valid
    try:
        HOUSES = db.collection('houses')
        house_ref = HOUSES.document(house_id)

        CHORE_INSTANCES = house_ref.collection('choreInstances')
        chore_inst_ref = CHORE_INSTANCES.document(data.get('id'))
    
        chore_inst_ref.set(data)
        return jsonify({'id': data.get('id')})
    except Exception as e:
        print(f"Error creating/updating chore instance: {e}")
        return jsonify({'error': 'Could not upsert chore instance'}), 500


# /// Un-Implemented Functions /// #
    # These functions have been written, but aren't used
    # and haven't been tested.

def get_chore_instances_by_user(db, data):
    """
    Retrieves chore instances for a specific user within a date range.

    Args:
        db (firestore.Client): The Firestore client.
        data: json of user_id and house_id

    Returns:
        list: A list of chore instance dictionaries, or an empty list on error.
    """
    try:
        instances = []
        houses_ref = db.collection('houses')
        house_ref = houses_ref.document(data.get('house_id'))
        chore_instances_ref = house_ref.collection('choreInstances')

        query = chore_instances_ref.where(
            filter=firestore.FieldFilter('assignee', '==', data.get('user_id'))
        )
        results = query.get()
        for instance in results:
            instances.append(instance.to_dict())
        return instances
    except Exception as e:
        print(f"Error getting chore instances for user {data.get('user_id')} in house {data.get('house_id')}: {e}")
        return []
    
def get_chore_instances_by_house(db, data):
    """
    Retrieves chore instances for a specific user within a date range.

    Args:
        db (firestore.Client): The Firestore client.
        data: json of house_id

    Returns:
        list: A list of chore instance dictionaries, or an empty list on error.
    """
    try:
        instances = []
        CHORE_INSTANCES = db.collection('houses').document(data.house_id).collection('choreInstances')

        results = CHORE_INSTANCES.get()
        for doc in results:
            instances.append(doc.to_dict())
        return instances
    except Exception as e:
        print(f"Error getting chore instances for house {data.get('house_id')}: {e}")
        return []

def get_chore_instance(db, instance_id):
    """
    Retrieves a chore instance by its ID.

    Args:
        db (firestore.Client): The Firestore client.
        instance_id (str): The ID of the chore instance.

    Returns:
        dict: The chore instance data, or None if not found or on error.
    """
    try:
        instance_ref = db.collection('Task').document(instance_id)
        doc = instance_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"Chore instance with ID {instance_id} not found.")
            return None
    except Exception as e:
        print(f"Error getting chore instance: {e}")
        return None


def update_chore_instance(db, instance_id, updates):
    """
    Updates a chore instance.

    Args:
        db (firestore.Client): The Firestore client.
        instance_id (str): The ID of the chore instance to update.
        updates (dict): A dictionary of fields to update (e.g., {'completed': True}).

    Returns:
        bool: True on success, False on error.
    """
    try:
        instance_ref = db.collection('Task').document(instance_id)
        instance_ref.update(updates)
        return True
    except Exception as e:
        print(f"Error updating chore instance: {e}")
        return False


def get_chores_by_house(db, house_id):
    """
    Retrieves all chores for a given house.

    Args:
        db (firestore.Client): the Firestore Client
        house_id (str): the id of the house

    Returns:
        list(dict): A list of chore dictionaries
    """
    try:
        chores = []
        chores_ref = db.collection('Task')
        query = chores_ref.where('house_id', '==', house_id)
        results = query.get()
        for chore in results:
            chores.append(chore.to_dict())
        return chores
    except Exception as e:
        print(f"Error getting chores for house {house_id}: {e}")
        return []
