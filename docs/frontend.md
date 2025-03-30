# Frontend Documentation

This document provides an overview of the Invisible Art Gallery frontend architecture, component structure, and implementation details.

## Table of Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [State Management](#state-management)
- [Authentication Flow](#authentication-flow)
- [Styling and UI](#styling-and-ui)
- [Important Pages](#important-pages)
- [WebSocket Integration](#websocket-integration)
- [Custom Hooks](#custom-hooks)
- [Testing](#testing)

## Overview

The frontend for Invisible Art Gallery is built as a single-page application (SPA) using React with TypeScript. It provides a rich, interactive user interface for both artists and viewers to engage with invisible art. The application features a responsive design that works well on both desktop and mobile devices.

## Technology Stack

- **React**: Core UI library (v18)
- **TypeScript**: For type safety and improved developer experience
- **Material UI**: Component library for consistent, attractive UI elements
- **React Router**: For client-side routing
- **Axios**: For HTTP requests to the backend API
- **Formik & Yup**: For form handling and validation
- **React Context API**: For state management
- **WebSockets**: For real-time updates

## Project Structure

The frontend codebase is organized as follows:

```
frontend/
├── public/                 # Static assets and HTML template
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── layout/         # Layout components (Header, Footer, etc.)
│   │   ├── common/         # Common components used across pages
│   │   └── artwork/        # Artwork-specific components
│   ├── context/            # React context providers
│   │   └── AuthContext.tsx # Authentication context
│   ├── pages/              # Page components
│   │   ├── Home.tsx        # Landing page
│   │   ├── Gallery.tsx     # Artwork gallery
│   │   ├── ArtworkDetail.tsx # Individual artwork page
│   │   ├── Login.tsx       # Login page
│   │   ├── Register.tsx    # Registration page
│   │   ├── Profile.tsx     # User profile page
│   │   ├── Dashboard.tsx   # Artist dashboard
│   │   ├── Upload.tsx      # Artwork upload page
│   │   ├── TermsOfService.tsx # Terms of Service page
│   │   ├── PrivacyPolicy.tsx # Privacy Policy page
│   │   └── NotFound.tsx    # 404 page
│   ├── services/           # API services and utilities
│   │   ├── api.ts          # API client and endpoints
│   │   └── websocket.ts    # WebSocket connection handler
│   ├── types/              # TypeScript interfaces and types
│   ├── theme.ts            # Material UI theme configuration
│   ├── App.tsx             # Main app component with routes
│   └── index.tsx           # Application entry point
```

## Key Components

### Layout Components

- **Layout**: The main layout wrapper that includes Header and Footer
- **Header**: Navigation bar with user menu and mobile responsive design
- **Footer**: Site footer with copyright information and links to Terms and Privacy pages

### Common Components

- **ArtworkCard**: Displays an artwork preview in the gallery
- **CommentSection**: Displays and allows adding comments to artworks
- **LoadingSpinner**: Loading indicator
- **ErrorBoundary**: Error handling component
- **NotificationSnackbar**: Toast notifications

### Artwork-Related Components

- **ArtworkReveal**: Handles the reveal animation when conditions are met
- **RevealConditionDisplay**: Shows the conditions for revealing an artwork
- **ArtworkUploadForm**: Form for uploading and configuring artwork

## State Management

The application uses React Context API for global state management:

- **AuthContext**: Manages user authentication state, including:
  - User information
  - Authentication tokens
  - Login/logout functionality
  - Token refresh

Local component state is managed using React's `useState` and `useReducer` hooks where appropriate.

## Authentication Flow

1. **Login/Registration**: User submits credentials
2. **Token Storage**: JWT tokens are stored securely
3. **Authorization**: Auth tokens are sent with each API request
4. **Token Refresh**: Automatic refresh of expired tokens
5. **Logout**: Clears tokens and redirects to home

## Styling and UI

The UI is built with Material UI components and custom styling:

- **Theme**: Custom theme defined in `theme.ts` with primary and secondary colors
- **Responsive Design**: Mobile-first approach with responsive layouts
- **Animations**: Smooth transitions and reveal animations
- **Accessibility**: ARIA attributes and keyboard navigation

## Important Pages

### Home Page
- Hero section with animated background
- Featured artworks section
- How it works explanation
- Call-to-action sections

### Gallery Page
- Filter and search functionality
- Grid layout of artwork cards
- Pagination for browsing many artworks
- Sorting options

### Artwork Detail Page
- Artwork display (hidden or revealed based on conditions)
- Reveal conditions information
- Artist details
- Comments section
- Related artworks

### Artist Dashboard
- Overview of artist's artworks
- Analytics on views and interactions
- Management tools for artworks
- Upload new artwork button

### Terms of Service Page
- Modern, well-structured layout
- Table of contents with navigation
- Clearly formatted legal sections
- Visual elements for better readability
- Last updated timestamp

### Privacy Policy Page
- Similar modern design to Terms page
- Section navigation via sidebar
- Visual indicators for important information
- Contact information section
- Integration with overall site navigation

## WebSocket Integration

The frontend connects to the backend WebSocket server for real-time updates:

1. **Connection**: Established when viewing artworks or on the dashboard
2. **Authentication**: WebSocket connections are authenticated using JWT
3. **Event Handling**: Listeners for artwork reveals, comments, and notifications
4. **Reconnection**: Automatic reconnection if the connection is lost

## Custom Hooks

Several custom hooks simplify common operations:

- `useAuth()`: Access authentication context
- `useArtwork(id)`: Fetch and manage artwork data
- `useWebSocket()`: WebSocket connection management
- `useForm()`: Form handling with validation

## Testing

The frontend includes unit and integration tests:

- Component tests using React Testing Library
- API mocking with MSW (Mock Service Worker)
- Snapshot testing for UI components
- Integration tests for key user flows

## Build and Deployment

The frontend is built using standard Create React App scripts:

- `npm start`: Run development server
- `npm test`: Run tests
- `npm run build`: Create production build

The production build is optimized for performance with code splitting, minification, and asset optimization. 