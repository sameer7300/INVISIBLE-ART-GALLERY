# Installation Guide

This guide provides detailed instructions for setting up the Invisible Art Gallery project in both development and production environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Running the Application](#running-the-application)
- [Production Setup](#production-setup)
  - [Docker Deployment](#docker-deployment)
  - [Manual Deployment](#manual-deployment)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [WebSocket Configuration](#websocket-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- Git
- Python 3.9+
- Node.js 16+
- npm or yarn
- PostgreSQL 13+
- Redis (for WebSockets in production)

## Development Setup

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sameer7300/INVISIBLE-ART-GALLERY.git
   cd invisible-art-gallery
   ```

2. Create a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   
6. Edit the `.env` file to configure your environment (see [Environment Variables](#environment-variables)).

7. Generate encryption keys (optional, but recommended):
   ```bash
   python scripts/generate_keys.py
   ```

8. Run database migrations:
   ```bash
   python manage.py migrate
   ```

9. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or if using yarn
   yarn install
   ```

3. Create a `.env` file for frontend configuration (if needed):
   ```bash
   cp .env.example .env
   ```

### Running the Application

1. Start the backend:
   ```bash
   # From the backend directory with virtual environment activated
   python manage.py runserver
   ```

2. Start the frontend (in a new terminal):
   ```bash
   # From the frontend directory
   npm start
   # or with yarn
   yarn start
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

## Production Setup

### Docker Deployment

The easiest way to deploy the application to production is using Docker and Docker Compose.

1. Clone the repository on your production server:
   ```bash
   git clone https://github.com/your-org/invisible-art-gallery.git
   cd invisible-art-gallery
   ```

2. Create a `.env` file for production with secure settings:
   ```bash
   cp backend/.env.example backend/.env
   ```
   
3. Edit the production environment variables as needed.

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

5. Create a superuser:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. The application should now be running at:
   - Frontend: http://your-server-ip
   - Backend API: http://your-server-ip/api
   - Admin interface: http://your-server-ip/admin

### Manual Deployment

For manual deployment, follow these steps:

#### Backend Deployment

1. Set up a production server with Python, PostgreSQL, and Redis.
2. Clone the repository and set up the virtual environment as described in the development setup.
3. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure a production `.env` file with appropriate settings.
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Collect static files:
   ```bash
   python manage.py collectstatic --no-input
   ```
7. Set up Gunicorn and Daphne (for WebSockets) behind Nginx or another reverse proxy.

#### Frontend Deployment

1. Build the production frontend assets:
   ```bash
   cd frontend
   npm install
   npm run build
   # or with yarn
   yarn build
   ```
2. Serve the built assets from the `frontend/build` directory using Nginx or another web server.

## Environment Variables

### Backend Environment Variables

Key environment variables for the backend:

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Debug mode (set to False in production) | `False` |
| `SECRET_KEY` | Django secret key (must be unique and secure) | `your-secret-key-here` |
| `ALLOWED_HOSTS` | Allowed hostnames | `example.com,www.example.com` |
| `DATABASE_URL` | Database connection string | `postgres://user:password@localhost:5432/db_name` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | `your-jwt-secret-key` |
| `ENCRYPTION_KEY` | Key for artwork encryption | `your-encryption-key-here` |
| `CHANNEL_LAYERS_HOST` | Redis host for WebSockets | `localhost` |
| `CHANNEL_LAYERS_PORT` | Redis port for WebSockets | `6379` |

### Frontend Environment Variables

Key environment variables for the frontend:

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | URL of the backend API | `https://api.example.com` |
| `REACT_APP_WS_URL` | WebSocket URL | `wss://api.example.com/ws` |

## Database Setup

The application uses PostgreSQL. To set up a new database:

1. Create a new PostgreSQL database:
   ```sql
   CREATE DATABASE invisible_art_gallery;
   CREATE USER gallery_user WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE invisible_art_gallery TO gallery_user;
   ```

2. Configure the database connection in the `.env` file:
   ```
   DATABASE_URL=postgres://gallery_user:your-password@localhost:5432/invisible_art_gallery
   ```

## WebSocket Configuration

For production, WebSockets require Redis as a channel layer:

1. Install Redis on your server.
2. Configure the channel layer in the `.env` file:
   ```
   CHANNEL_LAYERS_HOST=localhost
   CHANNEL_LAYERS_PORT=6379
   ```

## Troubleshooting

If you encounter issues during installation:

1. **Database connection errors**: Ensure PostgreSQL is running and the credentials are correct.
2. **WebSocket connection problems**: Check Redis configuration and firewall settings.
3. **Static files not loading**: Run `python manage.py collectstatic` and check your web server configuration.
4. **JWT token issues**: Verify the `JWT_SECRET_KEY` is set correctly.
5. **Encryption errors**: Check the `ENCRYPTION_KEY` is properly configured.

For more detailed troubleshooting, refer to the [Troubleshooting Guide](./troubleshooting.md). 