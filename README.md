# Divvy Backend - Chore Division App

This is the backend service for Divvy, a chore division application. It's built using Flask and interacts with a Firestore database. The application is structured into three main services (tentative):

* **User Service:** Manages user data.
* **House Service:** Manages house/household data and member assignments.
* **Chore Service:** Manages chore definitions and chore instances (scheduled occurrences of chores).

## Table of Contents

* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Configuration](#configuration)
* [Running the System](#running-the-system)
* [Running as a Regular Flask App](#running-as-a-regular-flask-app)
* [Testing](#testing)
* [Debugging](#debugging)
* [API Endpoints](#api-endpoints)
    * [User Service Endpoints](#user-service-endpoints)
    * [House Service Endpoints](#house-service-endpoints)
    * [Chore Service Endpoints](#chore-service-endpoints)

## Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.8+:** The application is written in Python 3.
* **pip:** Python's package installer.
* **Google Cloud SDK (Optional, for local Firestore emulator):** Required if you want to run a local Firestore emulator for development. See [Google Cloud SDK Installation](https://cloud.google.com/sdk/docs/install).
* **Firebase Admin SDK:** This is installed via pip.
* **Flask:** This is installed via pip.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <your_repository_url>
    cd <your_repository_directory>
    ```

2.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application requires a Firebase Admin SDK service account credentials file.

1.  **Obtain Firebase Admin SDK credentials:**
    * Go to the [Firebase Console](https://console.firebase.google.com/).
    * Select your project.
    * Go to Project settings > Service accounts.
    * Click "Generate new private key".
    * Download the JSON file containing your credentials.

2.  **Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:**
    * This environment variable should point to the path of your downloaded credentials JSON file.

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/serviceAccountKey.json" 
    set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\serviceAccountKey.json"
    ```

## Running the System 

1.  **Run the Flask application:** (Without env)

    ```bash
    cd ./src
    python app.py
    ```

    This will start the Flask development server, and your API will be accessible at `http://0.0.0.0:5000`.

## Running as a Regular Flask App (In case the first one doesnt work)

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

    * If you don't see "Pytest", you may need to create a launch configuration. Click on the gear icon or the "create a launch.json file" link. Then, replace the contents of the `launch.json` file with the following:

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
**NOTE: Not all endpoints are fully implemented yet. Please consult app.py to see which routes are currently implemented.**

### User Service Endpoints

* `GET /user/<user_id>`
    * Retrieves a user by their ID.
    * Example: `curl http://0.0.0.0:5000/user/some-user-id`
    * Response:

        ```json
        {
            "email": "user@example.com",
            "name": "Some User",
            "user_id": "some-user-id"
        }
        ```
* `POST /user`
    * Creates a new user.
    * Example:

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"email":"newuser@example.com","password":"password123","name":"New User"}' [http://0.0.0.0:5000/user](http://0.0.0.0:5000/user)
        ```
    * Request Body:

        ```json
        {
            "email": "user@example.com",
            "password": "password123",
            "name": "User Name"
        }
        ```
    * Response:

        ```json
        {
            "message": "User created successfully",
            "user_id": "new-user-id"
        }
        ```

### House Service Endpoints

* `POST /house`
    * Creates a new house.
    * Example:

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"name":"My House","creator_user_id":"user123"}' [http://0.0.0.0:5000/house](http://0.0.0.0:5000/house)
        ```
    * Request Body:

        ```json
        {
            "name": "House Name",
            "creator_user_id": "user-id"
        }
        ```
    * Response:

        ```json
        {
            "message": "House created successfully",
            "house_id": "house-id"
        }
        ```
* `GET /house/<house_id>`
    * Retrieves a house by its ID.
    * Example: `curl http://0.0.0.0:5000/house/some-house-id`
    * Response:

        ```json
        {
            "house_id": "some-house-id",
            "name": "Some House",
            "members": ["user1", "user2"]
        }
        ```
* `POST /house/<house_id>/members`
    * Adds a member to a house.
    * Example:

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"user_id":"user456"}' [http://0.0.0.0:5000/house/some-house-id/members](http://0.0.0.0:5000/house/some-house-id/members)
        ```
    * Request Body:

        ```json
        {
            "user_id": "user-id"
        }
        ```
    * Response:

        ```json
        {
            "message": "Member added successfully"
        }
        ```
* `GET /house/user/<user_id>`
    * Retrieves all houses a user is a member of.
    * Example: `curl http://0.0.0.0:5000/house/user/some-user-id`
    * Response:

        ```json
        [
            {
                "house_id": "house1",
                "name": "House One"
            },
            {
                "house_id": "house2",
                "name": "House Two"
            }
        ]
        ```

### Chore Service Endpoints

* `POST /chore`
    * Creates a new chore.
    * Example:

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"house_id":"house123","description":"Clean kitchen","assigned_to":["user1","user2"],"schedule_type":"weekly","schedule_data":{"day_of_week":"Monday"},"created_by":"user123"}' [http://0.0.0.0:5000/chore](http://0.0.0.0:5000/chore)
        ```
    * Request Body:

        ```json
        {
            "house_id": "house-id",
            "description": "Chore description",
            "assigned_to": ["user-id-1", "user-id-2"],
            "schedule_type": "daily" or "weekly" or "monthly",
            "schedule_data": { /* schedule-specific data */ },
            "created_by": "user-id",
            "subgroup_id": "optional-subgroup-id"
        }
        ```
    * Response:

        ```json
        {
            "message": "Chore created successfully",
            "chore_id": "chore-id"
        }
        ```
* `POST /chore/<chore_id>/instances`
    * Generates chore instances for a given chore.
    * Example:

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"start_date":"2024-01-01","end_date":"2024-01-31"}' [http://0.0.0.0:5000/chore/chore123/instances](http://0.0.0.0:5000/chore/chore123/instances)
        ```
    * Request Body:

        ```json
        {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        }
        ```
    * Response:

        ```json
        {
            "message": "Chore instances generated successfully",
            "instance_ids": ["instance-id-1", "instance-id-2"]
        }
        ```
* `GET /chore/user/<user_id>/instances`
    * Retrieves chore instances for a specific user within a date range.
    * Example:

        ```bash
        curl "[http://0.0.0.0:5000/chore/user/user123/instances?start_date=2024-01-15&end_date=2024-01-22](http://0.0.0.0:5000/chore/user/user123/instances?start_date=2024-01-15&end_date=2024-01-22)"
        ```
    * Query Parameters:
        * `start_date`: Start date (YYYY-MM-DD)
        * `end_date`: End date (YYYY-MM-DD)
    * Response:

        ```json
        [
            {
                "instance_id": "instance-id-1",
                "chore_id": "chore-id",
                "date": "YYYY-MM-DD",
                "status": "pending" or "completed"
            },
            // ...
        ]
        ```
* `GET /chore/instances/<instance_id>`
    * Retrieves a specific chore instance.
    * Example: `curl http://0.0.0.0:5000/chore/instances/instance123`
    * Response:

        ```json
        {
            "instance_id": "instance-id",
            "chore_id": "chore-id",
            "date": "YYYY-MM-DD",
            "status": "pending" or "completed"
        }
        ```
* `PUT /chore/instances/<instance_id>`
    * Updates a chore instance (e.g., to mark it as completed).
    * Example:

        ```bash
        curl -X PUT -H "Content-Type: application/json" -d '{"status":"completed"}' [http://0.0.0.0:5000/chore/instances/instance123](http://0.0.0.0:5000/chore/instances/instance123)
        ```
    * Request Body:

        ```json
        {
            "status": "completed"
        }
        ```
    * Response:

        ```json
        {
            "message": "Chore instance updated successfully"
        }
        ```
* `GET /chore/house/<house_id>`
    * Retrieves all chores for a given house.
    * Example: `curl http://0.0.0.0:5000/chore/house/house123`
    * Response:
        ```json
        [
            {
                "chore_id": "chore1",
                "description": "Clean the bathroom",
                "assigned_to": ["user1", "user2"],
                // ... other chore properties
            },
            {
                "chore_id": "chore2",
                "description": "Take out the trash",
                "assigned_to": ["user3"],
                // ... other chore properties
            }
        ]
        ```
