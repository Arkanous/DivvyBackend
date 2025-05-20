from firebase_admin import firestore
from datetime import datetime
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY

def upsert_chore_instance(db, data):
    # TODO: lots to do here, but definitely need to make sure that choreID is valid
    try:
        HOUSES = db.collection('houses')
        house_ref = HOUSES.document(data.get('houseID'))

        CHORE_INSTANCES = house_ref.collection('choreInstances')
        chore_inst_ref = CHORE_INSTANCES.document(data.get('id'))
        chore_inst = chore_inst_ref.get()

        chore_inst_dict = {}
        if (chore_inst.exists):
            chore_inst_dict = chore_inst.to_dict()

        id = data.get('id')

        assignee = data.get('assignee')
        if (chore_inst.exists and assignee == ''):
            assignee = chore_inst_dict['assignee']
        
        dueDate = data.get('dueDate')
        if (chore_inst.exists and dueDate == ''):
            dueDate = chore_inst_dict['dueDate']

        isDone = data.get('isDone')
        if (chore_inst.exists and isDone == ''):
            isDone = chore_inst_dict['isDone']

        chore_inst_data = {
            'id': id,
            'assignee': assignee,
            'dueDate': dueDate,
            'isDone': isDone
        }
    
        chore_inst_ref.set(chore_inst_data)
        return id

    except Exception as e:
        print(f"Error creating/updating user: {e}")
        return None
    

def upsert_chore(db, data):
    try:
        HOUSES = db.collection('houses')
        house_ref = HOUSES.document(data.get('houseID'))

        CHORES = house_ref.collection('chores')
        chore_ref = CHORES.document(data.get('choreID'))
        chore = chore_ref.get()

        chore_dict = {}
        if (chore.exists):
            chore_dict = chore.to_dict()
        
        id = data.get('choreID')
        if (chore.exists and id == ''):     # useless
            id = chore_dict['id']

        assignees = data.get('assignees')
        if (chore.exists and assignees == ''):      # not sure how to check for empty table []
            assignees = chore_dict['assignees']
        
        desc = data.get('description')
        if (chore.exists and desc == ''):
            desc = chore_dict['description']

        emoji = data.get('emoji')
        if (chore.exists and emoji == ''):
            emoji = chore_dict['emoji']

        freqDays = data.get('frequencyDays')
        if (chore.exists and freqDays == ''):
            freqDays = chore_dict['frequencyDays']

        freqPattern = data.get('frequencyPattern')
        if (chore.exists and freqPattern == ''):        # same issue here
            freqPattern = chore_dict['frequencyPattern']

        name = data.get('name')
        if (chore.exists and name == ''):
            name = chore_dict['name']

        startDate = data.get('startDate')
        if (chore.exists and startDate == ''):
            startDate = chore_dict['startDate']

        chore_data = {
            'id': id,
            'assignees': assignees,
            'description': desc,
            'emoji': emoji,
            'frequencyDays': freqDays,
            'frequencyPattern': freqPattern,
            'name': name,
            'startDate': startDate
        }
    
        chore_ref.set(chore_data)
        return id
    except Exception as e:
        print(f"Error creating/updating user: {e}")
        return None

def create_chore(db, house_id, description, assigned_to, schedule_type, schedule_data, created_by, subgroup_id=None):
    """
    Creates a new chore in Firestore.

    Args:
        db (firestore.Client): The Firestore client.
        house_id (str): The ID of the house the chore belongs to.
        description (str): The description of the chore.
        assigned_to (list): A list of user IDs assigned to the chore.
        schedule_type (str): The type of schedule ('once', 'daily', 'weekly', 'monthly').
        schedule_data (dict):  Schedule-specific data (e.g., {'date': datetime}, {'day_of_week': 0-6}, {'day_of_month': 1-31}).
        created_by (str): The user ID of the creator
        subgroup_id (str, optional): The ID of the subgroup the chore belongs to. Defaults to None.

    Returns:
        str: The ID of the newly created chore, or None on error.
    """
    try:
        chore_ref = db.collection('Task').document()
        chore_id = chore_ref.id
        chore_data = {
            'house_id': house_id,
            'description': description,
            'assigned_to': assigned_to,
            'schedule_type': schedule_type,
            'schedule_data': schedule_data,
            'created_at': firestore.SERVER_TIMESTAMP,
            'created_by': created_by,
            'subgroup_id': subgroup_id,
            'name': description,
            'is_active': True
        }
        chore_ref.set(chore_data)
        return chore_id
    except Exception as e:
        print(f"Error creating chore: {e}")
        return None



