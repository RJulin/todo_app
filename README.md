# Todo App with AI Calendar Integration

A simple todo application built with Cursor using FastAPI backend and Next.js frontend, featuring intelligent scheduling powered by AI and Google Calendar integration.

## ✨ Features

- 📝 **Smart Todo Management**: Create, edit, and organize todos by date
- 🤖 **AI-Powered Scheduling**: OpenAI GPT-4o Mini analyzes your todos and suggests optimal calendar placement
- 📅 **Google Calendar Integration**: Seamlessly add todos to your Gmail calendar
- 🎯 **Smart Time Slots**: AI finds the best available time based on task type and your schedule
- 🌙 **Dark Mode**: Beautiful dark/light theme toggle
- 📱 **Responsive Design**: Works perfectly on desktop and mobile
- 🚀 **Real-time Updates**: Instant feedback and smooth interactions
- 🛡️ **Fallback Scheduling**: Intelligent scheduling even when AI is unavailable

## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy ORM (Python 3.13+)
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Database**: SQLite (easily upgradable to PostgreSQL/MySQL)
- **AI**: OpenAI GPT-4o Mini for intelligent scheduling
- **Calendar**: Google Calendar API integration with OAuth 2.0

## 🚀 Quick Start

### Prerequisites
- Python 3.13+**
- Node.js 18+
- OpenAI API key (optional - fallback scheduling works without it)
- Google Cloud Project with Calendar API enabled

### 1. Clone and Setup
```bash
git clone <your-repo>
cd todo_app
```

### 2. Backend Setup
```bash
cd backend

# Create Python 3.13 virtual environment
python3.13 -m venv .venv_py313
source .venv_py313/bin/activate  # On Windows: .venv_py313\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp env.example .env
# Add your OPENAI_API_KEY to .env (optional but recommended)

# Download Google credentials.json and place in backend directory
# See backend/README.md for detailed Google Calendar setup

# Start backend
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
cd front
npm install
npm run dev
```

### 4. Open Your Browser
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔧 Google Calendar Setup

### Required Google Cloud Services
1. **Google Calendar API** - Core calendar functionality
2. **Google+ API** - User authentication (if not using basic OAuth)

### OAuth 2.0 Scopes
Your app requires this minimal scope for calendar access:
```
https://www.googleapis.com/auth/calendar.events
```
- **What it does**: Read and write calendar events only
- **User sees**: "See and manage events on your Google Calendar"
- **Perfect for**: Adding, editing, and deleting todo events

### Setup Steps
1. **Create Google Cloud Project** and enable Calendar API
2. **Generate OAuth 2.0 credentials** and download `credentials.json`
3. **Place credentials.json** in the backend directory
4. **Click "Connect Calendar"** in the app to authenticate

See [backend/README.md](backend/README.md) for detailed setup instructions.

## 🎯 How It Works

1. **Create a Todo**: Add tasks with title and description
2. **AI Analysis**: OpenAI GPT-4o Mini analyzes the task content and context (if available)
3. **Smart Scheduling**: AI or fallback logic finds the best available time slot
4. **Calendar Integration**: Todo automatically appears in your Google Calendar

## 🧠 AI vs Fallback Scheduling

- **AI Scheduling**: Uses OpenAI to analyze task content and suggest optimal timing
- **Fallback Scheduling**: Intelligent heuristics when AI is unavailable:
  - Work tasks prefer morning slots (9 AM - 12 PM)
  - Personal tasks prefer afternoon slots (12 PM - 6 PM)
  - Duration estimation based on task keywords
  - No external API dependencies

## 📚 API Endpoints

### Todo Management
- `GET /api/todoapp` - Get todos for a specific date
- `POST /api/todoapp` - Create a new todo
- `PUT /api/todoapp/{id}` - Update a todo
- `DELETE /api/todoapp/{id}` - Delete a todo

### Calendar Integration
- `GET /api/calendar/status` - Check calendar authentication status
- `POST /api/calendar/auth` - Authenticate with Google Calendar
- `GET /api/calendar/free-slots` - Get available time slots for a date
- `POST /api/calendar/schedule-todo/{id}` - Schedule todo in Google Calendar

## 🛡️ Security Features

- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure OAuth 2.0 authentication
- Environment variable configuration
- CORS protection for frontend integration

## 🔍 Troubleshooting

### Common Issues
- **403 Access Denied**: Add your email as a test user in Google OAuth consent screen
- **Calendar Connection Fails**: Ensure `credentials.json` is in the backend directory
- **AI Scheduling Errors**: Check OpenAI API key or use fallback scheduling
- **Module Not Found**: Install dependencies with `pip install -r requirements.txt`
- **Python Version Issues**: Ensure you're using Python 3.13+ for best compatibility

### Fallback Mode
The app works even without OpenAI API:
- Intelligent keyword-based scheduling
- Time-of-day preferences for different task types
- Duration estimation based on task content
- No external API dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- Check the [backend/README.md](backend/README.md) for detailed setup
- Review API documentation at `/docs` when backend is running
- Open an issue for bugs or feature requests
- The app includes comprehensive error handling and fallback modes 