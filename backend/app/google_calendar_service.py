import os
import json
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from tzlocal import get_localzone

class GoogleCalendarService:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
        self.creds = None
        self.calendar_service = None
        self.gmail_service = None
        
        # Get system timezone automatically
        try:
            self.timezone = str(get_localzone())
            print(f"DEBUG: Detected system timezone: {self.timezone}")
        except Exception as e:
            # Fallback to environment variable or default
            self.timezone = os.getenv('CALENDAR_TIMEZONE', 'UTC')
            print(f"DEBUG: Using fallback timezone: {self.timezone}")
        
        # Load existing credentials
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # Initialize services if authenticated
        if self.creds and self.creds.valid:
            self._initialize_services()

    def _initialize_services(self):
        """Initialize Google Calendar and Gmail services"""
        try:
            self.calendar_service = build('calendar', 'v3', credentials=self.creds)
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        except Exception as e:
            print(f"Error initializing services: {e}")

    def is_authenticated(self) -> bool:
        """Check if authenticated with Google"""
        if not self.creds:
            return False
        
        if self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                self._initialize_services()
                return True
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                return False
        
        return self.creds.valid and self.calendar_service is not None

    def authenticate_google(self) -> bool:
        """Authenticate with Google OAuth2"""
        try:
            if not os.path.exists('credentials.json'):
                print("credentials.json not found. Please download from Google Cloud Console.")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
            self.creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
            
            self._initialize_services()
            return True
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def logout_google(self) -> bool:
        """Logout from Google by clearing tokens and credentials"""
        try:
            # Clear existing tokens
            if os.path.exists('token.json'):
                os.remove('token.json')
            
            # Clear credentials and services
            self.creds = None
            self.calendar_service = None
            self.gmail_service = None
            
            print("Successfully logged out from Google")
            return True
            
        except Exception as e:
            print(f"Logout failed: {e}")
            return False

    def get_calendar_events(self, target_date: date) -> List[Dict]:
        """Get calendar events for a specific date"""
        if not self.calendar_service:
            return []
        
        try:
            # Convert date to datetime range for the entire day
            start_datetime = datetime.combine(target_date, time.min)
            end_datetime = datetime.combine(target_date, time.max)
            
            # Convert to RFC3339 timestamp
            start_rfc3339 = start_datetime.isoformat() + 'Z'
            end_rfc3339 = end_datetime.isoformat() + 'Z'
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=start_rfc3339,
                timeMax=end_rfc3339,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format events for our use
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': start,
                    'end': end,
                    'duration_minutes': self._calculate_duration(start, end)
                })
            
            return formatted_events
            
        except HttpError as error:
            print(f"Error getting calendar events: {error}")
            return []

    def _calculate_duration(self, start: str, end: str) -> int:
        """Calculate duration between start and end times in minutes"""
        try:
            if 'T' in start and 'T' in end:  # DateTime
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                duration = end_dt - start_dt
                return int(duration.total_seconds() / 60)
            else:  # All-day event
                return 1440  # 24 hours in minutes
        except:
            return 0

    def find_free_slots(self, target_date: date, min_duration: int = 30) -> List[Dict]:
        """Find free time slots in the calendar for a specific date"""
        events = self.get_calendar_events(target_date)
        
        # Define full day range (12 AM to 11:59 PM)
        day_start = datetime.combine(target_date, datetime.min.time().replace(hour=0, minute=0))
        day_end = datetime.combine(target_date, datetime.min.time().replace(hour=23, minute=59))
        
        # Convert to minutes since midnight for easier calculations
        day_start_minutes = day_start.hour * 60 + day_start.minute  # 0 minutes
        day_end_minutes = day_end.hour * 60 + day_end.minute  # 1439 minutes (23*60 + 59)
        
        # Create busy time ranges
        busy_ranges = []
        for event in events:
            if 'T' in event['start']:  # Skip all-day events
                start_dt = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                
                # Only consider events on the target date
                if start_dt.date() == target_date:
                    start_minutes = start_dt.hour * 60 + start_dt.minute
                    end_minutes = end_dt.hour * 60 + end_dt.minute
                    
                    # Ensure we don't go beyond day boundaries
                    start_minutes = max(0, start_minutes)
                    end_minutes = min(1439, end_minutes)
                    
                    busy_ranges.append((start_minutes, end_minutes))
        
        # Sort busy ranges
        busy_ranges.sort()
        
        # Find free slots
        free_slots = []
        current_time = day_start_minutes
        
        for start, end in busy_ranges:
            if current_time < start:
                slot_duration = start - current_time
                if slot_duration >= min_duration:
                    free_slots.append({
                        'start_minutes': current_time,
                        'end_minutes': start,
                        'duration_minutes': slot_duration,
                        'start_time': self._minutes_to_time(current_time),
                        'end_time': self._minutes_to_time(start)
                    })
            current_time = max(current_time, end)
        
        # Check if there's time after the last event
        if current_time < day_end_minutes:
            slot_duration = day_end_minutes - current_time
            if slot_duration >= min_duration:
                free_slots.append({
                    'start_minutes': current_time,
                    'end_minutes': day_end_minutes,
                    'duration_minutes': slot_duration,
                    'start_time': self._minutes_to_time(current_time),
                    'end_time': self._minutes_to_time(day_end_minutes)
                })
        
        return free_slots

    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to time string"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def add_todo_to_calendar(self, todo_title: str, todo_description: str, 
                            selected_slot: Dict, target_date: date) -> Optional[str]:
        """Add a todo item to Google Calendar and return the event ID"""
        try:
            if not self.calendar_service:
                return None
            
            # Create event start and end times with proper timezone handling
            hour = selected_slot['start_minutes'] // 60
            minute = selected_slot['start_minutes'] % 60
            
            # Create the time in the detected system timezone
            tz = pytz.timezone(self.timezone)
            local_dt = tz.localize(datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute)))
            
            duration = min(selected_slot['estimated_duration'], selected_slot['duration_minutes'])
            end_dt = local_dt + timedelta(minutes=duration)
                        
            # Format for Google Calendar - use local time with detected timezone
            start_str = local_dt.isoformat()
            end_str = end_dt.isoformat()
            
            event = {
                'summary': f"📝 {todo_title}",
                'description': todo_description or 'Todo item',
                'start': {
                    'dateTime': start_str,
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': end_str,
                    'timeZone': self.timezone,
                },
                'reminders': {
                    'useDefault': True,
                },
            }
            
            # Add event to calendar
            event_result = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return event_result['id']
            
        except Exception as e:
            print(f"Error adding todo to calendar: {e}")
            return None

    def update_calendar_event(self, event_id: str, todo_title: str, todo_description: str, 
                             selected_slot: Dict, target_date: date) -> bool:
        """Update an existing calendar event"""
        try:
            if not self.calendar_service:
                return False
            
            # Create event start and end times
            hour = selected_slot['start_minutes'] // 60
            minute = selected_slot['start_minutes'] % 60
            
            tz = pytz.timezone(self.timezone)
            local_dt = tz.localize(datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute)))
            
            duration = min(selected_slot['estimated_duration'], selected_slot['duration_minutes'])
            end_dt = local_dt + timedelta(minutes=duration)
            
            # Format for Google Calendar
            start_str = local_dt.isoformat()
            end_str = end_dt.isoformat()
            
            event = {
                'summary': f"📝 {todo_title}",
                'description': todo_description or 'Todo item',
                'start': {
                    'dateTime': start_str,
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': end_str,
                    'timeZone': self.timezone,
                },
            }
            
            # Update event
            self.calendar_service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error updating calendar event: {e}")
            return False

    def delete_calendar_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            if not self.calendar_service:
                return False
            
            self.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error deleting calendar event: {e}")
            return False 