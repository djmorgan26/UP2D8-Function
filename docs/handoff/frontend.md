# Function App API Documentation

This document provides details on the function app API endpoints for the Up2D8 application.

## Endpoints

### 1. Subscribe to Topics

- **Endpoint:** `POST /api/subscribe`
- **Description:** This endpoint subscribes a user to specified topics.
- **Request Body:**
  ```json
  {
    "email": "string",
    "topics": ["string"]
  }
  ```
- **Success Response:**
  ```json
  {
    "message": "string"
  }
  ```
- **Error Response:**
  ```json
  {
    "message": "string"
  }
  ```
