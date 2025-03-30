# Invisible Art Gallery

A modern platform where artists upload "invisible" creations that reveal themselves only under specific conditions.

![Invisible Art Gallery](https://via.placeholder.com/1200x600?text=Invisible+Art+Gallery)

## ✨ Overview

The Invisible Art Gallery is a fully functional platform where artists can upload works that are initially "invisible" to viewers. These artworks reveal themselves only when specific conditions are met, such as:

- After reaching a certain number of views
- At a specific date and time
- When a specific interaction threshold is met
- In specific physical locations (via AR)

This concept creates anticipation, exclusivity, and a novel experience for both artists and viewers.

## 🚀 Key Features

- **Conditional Art Revelation**: Set custom conditions for when your art becomes visible
- **Real-time Updates**: Witness art reveal itself in real-time via WebSockets
- **Secure Encryption**: All artwork is securely encrypted until conditions are met
- **Artist Dashboard**: Manage your invisible art portfolio and track reveal metrics
- **Social Interaction**: Comment on and share invisible artworks
- **Optional AR Integration**: Reveal art in augmented reality at specific locations
- **Modern UI**: Beautifully designed user interface with smooth transitions and animations
- **Legal Compliance**: Comprehensive Terms of Service and Privacy Policy pages

## 🛠️ Technology Stack

- **Backend**: Django REST Framework, Django Channels
- **Frontend**: React.js with TypeScript, Material-UI
- **Database**: PostgreSQL
- **Real-time Communication**: WebSockets
- **Encryption**: AES via Python's cryptography libraries
- **Optional AR**: AR.js integration
- **Authentication**: JWT with refresh tokens
- **Deployment**: Docker, AWS/Heroku

## 🏃‍♂️ Getting Started

See our comprehensive documentation in the `docs` folder:

- [Installation Guide](docs/installation.md)
- [Development Guide](docs/development.md)
- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/invisible-art-gallery.git
cd invisible-art-gallery

# Start the application with Docker Compose
docker-compose up -d

# The application will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Running Locally (Development)

#### Frontend
```bash
cd frontend
npm install
npm start
# Frontend will be available at http://localhost:3000
```

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# Backend will be available at http://localhost:8000
```

## 📂 Project Structure

The project follows a Django + React architecture:

```
invisible-art-gallery/
├── backend/              # Django REST API backend
│   ├── accounts/         # User authentication and profiles
│   ├── artworks/         # Artwork management and conditions
│   ├── encryption/       # Content encryption/decryption service
│   ├── websockets/       # Real-time communication
│   └── invisible_gallery/# Project settings and config
├── frontend/             # React SPA frontend
│   ├── public/           # Static assets
│   └── src/              # React source code
│       ├── components/   # Reusable UI components
│       ├── context/      # React contexts (auth, etc.)
│       ├── pages/        # Page components
│       ├── services/     # API and WebSocket services
│       └── types/        # TypeScript interfaces
└── docs/                 # Documentation
```

## 👥 Contributing

We welcome contributions! Please read our [Development Guide](docs/development.md) for coding standards and contribution workflow.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Thanks to all contributors and supporters of the project
- Special thanks to the open-source libraries that made this possible

## 📞 Contact

For questions or support, please contact the development team at sameergul321@gmail.com 
