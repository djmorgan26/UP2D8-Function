# Frontend Pass-off for UP2D8 Automated Tasks Service

This document outlines the key integration points and data structures the frontend application needs to be aware of to work seamlessly with the UP2D8 Automated Tasks Service (Azure Functions) and its associated backend.

## 1. User Profile Management

The frontend will need to provide an interface for users to manage their preferences, which are stored in the Cosmos DB `users` collection. The backend is expected to expose API endpoints for these operations.

### User Data Structure (Cosmos DB `users` collection)

```json
{
    "id": "<unique_user_id>",
    "email": "user@example.com",
    "subscribed_tags": ["Tech", "AI", "Science"], // List of tags the user is interested in
    "preferences": "concise" // or "detailed", controls newsletter length/style
    // ... other user-specific fields
}
```

### Frontend Responsibilities:

*   **Display/Edit Subscribed Tags:** Allow users to view and modify their list of `subscribed_tags`.
*   **Display/Edit Preferences:** Allow users to select their newsletter `preferences` (e.g., concise, detailed).
*   **Subscription Status:** Provide mechanisms for users to subscribe or unsubscribe from the service.

### Backend API Endpoints (Expected):

The frontend will interact with the backend to perform CRUD operations on user profiles. Examples of expected endpoints:

*   `POST /api/users/subscribe`: To create a new user subscription.
*   `PUT /api/users/{userId}/preferences`: To update user preferences (tags, format).
*   `DELETE /api/users/{userId}/unsubscribe`: To remove a user subscription.

## 2. Newsletter Display

The `NewsletterGenerator` function produces personalized newsletters in HTML format. The frontend will be responsible for displaying this HTML content to the user.

### Newsletter Content:

*   Newsletters will be delivered to the user's email address as HTML. The frontend might display past newsletters if the backend stores them.
*   The HTML content will be fully formatted and ready for rendering.

## 3. General Considerations

*   **Authentication & Authorization:** The frontend should handle user authentication and ensure that user profile management requests are properly authorized by the backend.
*   **Error Handling:** Display user-friendly error messages for any issues encountered during API interactions.
*   **Loading States:** Implement appropriate loading indicators during data fetching and submission.
