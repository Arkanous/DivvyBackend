import firebase_admin
from firebase_admin import credentials, firestore
import os

def get_firestore_db():
    """
    Retrieves the Firestore database client.

    Returns:
        firestore.Client: The Firestore client.  Returns None if initialization failed.
    """
    if firebase_admin._apps:
      return firestore.client()
    else:
      print("Firebase App not initialized.  Cannot get Firestore client.")
      return None
    