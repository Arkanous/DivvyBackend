# Divvy Backend - Chore Division App

This is the backend service for Divvy, a chore division application. It's built using Flask and interacts with a Firestore database. The application is structured into three main services (tentative):

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
  - [User Service Endpoints](#user-service-endpoints)
  - [House Service Endpoints](#house-service-endpoints)
  - [Chore Service Endpoints](#chore-service-endpoints)
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

**NOTE: This section was recently updated. If you had previously been instructed to skip it, please follow it now.**

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
3.  Note that with the current release, the Flask server and the frontend need to be running on the same machine. This will change. See the next step for how to start the server.

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
│   └── app.py                  # The main application entry point and API routes  
├── .gitignore                  # Files and directories to be ignored by Git  
├── requirements.txt            # Python dependencies  
└── README.md                   # This README file  

## Running the System

1.  **Run the Flask application:** (Without env)

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

**NOTE: Not all endpoints are fully implemented yet. Please consult app.py to see documentation for the routes that are currently implemented. Below is a list of those endpoints:**

POST /upsert-user
- Creates or updates a user.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"email":"test@example.com","id":"user123","houseID":"house456"}' http://127.0.0.1:5000/upsert-user
- Request Body:
  {
    "email": "test@example.com",
    "id": "user123",
    "houseID": "house456"
  }
- Response:
  {
    "message": "User upserted successfully"
  }

POST /add-house
- Creates a new house.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"name":"My New House","id":"house456"}' http://127.0.0.1:5000/add-house
- Request Body:
  {
    "name": "My New House",
    "id": "house456"
  }
- Response:
  {
    "message": "House created successfully"
  }

POST /add-chore
- Creates a new chore.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"name":"Take out trash","id":"chore789","houseID":"house456","description":"Take the trash out to the curb","points":10}' http://127.0.0.1:5000/add-chore
- Request Body:
  {
    "name": "Take out trash",
    "id": "chore789",
    "houseID": "house456",
    "description": "Take the trash out to the curb",
    "points": 10
  }
- Response:
  {
    "message": "Chore created successfully"
  }

POST /add-chore-instance
- Creates a new chore instance.
- Example:
  curl -X POST -H "Content-Type: application/json" -d '{"choreID":"chore789","assignedTo":"user123","dueDate":"2025-06-01T12:00:00Z","status":"pending","id":"instance123"}' http://127.0.0.1:5000/add-chore-instance
- Request Body:
  {
    "choreID": "chore789",
    "assignedTo": "user123",
    "dueDate": "2025-06-01T12:00:00Z",
    "status": "pending",
    "id": "instance123"
  }
- Response:
  {
    "message": "Chore instance created successfully"
  }

GET /house/<house_id>/chores
- Gets all chores in a house.
- Example:
  curl http://127.0.0.1:5000/house/house456/chores
- Response:
  [
    {
      "id": "chore789",
      "name": "Take out trash",
      "description": "Take the trash out to the curb",
      "points": 10
    }
  ]

GET /house/<house_id>/chore-instances
- Gets all chore instances in a house.
- Example:
  curl http://127.0.0.1:5000/house/house456/chore-instances
- Response:
  [
    {
      "id": "instance123",
      "choreID": "chore789",
      "assignedTo": "user123",
      "dueDate": "2025-06-01T12:00:00Z",
      "status": "pending"
    }
  ]

PUT /chore/instances/<instance_id>
- Updates a chore instance (e.g., to mark it as completed).
- Example:
  curl -X PUT -H "Content-Type: application/json" -d '{"status":"completed"}' http://0.0.0.0:5000/chore/instances/instance123
- Request Body:
  {
    "status": "completed"
  }
- Response:
  {
    "message": "Chore instance updated successfully"
  }

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
