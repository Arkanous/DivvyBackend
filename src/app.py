# gateway.py (Flask Gateway)
from flask import Flask, request, jsonify
from utils import initialize_firebase, get_firestore_db
from routes import user_bp  # Import the user blueprint.
# Import the new user service blueprint
# from user_service.routes import user_bp
import os

app = Flask(__name__)

# Initialize Firebase
if initialize_firebase():
    db = get_firestore_db()
    app.config['FIRESTORE_DB'] = db  # Store the db in app.config
else:
    print("Failed to initialize Firebase.  Application may not function correctly.")

# Register the user blueprint. Mount it at /users
app.register_blueprint(user_bp, url_prefix='/users')
# Register the user service blueprint at /users.  Adjust the prefix as needed.
# app.register_blueprint(user_bp, url_prefix='/users') #ORIGINAL


@app.route('/')
def hello():
    return "Hello, Divvy App Gateway!"  # Make this distinct from the service


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
