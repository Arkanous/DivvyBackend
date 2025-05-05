# IGNORE THIS FOR NOW

from flask import Flask, request, jsonify
from utils import initialize_firebase, get_firestore_db
import os

app = Flask(__name__)

# Initialize Firebase
if initialize_firebase():
    db = get_firestore_db()
    app.config['FIRESTORE_DB'] = db 
else:
    print("Failed to initialize Firebase.  Application may not function correctly.")


@app.route('/')
def hello():
    return "Hello, Divvy App Gateway!"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
