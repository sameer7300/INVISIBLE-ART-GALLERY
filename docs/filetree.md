# Invisible Art Gallery - Project File Structure

This document outlines the file structure for the Invisible Art Gallery project.

```
invisible-art-gallery/
│
├── docs/                           # Documentation
│   ├── README.md                   # Project overview
│   ├── TODO.md                     # Development tasks
│   ├── architecture.md             # System architecture
│   ├── installation.md             # Setup guide
│   ├── filetree.md                 # This file
│   ├── api.md                      # API documentation
│   └── troubleshooting.md          # Common issues and solutions
│
├── backend/                        # Django Backend
│   ├── manage.py                   # Django management script
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Example environment variables
│   │
│   ├── invisible_gallery/          # Main Django project
│   │   ├── __init__.py
│   │   ├── settings.py             # Project settings
│   │   ├── urls.py                 # URL routing
│   │   ├── asgi.py                 # ASGI config (WebSockets)
│   │   └── wsgi.py                 # WSGI config
│   │
│   ├── accounts/                   # User authentication app
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── models.py               # User model
│   │   ├── serializers.py          # User serializers
│   │   ├── views.py                # User views
│   │   └── tests.py
│   │
│   ├── artworks/                   # Artwork management app
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── models.py               # Artwork and condition models
│   │   ├── serializers.py          # Artwork serializers
│   │   ├── views.py                # Artwork views
│   │   └── tests.py
│   │
│   ├── encryption/                 # Encryption services
│   │   ├── __init__.py
│   │   ├── services.py             # Encryption/decryption logic
│   │   └── tests.py
│   │
│   └── websockets/                 # WebSocket handlers
│       ├── __init__.py
│       ├── consumers.py            # WebSocket consumers
│       ├── routing.py              # WebSocket routing
│       └── middleware.py           # WebSocket middleware
│
├── frontend/                       # React Frontend
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── index.js                # Entry point
│   │   ├── App.js                  # Main app component
│   │   ├── setupTests.js
│   │   │
│   │   ├── assets/                 # Static assets
│   │   │   ├── images/
│   │   │   └── styles/
│   │   │
│   │   ├── components/             # Reusable components
│   │   │   ├── common/
│   │   │   ├── layout/
│   │   │   └── artwork/
│   │   │
│   │   ├── context/                # React context providers
│   │   │   ├── AuthContext.js
│   │   │   └── WebSocketContext.js
│   │   │
│   │   ├── pages/                  # Page components
│   │   │   ├── Home.js
│   │   │   ├── Gallery.js
│   │   │   ├── ArtistDashboard.js
│   │   │   ├── ArtworkDetail.js
│   │   │   ├── Upload.js
│   │   │   └── Account.js
│   │   │
│   │   ├── services/               # API and service functions
│   │   │   ├── api.js              # API client
│   │   │   ├── auth.js             # Auth functions
│   │   │   ├── websocket.js        # WebSocket client
│   │   │   └── arService.js        # AR integration
│   │   │
│   │   └── utils/                  # Utility functions
│   │       ├── validation.js
│   │       └── formatting.js
│   │
│   ├── package.json                # NPM dependencies
│   ├── .env.example                # Example environment variables
│   └── README.md                   # Frontend documentation
│
├── scripts/                        # Utility scripts
│   ├── generate_keys.py            # Generate encryption keys
│   └── seed_data.py                # Seed database with sample data
│
├── .gitignore                      # Git ignore file
├── docker-compose.yml              # Docker Compose configuration
├── Dockerfile.backend              # Backend Docker config
├── Dockerfile.frontend             # Frontend Docker config
└── README.md                       # Project root README
```

## Notes on Structure

- **Backend**: Organized by Django apps (accounts, artworks, etc.) for modularity
- **Frontend**: Structured by feature with separation of components, pages, and services
- **Documentation**: Centralized in the docs folder
- **Docker**: Configuration for containerized development and deployment

This structure follows best practices for Django and React projects, with clear separation of concerns and modular organization. 