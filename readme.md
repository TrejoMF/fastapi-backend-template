# API

This is a very basic API that does very little.

## Setup

1. Clone the repository
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Set up environment variables:
    ```bash
    cp .env.example .env
    ```
4. Run the application:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
    ```

## API Usage

The API provides CRUD (Create, Read, Update, Delete) operations for users.

**Base URL:** `http://localhost:8080/api/v1` (or `http://127.0.0.1:8080/api/v1`)

### 1. Create User

*   **Endpoint:** `POST /users`
*   **Description:** Creates a new user.
*   **Request Body:** JSON object with `firstName`, `lastName`, `email`, `username`, and optional `phone`.
*   **Example:**
    ```bash
    curl -X POST "http://localhost:8080/api/v1/users/" \
         -H "Content-Type: application/json" \
         -d '{
              "firstName": "John",
              "lastName": "Doe",
              "email": "john.doe@example.com",
              "username": "johndoe",
              "phone": "123-456-7890"
            }'
    ```

### 2. Get All Users

*   **Endpoint:** `GET /users`
*   **Description:** Retrieves a list of all users. Supports pagination with `skip` and `limit` query parameters (defaults: `skip=0`, `limit=100`).
*   **Example:**
    ```bash
    curl -X GET "http://localhost:8080/api/v1/users/"
    ```
*   **Example with pagination:**
    ```bash
    curl -X GET "http://localhost:8080/api/v1/users/?skip=10&limit=5"
    ```

### 3. Get User by ID

*   **Endpoint:** `GET /users/{user_id}`
*   **Description:** Retrieves a specific user by their ID.
*   **Example (for user ID 1):**
    ```bash
    curl -X GET "http://localhost:8080/api/v1/users/1"
    ```

### 4. Update User

*   **Endpoint:** `PUT /users/{user_id}`
*   **Description:** Updates an existing user's information. Provide only the fields you want to change in the JSON body.
*   **Example (update first name and phone for user ID 1):**
    ```bash
    curl -X PUT "http://localhost:8080/api/v1/users/1" \
         -H "Content-Type: application/json" \
         -d '{
              "firstName": "Jane",
              "phone": "987-654-3210"
            }'
    ```

### 5. Delete User

*   **Endpoint:** `DELETE /users/{user_id}`
*   **Description:** Deletes a specific user by their ID.
*   **Example (for user ID 1):**
    ```bash
    curl -X DELETE "http://localhost:8080/api/v1/users/1"
    ```

**Note:** Replace `http://localhost:8080` with `http://127.0.0.1:8080` if needed.
