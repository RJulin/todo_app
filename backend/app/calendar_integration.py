from datetime import date
from typing import Dict, List, Optional
from .ai_service import AIService
from .google_calendar_service import GoogleCalendarService

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send'
]

class CalendarIntegration:
    def __init__(self):
        self.ai_service = AIService()
        self.google_calendar_service = GoogleCalendarService()

    def is_authenticated(self) -> bool:
        """Check if authenticated with Google Calendar"""
        return self.google_calendar_service.is_authenticated()

    def authenticate_google(self) -> bool:
        """Authenticate with Google Calendar"""
        return self.google_calendar_service.authenticate_google()

    def logout_google(self) -> bool:
        """Logout from Google Calendar by clearing tokens"""
        return self.google_calendar_service.logout_google()

    def get_calendar_events(self, target_date: date) -> List[Dict]:
        """Get calendar events for a specific date"""
        return self.google_calendar_service.get_calendar_events(target_date)

    def find_free_slots(self, target_date: date, min_duration: int = 30) -> List[Dict]:
        """Find free time slots in the calendar for a specific date"""
        return self.google_calendar_service.find_free_slots(target_date, min_duration)

    def ai_schedule_todo(self, todo_title: str, todo_description: str, target_date: date, 
                        free_slots: List[Dict]) -> Optional[Dict]:
        """Use AI to determine the best time slot for a todo"""
        return self.ai_service.schedule_todo(todo_title, todo_description, target_date, free_slots)

    def add_todo_to_calendar(self, todo_title: str, todo_description: str, 
                            selected_slot: Dict, target_date: date) -> Optional[str]:
        """Add a todo item to Google Calendar and return the event ID"""
        return self.google_calendar_service.add_todo_to_calendar(todo_title, todo_description, selected_slot, target_date)

    def update_calendar_event(self, event_id: str, todo_title: str, todo_description: str, 
                             selected_slot: Dict, target_date: date) -> bool:
        """Update an existing calendar event"""
        return self.google_calendar_service.update_calendar_event(event_id, todo_title, todo_description, selected_slot, target_date)

    def delete_calendar_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        return self.google_calendar_service.delete_calendar_event(event_id)

# Global instance
calendar_integration = CalendarIntegration() 