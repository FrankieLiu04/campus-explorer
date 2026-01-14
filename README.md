# Campus Explorer

A full-stack web application for CUHK campus exploration and student social interaction. Features an interactive campus map, real-time chat, and user profile management.

## Features

### 🗺️ Interactive Campus Map
- Mark and discover campus locations (libraries, cafeterias, study areas)
- Add custom markers with titles and descriptions
- Real-time route planning between locations using OpenRouteService API
- Geolocation support to find your current position
- Pan and zoom navigation with marker clustering

### 💬 Real-time Chat
- Live messaging with other students using WebSocket connections
- Emoji picker with 100+ emojis
- Sticker support for expressive communication
- Image sharing capability
- Voice message recording and playback
- Online user count display
- Message history persistence

### 👤 User Profile Management
- User registration and authentication with JWT tokens
- Customizable profile with avatar upload
- Personal information management (name, age, gender, location, bio)
- Secure password change functionality

### 🔐 Authentication System
- Secure user registration and login
- JWT-based session management
- Protected routes and API endpoints

## Tech Stack

### Frontend
- **Vue.js 3** - Progressive JavaScript framework with Composition API
- **Vue Router** - Official router for Vue.js SPA navigation
- **Pinia** - State management for Vue.js
- **Vite** - Next-generation frontend build tool
- **Element Plus** - Vue 3 UI component library
- **Leaflet** - Interactive maps library
- **Vue Leaflet** - Vue 3 components for Leaflet maps
- **Socket.IO Client** - Real-time bidirectional communication
- **Axios** - Promise-based HTTP client

### Backend
- **Flask** - Lightweight Python web framework
- **Flask-SQLAlchemy** - SQL toolkit and ORM
- **Flask-JWT-Extended** - JWT authentication support
- **Flask-SocketIO** - WebSocket support for Flask
- **Flask-CORS** - Cross-Origin Resource Sharing handling
- **Werkzeug** - WSGI utility library for password hashing
- **SQLite** - Lightweight database for development

### APIs & Services
- **OpenStreetMap** - Map tile provider
- **OpenRouteService** - Route planning and directions API

## Project Structure

```
full_stack_web_app/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── models/              # Database models
│   │   │   ├── user.py          # User model
│   │   │   └── map_marker.py    # Map marker model
│   │   ├── routes/              # API endpoints
│   │   │   ├── auth.py          # Authentication routes
│   │   │   ├── chat.py          # Chat/WebSocket routes
│   │   │   ├── map.py           # Map marker routes
│   │   │   └── profile.py       # Profile management routes
│   │   └── static/              # Static files (avatars)
│   ├── instance/                # SQLite database
│   ├── requirements.txt         # Python dependencies
│   └── run.py                   # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── App.vue              # Root component
│   │   ├── main.js              # Application entry
│   │   ├── router/              # Vue Router configuration
│   │   ├── stores/              # Pinia state stores
│   │   ├── styles/              # Global styles and variables
│   │   └── views/               # Page components
│   │       ├── Home.vue         # Landing page
│   │       ├── Login.vue        # Login page
│   │       ├── Register.vue     # Registration page
│   │       ├── Map.vue          # Interactive map
│   │       ├── Chat.vue         # Real-time chat
│   │       └── Profile.vue      # User profile
│   ├── public/                  # Static assets
│   ├── index.html               # HTML entry point
│   ├── package.json             # Node.js dependencies
│   └── vite.config.js           # Vite configuration
│
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

The backend server will start at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend development server will start at `http://localhost:3000`

## Production Notes

- Backend config is environment-driven. See `.env.example`.
- Health endpoints:
  - `GET /healthz` - liveness
  - `GET /readyz` - readiness (checks DB connectivity)

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Profile
- `GET /api/profile/profile` - Get user profile
- `PUT /api/profile/profile` - Update user profile
- `POST /api/profile/change-password` - Change password

### Map
- `GET /api/map/markers` - Get all markers
- `POST /api/map/markers` - Create new marker
- `DELETE /api/map/markers/:id` - Delete marker
- `POST /api/map/route` - Calculate route between points

### Chat (WebSocket)
- `join` - Join chat room
- `message` - Send/receive messages
- `user_joined` / `user_left` - User presence events

## License

This project is for educational purposes.
