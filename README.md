# Divvy Backend - Chore Division App

This is the backend service for Divvy, a chore division application. It's built using Flask and interacts with a Firestore database. It also provides API endpoints through which the frontend communicates. The application is structured into three main services:

- **User Service:** Manages user data.
- **House Service:** Manages house/household data and member assignments.
- **Chore Service:** Manages chore definitions and chore instances (scheduled occurrences of chores).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Setting up the Frontend](#setting-up-the-frontend)
- [Running the System](#running-the-system)
- [Running as a Regular Flask App](#running-as-a-regular-flask-app)
- [Testing](#testing)
- [Debugging](#debugging)
- [API Endpoints](#api-endpoints)
- [Adding New Tests](#adding-new-tests)
- [How to Build a Release of the Software](#how-to-build-a-release-of-the-software)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+:** The application is written in Python 3.
- **pip:** Python's package installer.
- **Google Cloud SDK (Optional, for local Firestore emulator):** Required if you want to run a local Firestore emulator for development. See [Google Cloud SDK Installation](https://cloud.google.com/sdk/docs/install).
- **Firebase Admin SDK:** This is installed via pip.
- **Flask:** This is installed via pip.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <your_repository_url>
    cd <your_repository_directory>
    ```

2.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt  
    pip install --upgrade google-cloud-firestore  
    ```

    Note that if you're on a newer mac, you may need to run

    ```bash
    pip3 install -r requirements.txt  
    pip install --upgrade google-cloud-firestore  
    ```

## Configuration

The application requires a Firebase Admin SDK service account credentials file.

1.  **Obtain Firebase Admin SDK credentials:**

    - Go to the [Firebase Console](https://console.firebase.google.com/).
    - Select the Divvy project. If you do not see it, please contact acsparks@uw.edu.
    - Go to Project settings > Service accounts.
    - Under "Firebase Admin SDK", click "Generate new private key". If you're told that the max number of keys has been reached, please contact acsparks@uw.edu.
    - Download the JSON file containing your credentials.

2.  **Add the private key:**

    - Create a file called firebase-auth.json in ./src.
    - Paste the contents of the JSON file you downloaded into firebase-auth.json.
    - This is your personal private key. Make sure to never commit the contents of firebase-auth.json to the repository.

## Setting up the Frontend

1.  **Please see the frontend repository for instructions on setting up the frontend:** https://github.com/sonyaouthred/Divvy
2.  Tests for the backend will work just fine without the frontend, and you can still use curl to access endpoints, but if you would like to run the full app, you will obviously need the frontend.
3.  Note that with the current public release of the frontend repository, the Flask server and the frontend need to be running on the same machine for development. The actual iOS release connects to our Digital Ocean server (see [How to Build a Release of the Software](#how-to-build-a-release-of-the-software)). See [Running the System](#running-the-system) for how to start the Flask server.

## File layout
DivvyBackend/  
├── src/  
│   ├── houseService/           # Handles all house-related logic and database interactions  
│   │   ├── __init__.py  
│   │   ├── house_utils.py      # Utilities for house data processing  
│   │   └── houseUtilsTests.py  # Unit tests for userService  
│   ├── userService/            # Manages user accounts, profiles, and authentication  
│   │   ├── __init__.py  
│   │   ├── user_utils.py       # Utilities for user authentication  
│   │   └── userUtilsTests.py   # Unit tests for userService  
│   ├── choreService/           # Manages chore creation, assignment, and tracking  
│   │   ├── __init__.py  
│   │   ├── chore_utils.py      # Utilities for chore assignments  
│   │   └── choreUtilsTests.py  # Unit tests for userService  
│   ├── utils/                  # General utility functions, particularly for Firebase interactions  
│   │   ├── __init__.py  
│   │   └── firebase_utils.py  # Utility for Firebase database operations  
│   │   └── firebaseUtilsTests.py # Unit tests for userService  
│   ├── app.py                  # The main application entry point and API routes  
│   └── firebase-auth.json      # The private key through which Firebase is accessed (stored locally, not in repo)    
├── .gitignore                  # Files and directories to be ignored by Git  
├── requirements.txt            # Python dependencies  
└── README.md                   # This README file  

## Running the System

1.  **Run the Flask application:** (without env)

    ```bash
    cd ./src
    python app.py
    ```

    Or on Mac,

    ```bash
    cd ./src
    python3 app.py
    ```

    This will start the Flask development server, and your API will be accessible at `http://0.0.0.0:5000`.

## Running as a Regular Flask App (In case the first one doesn't work)

1.  **Set the `FLASK_APP` environment variable:**

    ```bash
    export FLASK_APP=app.py
    ```

2.  **Run the Flask application:**

    ```bash
    python -m flask run --host=0.0.0.0:5000
    ```

## Testing

The application includes unit tests. Here's how to run them:

1.  **Install pytest:**

    ```bash
    pip install pytest
    ```

2.  **Run the tests:** (do this from ./src/) Test files are found inside the choreService, userService, houseService, and utils folders.

    ```bash
    python -m pytest [path to test]
    ```

## Debugging

Here's how to debug the application using Visual Studio Code:

1.  **Set a breakpoint:** In VS Code, open the file you want to debug (e.g., a view function in one of the service files) and click in the left margin to set a breakpoint.

2.  **Open the Run and Debug view:** Click on the "Run and Debug" icon in the Activity Bar on the side of VS Code.

3.  **Select the "Pytest" configuration:** In the dropdown menu at the top of the Run and Debug view, select "Pytest".

    - If you don't see "Pytest", you may need to create a launch configuration. Click on the gear icon or the "create a launch.json file" link. Then, replace the contents of the `launch.json` file with the following:

      ```json
      {
        "version": "0.2.0",
        "configurations": [
          {
            "name": "Pytest",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
          },
          {
            "name": "Python Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
          }
        ]
      }
      ```

4.  **Start debugging:** Press the green "Start Debugging" button (or press F5). VS Code will run the tests, and when it hits your breakpoint, the execution will pause, allowing you to inspect variables and step through the code.

## API Endpoints

The frontend sends and receives data from the server via requests to the server's address. Different address URIs are routed to call different functions in the backend server based on these endpoints.

Endpoints outlined here give an example curl command to use, an example body, and an example response. Items in "<>" (e.g., <house_id>) are meant to be replaced with other data, usually an ID of some kind. Some example responses are too long to be reasonably fit into this README. Please see the frontend repository and the Firestore database for examples of expected output. Alternatively, use the provided curl command for that endpoint with a known house_id and observe the output.

POST /upsert-member-<house_id>
- Adds an existing user as a member to a house in the database's house collection. If the member already exists, then non-empty fields will be updated instead. The houseID field must be a valid house ID. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'houseID': 'aslkdf', 'id': 'zoiwern', 'chores': ['asdnzxpow8cx'], 'dateJoined': 'Thu, 01 May 2025 07:00:00 GMT', 'email': 'example@divvy.com', 'name': 'a Name', 'onTimePct': '82', 'profilePicture': 'lightGreen', 'subgroups': ['zxc0923n']}' http://127.0.0.1:5000/upsert-member-<house_id>
- Request body example:
            {
                'id': <member_id>,
                'chores': [
                    'asdnzxpow8cx'],
                'email': 'example@divvy.com',
                'name': 'a Name',
                'onTimePct': '82',
                'profilePicture': 'lightGreen',
                'subgroups': [
                    'zxc0923n']
            }
- Response: {'id': <member_id>}

POST /upsert-chore-instance-<house_id>
- Creates a new chore instance under a house in the database's house collection. If the chore instance already exists, then non-empty fields will be updated instead. The houseID field must be a valid house ID. The choreID field must a valid (super) chore ID of that house. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'assignee': <user_id>, 'choreID': "e79c266c-f1fc-4dd6-bc66-92595ae11f68", 'doneOnTime': false, 'dueDate': "Fri, 04 Jul 2025 18:59:59 GMT", 'id': "04a03063-95a5-46cc-a631-0f074a8ba441", 'isDone': false, 'swapID:' "" }' http://127.0.0.1:5000/upsert-chore-instance-<house_id>
- Request body example:
            {
              'assignee': <user_id>,
              'choreID': <chore_instance_id>,
              'doneOnTime': false,
              'dueDate': "Fri, 04 Jul 2025 18:59:59 GMT",
              'id': "04a03063-95a5-46cc-a631-0f074a8ba441",
              'isDone': false,
              'swapID:' ""
            }
  - Response: {'id': <chore_instance_id>}

POST /upsert-chore-<house_id>
- Creates a new chore under a house in the database's house collection. If the chore already exists, then non-empty fields will be updated instead. The houseID field must be a valid house ID. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'id': '12lcxzv', 'assignees': ['asdnzxvcie'], 'description': 'A useful desc.', 'emoji': '<emojiHere>', 'frequencyDays': ['3','7'], 'frequencyPattern': 'weekly', 'name': 'choreName', 'startDate': 'Thu, 01 May 2025 07:00:00 GMT'}' http://127.0.0.1:5000/upsert-chore-<house_id>
- Request body example:
            {
                'id': '12lcxzv',
                'assignees': [
                    'asdnzxvcie'],
                'description': 'A useful desc.',
                'emoji': '<emojiHere>',
                'frequencyDays': ['3','7'],
                'frequencyPattern': 'weekly',
                'name': 'choreName',
                'startDate': 'Thu, 01 May 2025 07:00:00 GMT'
            }
- Response: {'id': '12lcxzv'}

POST /get-user-chores
- Get a list of a user's chore instances from their house in the database's house collection.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"user_id": <user_id>, "house_id": <house_id>}' http://127.0.0.1:5000/get-user-chores
- Request body example: { "user_id": <user_id>, "house_id":  <house_id> }
- Response: [{'assignee': <user_id>, 'choreID': "e79c266c-f1fc-4dd6-bc66-92595ae11f68", 'doneOnTime': false, 'dueDate': "Fri, 04 Jul 2025 18:59:59 GMT", 'id': "04a03063-95a5-46cc-a631-0f074a8ba441", 'isDone': false, 'swapID:' "" }]

POST /get-current-day-user-chores
- Get a list of a user's chore instances from their house in the database's house collection for today.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"user_id": <user_id>, "house_id": <house_id>}' http://127.0.0.1:5000/get-current-day-user-chores
- Request body example: { "user_id": <user_id>, "house_id":  <house_id> }
- Response: [{'assignee': <user_id>, 'choreID': "e79c266c-f1fc-4dd6-bc66-92595ae11f68", 'doneOnTime': false, 'dueDate': "Fri, 04 Jul 2025 18:59:59 GMT", 'id': "04a03063-95a5-46cc-a631-0f074a8ba441", 'isDone': false, 'swapID:' "" }]

POST /get-house-chores
- Get a list of the chores in a house.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"house_id": <house_id>}' http://127.0.0.1:5000/get-house-chores
- Request body example: {"house_id": <house_id>}
- Response: [{
    "assignee": "wFbjmkmVVrXAWQPVHAv2sjCaMNu1",
    "choreID": "2be7dde8-06fe-4ad7-881e-d7b4ffc605e9",
    "doneOnTime": false,
    "dueDate": "Sat, 06 Sep 2025 18:59:59 GMT",
    "id": "fd2364e1-a4b7-4f97-924a-0e39cfaed6ef",
    "isDone": false,
    "swapID": ""
  },
  {
    "assignee": "wFbjmkmVVrXAWQPVHAv2sjCaMNu1",
    "choreID": "c16381d7-06e5-4989-b5b8-b6a078692580",
    "doneOnTime": false,
    "dueDate": "Thu, 18 Sep 2025 18:59:59 GMT",
    "id": "fea67adb-91b8-48ae-b763-cc6251b0152c",
    "isDone": false,
    "swapID": ""
  }]

POST /upsert-subgroup-<house_id>
- Creates a new subgroup under a house in the database's house collection. If the subgroup already exists, then non-empty fields will be updated instead.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"chores": ["e79c266c-f1fc-4dd6-bc66-92595ae11f68"], "id": <subgroup_id>, "members": ["Iqha69gogtMJQuoWitSVgQFqI6V2"], "name": "Upstairs", "profilePicture": "Blue"}' http://127.0.0.1:5000/upsert-subgroup-<house_id>
- Request body example: {"id": <subgroup_id>}
- Response: {"id": <subgroup_id>}

POST /upsert-swap-<house_id>
- Creates a new swap under a house in the database's house collection. If the swap already exists, then non-empty fields will be updated instead.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"id": <swap_id>, "choreID": <choreID_to_swap>, "choreInstID": <choreInstID_to_swap_with>, 'from': <request_from_member_id>, 'to': <request_to_member_id>, 'status': <swap_status>, 'offered': <choreInstID_offered_to_swap_with>}' http://127.0.0.1:5000/upsert-swap-<house_id>
- Request body example: {"id": <swap_id>, "choreID": <choreID_to_swap>, "choreInstID": <choreInstID_to_swap_with>, 'from': <request_from_member_id>, 'to': <request_to_member_id>, 'status': <swap_status>, 'offered': <choreInstID_offered_to_swap_with>}
- Response: {"id": <swap_id>}

POST /upsert-house
- Updates house data. If the house already exists, then fields will be updated instead.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'name': 'houseName', 'id': <house_id>, 'imageID': '', 'joinCode': 'ZsmLvSVz53', 'dateCreated': 'Tue, 20 May 2025 22:43:40 GMT'}' http://127.0.0.1:5000/upsert-house
- Request body example: {'name': 'houseName', 'id': <house_id>, 'imageID': '', 'joinCode': 'ZsmLvSVz53', 'dateCreated': 'Tue, 20 May 2025 22:43:40 GMT'}
- Response: {"id": <house_id>}

POST /upsert-user
- Creates a new user in the database's user collection. If the user already exists, then non-empty fields will be updated instead.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'email': 'example@gmail.com', 'houseID': 'alskdjfl', 'id': 'NisesS', 'name': 'John'}' http://127.0.0.1:5000/upsert-user
- Request body example: {'email': 'example@gmail.com', 'houseID': 'alskdjfl', 'id': 'NisesS', 'name': 'John'}
- Response: {"id": <user_id>}

POST /delete-user-<user_id>
- Deletes a user in the database's user collection. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{}' http://127.0.0.1:5000/delete-user-<user_id>
- Request body example: {}
- Response: {"id": <user_id>}

POST /delete-chore-<house_id>
- Deletes a chore in the database's house collection. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'id': <chore_id>}' http://127.0.0.1:5000/delete-chore-<house_id>
- Request body example: {'id': <chore_id>}
- Response: {'id': <chore_id>}

POST /delete-chore-instance-<house_id>
- Deletes a chore instance in the database's house collection. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'id': <chore_instance_id>}' http://127.0.0.1:5000/delete-chore-instance-<house_id>
- Request body example: {'id': <chore_instance_id>}
- Response: {'id': <chore_instance_id>}

POST /delete-subgroup-<house_id>
- Deletes a subgroup in the database's house collection. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'id': <subgroup_id>}' http://127.0.0.1:5000/delete-subgroup-<house_id>
- Request body example: {'id': <subgroup_id>}
- Response: {'id': <subgroup_id>}

POST /delete-swap-<house_id>
- Deletes a swap in the database's house collection. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'id': <swap_id>}' http://127.0.0.1:5000/delete-swap-<house_id>
- Request body example: {'id': <swap_id>}
- Response: {'id': <swap_id>}

POST /delete-member-<house_id>
- Deletes a member in the database's house collection. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'id': <member_id>}' http://127.0.0.1:5000/delete-member-<house_id>
- Request body example: {'id': <member_id>}
- Response: {'id': <member_id>}

POST /add-house
- Creates a new house in the database's houses collection.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{'house_id': '1', 'house_name': 'New House', 'creator_user_id': 'u123'}' http://127.0.0.1:5000/add-house
- Request Body: {'house_id': '1', 'house_name': 'New House', 'creator_user_id': 'u123'}
- Response: {'id': <house_id>}

POST /delete-house-<house_id>
- Deletes a house in the database's houses collection. Deletes all subcollections within. The id field must be non-empty.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{}' http://127.0.0.1:5000/delete-house-<house_id>
- Request Body: {}
- Response: {'id': <house_id>}

GET /get-house-<house_id>
- Retrieves a house document from the database's houses collection. If the ID does not exist in the database, returns None.
- Example:
  curl http://127.0.0.1:5000/get-house-<house_id>
- Response: The house as a json object. This one is a bit too long to document here and would only serve to clutter the README. Please refer to the frontend repository and the Firestore for examples.

GET /get-house-join-<join_code>
- Retrieves a house document from the database's houses collection with the matching join code.
- Example:
  curl http://127.0.0.1:5000/get-house-join-<join_code>
- Response: The matching house as a json object. This one is a bit too long to document here and would only serve to clutter the README. Please refer to the frontend repository and the Firestore for examples.

GET /get-user-<user_id>
- Retrieves a user's document from the database's users collection. If the user ID does not exist in the database, returns None.
- Example:
  curl http://127.0.0.1:5000/get-user-<user_id>
- Response: {'email': 'example@gmail.com', 'houseID': 'alskdjfl', 'id': <user_id>, 'name': 'John'}

GET /get-house-<house_id>-chores
- Retrieves a house's chores collection. Returns None if house_id is not in the database.
- Example:
  curl http://127.0.0.1:5000/get-house-<house_id>-chores
- Response: The list of all chores and their data for the house. This one is a bit too long to document here and would only serve to clutter the README. Please refer to the frontend repository and the Firestore for examples.

GET /get-house-<house_id>-swaps
- Retrieves a house's swaps collection. Returns None if house_id is not in the database.
- Example:
  curl http://127.0.0.1:5000/get-house-<house_id>-swaps
- Response: The list of all swaps and their data for the house. This one is a bit too long to document here and would only serve to clutter the README. Please refer to the frontend repository and the Firestore for examples.

GET /get-house-<house_id>-chore-instances
- Retrieves a house's chore instances collection. Returns None if house_id is not in the database.
- Example:
  curl http://127.0.0.1:5000/get-house-<house_id>-chore-instances
- Response: The list of all chore instances and their data for the house. This one is a bit too long to document here and would only serve to clutter the README. Please refer to the frontend repository and the Firestore for examples.

GET /get-house-<house_id>-members
- Retrieves a house's members collection. Returns None if house_id is not in the database.
- Example:
  curl http://127.0.0.1:5000/get-house-<house_id>-members
- Response: The list of all members and their data for the house. This one is a bit too long to document here and would only serve to clutter the README. Please refer to the frontend repository and the Firestore for examples.

GET /get-house-<house_id>-subgroups
- Retrieves a house's subgroups collection. Returns None if house_id is not in the database.
- Example:
  curl http://127.0.0.1:5000/get-house-<house_id>-subgroups
- Response: The list of all subgroups and their data for the house. This one is a bit too long to document here and would only serve to clutter the README. Please refer to the frontend repository and the Firestore for examples.

GET /get-house-<house_id>-subgroup-<subgroup_id>
- Retrieves a subgroup from a house. Returns None if house_id or subgroup_id is not in the database. 
- Example:
  curl http://127.0.0.1:5000/get-house-<house_id>-subgroup-<subgroup_id>
- Response: {"chores": ["e79c266c-f1fc-4dd6-bc66-92595ae11f68"], "id": <subgroup_id>, "members": ["Iqha69gogtMJQuoWitSVgQFqI6V2"], "name": "Upstairs", "profilePicture": "Blue"}

## Adding New Tests
- Create a test file inside the related folder you are unit testing.
- Go to .github\workflows\python-app.yml and add the command to run your test file to the run section at the bottom (i.e. python -m pytest ./choreService/choreServiceTests.py).
- For examples of existing tests, look at (inside ./src) ./houseService/houseServiceTests.py, ./choreService/choreServiceTests.py, and ./userService/userServiceTests.py.
- We use the unittest.mock Python library to mock the database for testing. Ensure that you have the following statements at the top of your test file:
```python
import unittest
from unittest.mock import MagicMock, patch
```

## How to Build a Release of the Software
1. Ask the owners to be added to our Digital Ocean Server  

2. ssh into the server through your terminal
```
ssh root@[server ip]
```

3. Start the virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

4. Go to the Divvy repo
```
cd DivvyBackend/
pip install -r requirements.txt
pip install --upgrade google-cloud-firestore  
```

5. Start the server (optional)
```
cd src/
gunicorn --bind 0.0.0.0:5000 app:app
```
You can now call the server at
```
http://[server ip]:5000
```

## Questions?
If you have questions, concerns, comments, or other queries, please feel free to contact acsparks@uw.edu.
