# WebSockets Module for Invisible Art Gallery

This module provides real-time communication functionality for the Invisible Art Gallery application using Django Channels and WebSockets.

## Overview

WebSockets enable real-time bidirectional communication between clients and the server. In the Invisible Art Gallery, WebSockets are used for:

1. **Real-time artwork reveals**: When an artwork is revealed, all connected clients viewing that artwork receive an instant notification.
2. **User notifications**: Artists receive notifications about comments, views, and reveals of their artworks.
3. **Live engagement**: Enabling interactive experiences around the artwork revelation process.

## Components

### 1. Consumers

WebSocket consumers handle connections, messages, and disconnections:

- `ArtworkConsumer`: Handles connections to specific artworks, providing updates when they are revealed.
- `NotificationConsumer`: Handles user-specific notification streams.

### 2. Authentication Middleware

The `JWTAuthMiddleware` authenticates WebSocket connections using JWT tokens from the query parameters, ensuring secure real-time communication.

### 3. Event Handlers

The `WebSocketEventHandler` class provides methods to send notifications and updates via WebSockets:

- `notify_artwork_revealed`: Sends notifications when an artwork is revealed.
- `notify_new_comment`: Sends notifications when a new comment is added.
- `notify_new_view`: Sends notifications for artwork view milestones.
- `broadcast_system_message`: Sends system-wide announcements.

## WebSocket URLs

The module defines the following WebSocket endpoints:

- `/ws/artwork/<artwork_id>/`: For receiving updates about a specific artwork.
- `/ws/notifications/`: For receiving user-specific notifications (requires authentication).

## Connecting to WebSockets

### Artwork WebSocket

```javascript
// Connect to an artwork's WebSocket
const socket = new WebSocket(`ws://example.com/ws/artwork/${artworkId}/`);

// Handle messages
socket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  
  if (data.type === 'artwork_revealed') {
    // The artwork has been revealed!
    // Update the UI accordingly
  }
};
```

### Notifications WebSocket (Authenticated)

```javascript
// Connect to the notifications WebSocket with JWT token
const socket = new WebSocket(`ws://example.com/ws/notifications/?token=${jwtToken}`);

// Handle notifications
socket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  
  if (data.type === 'notification') {
    // Display the notification
    showNotification(data.message);
  }
};
```

## Message Types

### Artwork WebSocket Messages

1. `artwork_status`: Sent when connecting, provides the current status of the artwork.
   ```json
   {
     "type": "artwork_status",
     "is_revealed": false,
     "artwork": {
       "id": "uuid-here",
       "title": "Artwork Title"
     }
   }
   ```

2. `artwork_revealed`: Sent when an artwork is revealed.
   ```json
   {
     "type": "artwork_revealed",
     "artwork": {
       "id": "uuid-here",
       "title": "Artwork Title",
       "artist": "Artist Name",
       "is_revealed": true
     }
   }
   ```

### Notification WebSocket Messages

1. `welcome`: Sent when connection is established.
   ```json
   {
     "type": "welcome",
     "message": "Connected to notification service"
   }
   ```

2. `notification`: Sent when there is a notification for the user.
   ```json
   {
     "type": "notification",
     "message": "New comment on your artwork",
     "data": {
       "type": "new_comment",
       "artwork_id": "uuid-here",
       "comment_id": "uuid-here",
       "user": "Commenter Username"
     }
   }
   ```

## Integration with Artwork Views

The WebSockets functionality is integrated with the artwork views in the following ways:

1. When an artwork is revealed (due to view count, time, or interactive conditions), a WebSocket notification is sent.
2. When a new comment is added to an artwork, a notification is sent to the artist.
3. When an artwork reaches view milestones (10, 50, 100, etc.), a notification is sent to the artist.

## Testing WebSockets

The module includes tests for WebSocket functionality:

- Testing connection to the `ArtworkConsumer`
- Testing connection with non-existent artwork IDs
- Testing authenticated connections to the `NotificationConsumer`
- Testing unauthenticated connections to the `NotificationConsumer`

Run the tests with:

```bash
python manage.py test websockets
```

## Example Client Code

See `scripts/websocket_client_example.js` for a complete example of how to connect to and use the WebSocket endpoints from a JavaScript client.

## Security Considerations

- WebSocket connections to the notification endpoint require authentication via JWT token.
- The JWT token is passed as a query parameter and validated by the `JWTAuthMiddleware`.
- Artwork data sent via WebSockets does not include the encrypted content, only metadata.

## Dependencies

- Django Channels
- Channels Redis (for production deployments)
- Django REST Framework Simple JWT (for authentication) 