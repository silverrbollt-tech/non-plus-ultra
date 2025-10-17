# Discord-like Flask App

A full-featured Discord-like chat application built with Flask, featuring real-time messaging, server management, and user authentication.

## 🚀 Features

- **User Authentication**: Register, login, and profile management
- **Server Management**: Create servers, join with codes, and manage members
- **Real-time Chat**: Socket.IO powered messaging in channels
- **Channel System**: Create and manage text channels within servers
- **Member Management**: View server members and roles
- **Join by Code**: Easy server joining with unique codes
- **Responsive Design**: Discord-inspired dark theme UI

## 🏗️ Project Structure

```
myapp/
│
├── app.py                      # Flask entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── init_db.py                  # Database initialization script
│
├── instance/
│   └── myapp.sqlite            # SQLite database (auto-created)
│
├── myapp/
│   ├── __init__.py             # App factory + Socket.IO setup
│   ├── extensions.py           # Database, login manager, socketio
│   ├── models.py               # Database models
│   │
│   ├── auth/                   # Authentication Blueprint
│   │   ├── __init__.py
│   │   ├── routes.py           # Login, register, logout routes
│   │   ├── forms.py            # WTForms for auth
│   │   └── templates/auth/     # Auth templates
│   │
│   ├── main/                   # Profile & dashboard
│   │   ├── __init__.py
│   │   ├── routes.py           # Profile routes
│   │   └── templates/main/     # Profile templates
│   │
│   ├── servers/                # Server & channel management
│   │   ├── __init__.py
│   │   ├── routes.py           # Server/channel routes
│   │   ├── forms.py            # Server/channel forms
│   │   ├── sockets/
│   │   │   └── events.py       # Socket.IO event handlers
│   │   └── templates/servers/  # Server templates
│   │
│   ├── templates/              # Shared templates
│   │   ├── base.html           # Main layout
│   │   └── errors/             # Error pages
│   │
│   ├── static/                 # Static assets
│   │   ├── css/style.css       # Custom styles
│   │   ├── js/app.js           # Frontend JavaScript
│   │   └── images/             # Images
│   │
│   └── utils/                  # Utility functions
│       ├── decorators.py       # Route decorators
│       ├── helpers.py          # Helper functions
│       └── seeds.py            # Database seeding
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd discord-like-flask-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python init_db.py
```

This will:
- Create all database tables
- Seed the database with sample data
- Create a default "Welcome Server" with sample users

### 4. Run the Application

```bash
python app.py
```

The application will be available at:
- **Local**: http://127.0.0.1:5001
- **Network**: http://0.0.0.0:5001

## 👥 Sample Users

The database is seeded with these test accounts:

| Username | Email | Password | Role |
|----------|-------|----------|------|
| admin | admin@example.com | password123 | Owner |
| alice | alice@example.com | password123 | Member |
| bob | bob@example.com | password123 | Member |

## 🎯 Usage Guide

### Getting Started

1. **Register/Login**: Create a new account or use the sample accounts
2. **View Servers**: See all servers you're a member of
3. **Join Server**: Use the join code form in the sidebar
4. **Create Server**: Click "Create Server" to make your own

### Server Management

- **Create Server**: Set name, description, and get a unique join code
- **Join Server**: Use the 6-character join code to join servers
- **Manage Channels**: Create text channels within servers
- **View Members**: See all server members in the right sidebar

### Real-time Chat

- **Select Channel**: Click on any channel to start chatting
- **Send Messages**: Type and press Enter to send messages
- **Real-time Updates**: See messages from other users instantly

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///myapp.sqlite
```

### Database

The app uses SQLite by default. To use PostgreSQL or MySQL:

1. Install the appropriate database driver
2. Update `DATABASE_URL` in `config.py`
3. Run `python init_db.py` to create tables

## 🚀 Production Deployment

For production deployment:

1. **Use a production WSGI server** (e.g., Gunicorn)
2. **Set up a reverse proxy** (e.g., Nginx)
3. **Use a production database** (PostgreSQL recommended)
4. **Set secure SECRET_KEY**
5. **Enable HTTPS**

Example with Gunicorn:

```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:8000 app:app
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py`
2. **Database errors**: Delete `instance/myapp.sqlite` and run `python init_db.py`
3. **Socket.IO issues**: Check browser console for JavaScript errors

### Debug Mode

The app runs in debug mode by default. To disable:

```python
# In app.py
socketio.run(app, debug=False, host="0.0.0.0", port=5001)
```

## 📝 API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Process registration
- `GET /logout` - Logout user

### Servers
- `GET /servers/` - List user's servers
- `GET /servers/create` - Create server page
- `POST /servers/create` - Process server creation
- `GET /servers/<id>` - View server
- `GET /servers/<id>/channel/<id>` - View channel

### Socket.IO Events
- `join` - Join a channel room
- `leave` - Leave a channel room
- `send_message` - Send a message
- `message` - Receive a message

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Flask framework
- Socket.IO for real-time communication
- Bootstrap for UI components
- Discord for design inspiration