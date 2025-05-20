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
    
def upsert_member(db, data):
    # TODO: check to make sure the user exists already
    try:
        HOUSES = db.collection('houses')
        house_ref = HOUSES.document(data.get('houseID'))
        
        MEMBERS = house_ref.collection('members')
        member_ref = MEMBERS.document(data.get('id'))
        member = member_ref.get()

        member_dict = {}
        if (member.exists):
            member_dict = member.to_dict()

        id = data.get('id')

        chores = data.get('chores')
        if (member.exists and chores == ''):
            chores = member_dict['chores']
        
        dateJoined = data.get('dateJoined')
        if (member.exists and dateJoined == ''):
            dateJoined = member_dict['dateJoined']
        
        email = data.get('email')
        if (member.exists and email == ''):
            email = member_dict['email']

        name = data.get('name')
        if (member.exists and name == ''):
            name = member_dict['name']

        onTimePct = data.get('onTimePct')
        if (member.exists and onTimePct == ''):
            onTimePct = member_dict['onTimePct']

        profilePicture = data.get('profilePicture')
        if (member.exists and profilePicture == ''):
            profilePicture = member_dict['profilePicture']

        subgroups = data.get('subgroups')
        if (member.exists and subgroups == ''):
            subgroups = member_dict['subgroups']


        member_data = {
            'id': id,
            'chores': chores,
            'dateJoined': dateJoined,
            'email': email,
            'name': name,
            'onTimePct': onTimePct,
            'profilePicture': profilePicture,
            'subgroups': subgroups
        }

        member_ref.set(member_data)
        return id

    except Exception as e:
        print(f"Error creating/updating user: {e}")
        return None

def upsert_user(db, data):
    try:
        USERS = db.collection('users')
        user_ref = USERS.document(data.get('id'))
        user = user_ref.get()
        user_dict = {}
        if (user.exists):
            user_dict = user.to_dict()

        email = data.get('email')
        if (user.exists and email == ''):
            email = user_dict['email']
        houseID = data.get('houseID')
        if (user.exists and houseID == ''):
            houseID = user_dict['houseID']
        id = data.get('id')
        if (user.exists and id == ''):
            id = user_dict['id']
        
        user_data = {
            'email': email,
            'houseID': houseID,
            'id': id
        }

        user_ref.set(user_data)
        return id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None