# Invisible Art Gallery - Architecture

This document outlines the architecture, components, and data models for the Invisible Art Gallery platform.

## System Architecture

The Invisible Art Gallery uses a client-server architecture with the following main components:

```
┌─────────────────┐     ┌───────────────────────────────────────┐
│                 │     │                                       │
│  React Frontend │◄────┤ Django Backend                        │
│  (SPA)          │────►│  ├── REST API                         │
│                 │     │  ├── WebSocket Server                 │
│                 │     │  ├── Encryption/Decryption Service    │
│                 │     │  └── Authentication                   │
└─────────────────┘     │                                       │
                        └───────────┬───────────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │                       │
                        │  PostgreSQL Database  │
                        │                       │
                        └───────────────────────┘
```

### Component Description

1. **React Frontend (SPA)**
   - User interface for both artists and viewers
   - Gallery browsing experience
   - Artist dashboard for uploads and condition management
   - Real-time updates via WebSocket connections
   - Optional AR.js integration for augmented reality experiences

2. **Django Backend**
   - RESTful API for data access and manipulation
   - User authentication and authorization
   - WebSocket server for real-time updates
   - Artwork encryption and decryption services
   - Condition checking and revelation logic

3. **PostgreSQL Database**
   - Stores user data, artwork metadata, and condition configurations
   - Encrypted artwork content
   - View counts and interaction metrics

## Data Models

### User
- id: UUID
- username: String
- email: String
- password: Hashed String
- profile_picture: Image (optional)
- bio: Text (optional)
- is_artist: Boolean
- created_at: DateTime
- updated_at: DateTime

### Artwork
- id: UUID
- title: String
- description: Text
- artist: ForeignKey(User)
- encrypted_content: Binary/Text
- placeholder_image: Image
- content_type: String (image/video/audio/etc.)
- is_revealed: Boolean
- reveal_conditions: JSON
- view_count: Integer
- created_at: DateTime
- updated_at: DateTime

### RevealCondition
- id: UUID
- artwork: ForeignKey(Artwork)
- condition_type: String (time/view_count/location/interactive)
- condition_value: JSON
- is_met: Boolean
- created_at: DateTime
- updated_at: DateTime

### ArtworkView
- id: UUID
- artwork: ForeignKey(Artwork)
- viewer: ForeignKey(User)
- viewed_at: DateTime
- ip_address: String
- device_info: JSON

### Comment
- id: UUID
- artwork: ForeignKey(Artwork)
- user: ForeignKey(User)
- content: Text
- created_at: DateTime
- updated_at: DateTime

## Authentication Flow

The platform uses JWT (JSON Web Tokens) for authentication:

1. User logs in with credentials
2. Backend validates and issues JWT token
3. Frontend stores token in secure storage
4. Token is included in API requests for authentication
5. WebSocket connections use token for authentication

## Encryption Process

### Encryption Flow (Upload)
1. Artist uploads artwork
2. Frontend sends artwork to backend
3. Backend generates encryption key
4. Content is encrypted using AES encryption
5. Encrypted content and key are stored in the database
6. Key is associated with unlock conditions

### Decryption Flow (Reveal)
1. Viewer accesses artwork
2. Backend checks if conditions are met
3. If conditions are met, backend decrypts content
4. Decrypted content is sent to frontend via secure channel
5. Frontend displays the revealed content

## Real-time Updates

WebSockets are used for real-time communication:

1. Frontend establishes WebSocket connection
2. Backend tracks artwork condition status
3. When conditions are met, backend sends update via WebSocket
4. Frontend receives update and reveals artwork

## Security Considerations

- All sensitive data is encrypted at rest and in transit
- AES encryption for artwork content
- HTTPS for all API communications
- JWT with appropriate expiration for authentication
- Rate limiting to prevent abuse
- Regular security audits and updates 