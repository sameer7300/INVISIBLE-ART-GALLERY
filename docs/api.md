# Invisible Art Gallery - API Documentation

This document outlines the API endpoints available in the Invisible Art Gallery platform.

## Base URL

```
https://api.invisibleartgallery.com/v1/
```

Development:
```
http://localhost:8000/api/v1/
```

## Authentication

Most endpoints require authentication using JWT (JSON Web Tokens). Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

### Authentication Endpoints

#### POST /auth/register

Register a new user.

**Request Body:**
```json
{
  "username": "artlover",
  "email": "user@example.com",
  "password": "securepassword",
  "is_artist": true
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "artlover",
  "email": "user@example.com",
  "is_artist": true,
  "created_at": "2025-01-01T12:00:00Z"
}
```

#### POST /auth/login

Authenticate and receive a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "artlover",
    "email": "user@example.com",
    "is_artist": true
  }
}
```

#### POST /auth/refresh

Refresh an expired access token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## User Endpoints

#### GET /users/me

Get the authenticated user's profile.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "artlover",
  "email": "user@example.com",
  "is_artist": true,
  "profile_picture": "https://example.com/profiles/image.jpg",
  "bio": "Art enthusiast and occasional artist",
  "created_at": "2025-01-01T12:00:00Z"
}
```

#### PUT /users/me

Update the authenticated user's profile.

**Request Body:**
```json
{
  "username": "artlover2",
  "bio": "Updated bio information",
  "profile_picture": "[base64 encoded image]"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "artlover2",
  "email": "user@example.com",
  "is_artist": true,
  "profile_picture": "https://example.com/profiles/new_image.jpg",
  "bio": "Updated bio information",
  "created_at": "2025-01-01T12:00:00Z"
}
```

## Artwork Endpoints

#### GET /artworks

List all artworks with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `artist`: Filter by artist ID
- `revealed`: Filter by revelation status (true/false)

**Response (200 OK):**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/artworks?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Mystery Landscape",
      "description": "A landscape that reveals itself over time",
      "artist": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "artlover"
      },
      "placeholder_image": "https://example.com/placeholders/landscape.jpg",
      "content_type": "image/jpeg",
      "is_revealed": false,
      "view_count": 42,
      "created_at": "2025-01-02T12:00:00Z"
    },
    // More artworks...
  ]
}
```

#### POST /artworks

Upload a new artwork (requires artist role).

**Request Body (multipart/form-data):**
```
title: "Mystery Landscape"
description: "A landscape that reveals itself over time"
artwork_file: [binary file data]
placeholder_image: [binary file data]
content_type: "image/jpeg"
reveal_conditions: {
  "type": "view_count",
  "value": 100
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Mystery Landscape",
  "description": "A landscape that reveals itself over time",
  "artist": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "artlover"
  },
  "placeholder_image": "https://example.com/placeholders/landscape.jpg",
  "content_type": "image/jpeg",
  "is_revealed": false,
  "reveal_conditions": {
    "type": "view_count",
    "value": 100
  },
  "view_count": 0,
  "created_at": "2025-01-02T12:00:00Z"
}
```

#### GET /artworks/{id}

Get a specific artwork. Increments the view count if authenticated.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Mystery Landscape",
  "description": "A landscape that reveals itself over time",
  "artist": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "artlover"
  },
  "content": null,  // Will be populated if conditions are met
  "placeholder_image": "https://example.com/placeholders/landscape.jpg",
  "content_type": "image/jpeg",
  "is_revealed": false,
  "reveal_conditions": {
    "type": "view_count",
    "value": 100
  },
  "view_count": 43,
  "comments": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "username": "commentor"
      },
      "content": "Can't wait to see this revealed!",
      "created_at": "2025-01-03T12:00:00Z"
    }
  ],
  "created_at": "2025-01-02T12:00:00Z"
}
```

#### PUT /artworks/{id}

Update an artwork (artist owner only).

**Request Body:**
```json
{
  "title": "Updated Mystery Landscape",
  "description": "Updated description",
  "reveal_conditions": {
    "type": "view_count",
    "value": 200
  }
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Updated Mystery Landscape",
  "description": "Updated description",
  "artist": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "artlover"
  },
  "placeholder_image": "https://example.com/placeholders/landscape.jpg",
  "content_type": "image/jpeg",
  "is_revealed": false,
  "reveal_conditions": {
    "type": "view_count",
    "value": 200
  },
  "view_count": 43,
  "created_at": "2025-01-02T12:00:00Z",
  "updated_at": "2025-01-04T12:00:00Z"
}
```

#### DELETE /artworks/{id}

Delete an artwork (artist owner only).

**Response (204 No Content)**

## Comments Endpoints

#### POST /artworks/{id}/comments

Add a comment to an artwork.

**Request Body:**
```json
{
  "content": "This is an interesting concept!"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "artlover"
  },
  "content": "This is an interesting concept!",
  "created_at": "2025-01-05T12:00:00Z"
}
```

## WebSocket Endpoints

### Connection URL

```
wss://api.invisibleartgallery.com/ws/
```

Development:
```
ws://localhost:8000/ws/
```

### Authentication

Include the JWT token in the connection URL:

```
ws://localhost:8000/ws/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Channels

#### /artwork/{artwork_id}/

Subscribe to updates for a specific artwork. Receives messages when the artwork is revealed.

**Example message received:**
```json
{
  "type": "artwork_revealed",
  "artwork": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Mystery Landscape",
    "content": "https://example.com/revealed/landscape.jpg"
  },
  "timestamp": "2025-01-10T12:00:00Z"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid request parameters",
  "details": {
    "title": ["This field is required"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Authentication credentials were not provided or are invalid"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "The requested resource was not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
``` 