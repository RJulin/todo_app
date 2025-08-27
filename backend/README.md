# Todo App Backend

A FastAPI backend for a todo application with Google Calendar integration and AI-powered scheduling, featuring intelligent fallback mechanisms.

## Features

- ✅ **CRUD Operations**: Create, read, update, and delete todos
- 📅 **Date-based Todos**: Organize todos by specific dates
- 🤖 **AI Scheduling**: Use OpenAI GPT-4o Mini to intelligently schedule todos in Google Calendar
- 🛡️ **Fallback Scheduling**: Intelligent scheduling even when AI is unavailable
- 🔐 **Google Calendar Integration**: Seamlessly add todos to your Gmail calendar
- 🚀 **Smart Time Slots**: AI or fallback logic finds the best time for each todo
- 🛡️ **Security**: Rate limiting, input validation, and OAuth 2.0

## Setup

### 1. Install Dependencies

**Prerequisites:**
- **Python 3.13+** (required for best compatibility and performance)

```bash
# Create Python 3.13 virtual environment
python3.13 -m venv .venv_py313
source .venv_py313/bin/activate  # On Windows: .venv_py313\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Required packages:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy>=2.0.43` - Database ORM (Python 3.13 compatible)
- `alembic` - Database migrations
- `google-auth` - Google authentication
- `google-auth-oauthlib` - OAuth 2.0 flow
- `google-api-python-client` - Google Calendar API
- `openai` - AI scheduling with GPT-4o Mini (optional)
- `pytz` & `tzlocal` - Timezone handling

### 2. Environment Variables

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

**Required variables:**
- `OPENAI_API_KEY`: Your OpenAI API key (optional - fallback works without it)
- `DATABASE_URL`: Database connection string (default: SQLite)

### 3. Google Calendar Setup

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API and Gmail API

#### Step 2: Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Download the `credentials.json` file
5. Place `credentials.json` in the backend directory

#### Step 3: Configure OAuth Consent Screen
1. Go to "APIs & Services" > "OAuth consent screen"
2. Set app name and user support email
3. Add scopes:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/gmail.send`
4. **Add test users** (including your own email)
5. Save and continue

#### Step 4: First Authentication
1. Start the backend server
2. Click "Connect Calendar" in the frontend
3. Complete OAuth flow in your browser
4. Grant calendar and Gmail permissions

### 4. Run the Application

```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

## API Endpoints

### Todo Management
- `GET /api/todoapp` - Get todos for a specific date
- `POST /api/todoapp` - Create a new todo
- `GET /api/todoapp/{id}` - Get a specific todo
- `PUT /api/todoapp/{id}` - Update a todo
- `DELETE /api/todoapp/{id}` - Delete a todo

### Calendar Integration
- `GET /api/calendar/status` - Check calendar authentication status
- `POST /api/calendar/auth` - Authenticate with Google Calendar
- `GET /api/calendar/free-slots` - Get available time slots for a date
- `POST /api/calendar/schedule-todo/{id}` - Schedule a todo in Google Calendar

## How AI Scheduling Works

### 1. **Free Slot Detection**
- Analyzes your calendar for available time slots
- Focuses on business hours (9 AM - 6 PM)
- Considers existing events and conflicts

### 2. **AI Analysis** (when OpenAI is available)
- OpenAI analyzes todo content and context
- Considers task type, urgency, and energy patterns
- Suggests optimal timing based on AI insights

### 3. **Fallback Scheduling** (when AI is unavailable)
- **Work Tasks**: Prefer morning slots (9 AM - 12 PM)
- **Personal Tasks**: Prefer afternoon slots (12 PM - 6 PM)
- **Duration Estimation**: Based on task keywords
- **Smart Selection**: Chooses best available slot

### 4. **Calendar Integration**
- Automatically adds todos to your Google Calendar
- Sets appropriate duration and reminders
- Includes task description and context
- Handles timezone conversions properly

## Security Features

- **Rate Limiting**: Prevents API abuse (stricter for calendar operations)
- **Input Validation**: Sanitizes user input against malicious patterns
- **OAuth 2.0**: Secure Google API authentication
- **Environment Variables**: Secure configuration management
- **CORS Protection**: Configured for frontend integration

## Troubleshooting

### Calendar Authentication Issues

#### 403 Access Denied
- **Solution**: Add your email as a test user in OAuth consent screen
- **Steps**: 
  1. Go to Google Cloud Console > OAuth consent screen
  2. Scroll to "Test users" section
  3. Click "Add Users" and add your email
  4. Save changes

#### Missing Credentials
- **Error**: "Please download credentials.json from Google Cloud Console"
- **Solution**: Download and place `credentials.json` in backend directory

#### API Not Enabled
- **Error**: "API not enabled"
- **Solution**: Enable Google Calendar API and Gmail API in Google Cloud Console

### OpenAI API Issues

#### API Key Invalid
- **Error**: "Invalid API key"
- **Solution**: Check your API key in `.env` file

#### Quota Exceeded
- **Error**: "You exceeded your current quota"
- **Solution**: The app will automatically use fallback scheduling

#### No API Key
- **Behavior**: App works perfectly with fallback scheduling
- **Benefit**: No external dependencies, intelligent scheduling still works

### Database Issues

- **Auto-creation**: SQLite database is created automatically on first run
- **Schema updates**: Database adapts to model changes automatically
- **Production**: Consider PostgreSQL or MySQL for production use

### Common Frontend Errors

#### "Failed to schedule todo in calendar"
- **Check**: Backend logs for specific error details
- **Common causes**: Missing credentials, API errors, authentication issues

#### "Calendar not authenticated"
- **Solution**: Click "Connect Calendar" and complete OAuth flow

## Development

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── calendar_integration.py  # Google Calendar + AI logic
│   ├── database.py              # Database configuration
│   ├── models.py                # SQLAlchemy models
│   ├── routers/
│   │   └── api.py              # API endpoints
│   └── schemas.py              # Pydantic schemas
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
└── credentials.json             # Google OAuth credentials
```

### Testing Endpoints

#### Test Calendar Status
```bash
curl "http://localhost:8000/api/calendar/status"
```

#### Test Free Slots
```bash
curl "http://localhost:8000/api/calendar/free-slots?target_date=2025-08-24"
```

#### Test Todo Scheduling
```bash
curl -X POST "http://localhost:8000/api/calendar/schedule-todo/1?target_date=2025-08-24"
```

### Environment Variables Reference

```bash
# Required
DATABASE_URL=sqlite:///./todo_app.db

# Optional but recommended
OPENAI_API_KEY=your-openai-api-key-here


## Production Considerations

- **Database**: Use PostgreSQL or MySQL instead of SQLite
- **Authentication**: Implement proper user authentication
- **Rate Limiting**: Adjust limits based on your needs
- **Logging**: Add structured logging for monitoring
- **Monitoring**: Add health checks and metrics
- **SSL**: Use HTTPS in production 