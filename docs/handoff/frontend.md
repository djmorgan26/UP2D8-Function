# Function App API Documentation

This document provides details on the function app API endpoints for the Up2D8 application.

## Endpoints

### 1. User Subscription

- **Endpoint:** `POST /api/users`
- **Description:** Creates a new user or updates an existing user's topics if the email already exists. Primarily used for newsletter subscriptions or initial user setup.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "topics": ["technology", "news"]
  }
  ```
- **Success Response:**
  ```json
  {
    "message": "Subscription confirmed." | "User already exists, topics updated.",
    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
  }
  ```
  }
  ```

### 2. User Management

*   **PUT /api/users/{user_id}**
    *   **Description:** Updates a user's preferences or topics.
    *   **Path Parameters:**
        *   `user_id` (string): The unique identifier of the user.
    *   **Request Body (application/json):** `UserUpdate`
        ```json
        {
            "topics": ["sports", "finance"],
            "preferences": {
                "newsletter_frequency": "weekly",
                "theme": "dark"
            }
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
            "message": "Preferences updated."
        }
        ```
    *   **Error Responses:**
        *   `400 Bad Request`: If no fields to update are provided.
        *   `404 Not Found`: If the `user_id` does not exist.

### 3. Chat Interaction

*   **POST /api/chat**
    *   **Description:** Stateless proxy to the Google Gemini API for chat interactions.
    *   **Request Body (application/json):** `ChatRequest`
        ```json
        {
            "prompt": "Tell me a joke."
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
            "text": "Why don't scientists trust atoms? Because they make up everything!"
        }
        ```
    *   **Error Responses:**
        *   `500 Internal Server Error`: If there's an issue with the Gemini API.

*   **POST /api/sessions**
    *   **Description:** Creates a new chat session for a user.
    *   **Request Body (application/json):** `SessionCreate`
        ```json
        {
            "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "title": "My first chat session"
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
            "session_id": "f1e2d3c4-b5a6-9876-5432-10fedcba9876"
        }
        ```

*   **GET /api/users/{user_id}/sessions**
    *   **Description:** Retrieves all chat sessions for a given user.
    *   **Path Parameters:**
        *   `user_id` (string): The unique identifier of the user.
    *   **Response (200 OK):**
        ```json
        [
            {
                "session_id": "f1e2d3c4-b5a6-9876-5432-10fedcba9876",
                "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "title": "My first chat session",
                "created_at": "2023-10-27T10:00:00.000Z",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello Gemini!",
                        "timestamp": "2023-10-27T10:01:00.000Z"
                    }
                ]
            }
        ]
        ```

*   **POST /api/sessions/{session_id}/messages**
    *   **Description:** Sends a new message within an existing chat session.
    *   **Path Parameters:**
        *   `session_id` (string): The unique identifier of the chat session.
    *   **Request Body (application/json):** `MessageContent`
        ```json
        {
            "content": "What is the capital of France?"
        }
        ```
    *   **Response (200 OK):**
        ```json
        {
            "message": "Message sent."
        }
        ```
    *   **Error Responses:**
        *   `404 Not Found`: If the `session_id` does not exist.

*   **GET /api/sessions/{session_id}/messages**
    *   **Description:** Retrieves all messages for a specific chat session.
    *   **Path Parameters:**
        *   `session_id` (string): The unique identifier of the chat session.
    *   **Response (200 OK):**
        ```json
        [
            {
                "role": "user",
                "content": "Hello Gemini!",
                "timestamp": "2023-10-27T10:01:00.000Z"
            },
            {
                "role": "model",
                "content": "Hello! How can I help you today?",
                "timestamp": "2023-10-27T10:01:05.000Z"
            }
        ]
        ```
    *   **Error Responses:**
        *   `404 Not Found`: If the `session_id` does not exist.

### 4. Feedback

*   **POST /api/feedback**
    *   **Description:** Records user feedback on chat messages or other interactions.
    *   **Request Body (application/json):** `FeedbackCreate`
        ```json
        {
            "message_id": "msg_12345",
            "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "rating": "good"
        }
        ```
    *   **Response (201 Created):**
        ```json
        {
            "message": "Feedback received."
        }
        ```

### 5. Analytics

*   **POST /api/analytics**
    *   **Description:** Logs various user interaction events for analytics purposes.
    *   **Request Body (application/json):** `AnalyticsEvent`
        ```json
        {
            "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "event_type": "page_view",
            "details": {
                "page": "/dashboard",
                "duration_ms": 5000
            }
        }
        ```
    *   **Response (202 Accepted):**
        ```json
        {
            "message": "Event logged."
        }
        ```

## 6. Data Models (Pydantic)

### `UserCreate`
```python
class UserCreate(BaseModel):
    email: EmailStr
    topics: list[str]
```

### `UserUpdate`
```python
class UserUpdate(BaseModel):
    topics: list[str] | None = None
    preferences: dict | None = None
```

### `ChatRequest`
```python
class ChatRequest(BaseModel):
    prompt: str
```

### `SessionCreate`
```python
class SessionCreate(BaseModel):
    user_id: str
    title: str
```

### `MessageContent`
```python
class MessageContent(BaseModel):
    content: str
```

### `FeedbackCreate`
```python
class FeedbackCreate(BaseModel):
    message_id: str
    user_id: str
    rating: str # e.g., "good", "bad", "neutral"
```

### `AnalyticsEvent`
```python
class AnalyticsEvent(BaseModel):
    user_id: str
    event_type: str
    details: dict
```

## 7. Error Handling

The API uses standard HTTP status codes for error reporting. Common error responses include:

*   `400 Bad Request`: Invalid request payload or missing required fields.
*   `404 Not Found`: Resource not found (e.g., invalid `user_id` or `session_id`).
    *   `500 Internal Server Error`: Unexpected server-side errors, often with a `detail` message.

## 8. Specific Notes for Function App Developers

*   **MongoDB Client:** The `get_db_client` dependency provides a MongoDB client. Ensure your function app can connect to MongoDB using the provided connection string (retrieved via Azure Key Vault).
*   **Secrets Management:** Utilize Azure Key Vault for managing sensitive information like the MongoDB connection string and Gemini API key, as demonstrated in `dependencies.py` and `shared/key_vault_client.py`.
    *   **Idempotency:** For operations that might be retried (e.g., analytics logging), consider implementing idempotency where appropriate to prevent duplicate data.

---
**Document Version:** 1.0
**Date:** November 4, 2025