def generate_chore_instances(db, chore_id, start_date, end_date):
    """
    Generates chore instances for a given chore within a date range.

    Args:
        db (firestore.Client): The Firestore client.
        chore_id (str): The ID of the chore.
        start_date (datetime): The start date for generating instances.
        end_date (datetime): The end date for generating instances.

    Returns:
        list: A list of IDs of the generated chore instances, or an empty list on error.
    """
    try:
        chore_ref = db.collection('Task').document(chore_id)
        chore_doc = chore_ref.get()
        if not chore_doc.exists:
            print(f"Chore with ID {chore_id} not found.")
            return []

        chore_data = chore_doc.to_dict()
        schedule_type = chore_data['schedule_type']
        schedule_data = chore_data['schedule_data']
        assigned_to = chore_data['assigned_to']

        instance_ids = []
        if schedule_type == 'once':
            chore_date = schedule_data.get('date')
            if chore_date and start_date <= chore_date <= end_date:
                instance_ref = db.collection('Task').document()
                instance_id = instance_ref.id
                instance_data = {
                    'chore_id': chore_id,
                    'date': chore_date,
                    'completed': False,
                    'assigned_to': assigned_to,
                }
                instance_ref.set(instance_data)
                instance_ids.append(instance_id)
        elif schedule_type == 'daily':
            dates = list(rrule(DAILY, dtstart=start_date, until=end_date))
            for chore_date in dates:
                instance_ref = db.collection('Task').document()
                instance_id = instance_ref.id
                instance_data = {
                    'chore_id': chore_id,
                    'date': chore_date,
                    'completed': False,
                    'assigned_to': assigned_to,
                }
                instance_ref.set(instance_data)
                instance_ids.append(instance_id)
        elif schedule_type == 'weekly':
            day_of_week = schedule_data.get('day_of_week')
            if day_of_week is not None:
                dates = list(rrule(WEEKLY, dtstart=start_date, until=end_date, byweekday=day_of_week))
                for chore_date in dates:
                    instance_ref = db.collection('Task').document()
                    instance_id = instance_ref.id
                    instance_data = {
                        'chore_id': chore_id,
                        'date': chore_date,
                        'completed': False,
                        'assigned_to': assigned_to,
                    }
                    instance_ref.set(instance_data)
                    instance_ids.append(instance_id)
        elif schedule_type == 'monthly':
            day_of_month = schedule_data.get('day_of_month')
            if day_of_month is not None:
                dates = list(rrule(MONTHLY, dtstart=start_date, until=end_date, bymonthday=day_of_month))
                for chore_date in dates:
                    instance_ref = db.collection('Task').document()
                    instance_id = instance_ref.id
                    instance_data = {
                        'chore_id': chore_id,
                        'date': chore_date,
                        'completed': False,
                        'assigned_to': assigned_to,
                    }
                    instance_ref.set(instance_data)
                    instance_ids.append(instance_id)
        else:
            print(f"Invalid schedule type: {schedule_type}")
            return []
        return instance_ids
    except Exception as e:
        print(f"Error generating chore instances: {e}")
        return []


def get_chore_instances_by_user(db, user_id, start_date, end_date):
    """
    Retrieves chore instances for a specific user within a date range.

    Args:
        db (firestore.Client): The Firestore client.
        user_id (str): The ID of the user.
        start_date (datetime): The start date for the query.
        end_date (datetime): The end date for the query.

    Returns:
        list: A list of chore instance dictionaries, or an empty list on error.
    """
    try:
        instances = []
        instances_ref = db.collection('Task')
        #  query for instances assigned to the user AND within the date range.
        query = instances_ref.where('assigned_to', '==', user_id).where('date', '>=', start_date).where('date', '<=', end_date)
        results = query.get()
        for instance in results:
            instances.append(instance.to_dict())
        return instances
    except Exception as e:
        print(f"Error getting chore instances for user {user_id}: {e}")
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
