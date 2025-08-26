from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import time
from datetime import date, datetime
from ..database import get_db
from ..models import Todo
from ..schemas import TodoCreate, TodoUpdate, Todo as TodoSchema
from ..calendar_integration import calendar_integration

router = APIRouter(tags=["api"]) 

# Simple rate limiting storage
request_times = {}
RATE_LIMIT_PER_MINUTE = 60

def check_rate_limit(request: Request, limit_per_minute: int = None):
    """Basic rate limiting - max requests per minute per IP"""
    if limit_per_minute is None:
        limit_per_minute = RATE_LIMIT_PER_MINUTE
        
    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip not in request_times:
        request_times[client_ip] = []
    
    # Remove requests older than 1 minute
    request_times[client_ip] = [t for t in request_times[client_ip] if current_time - t < 60]
    
    # Check if limit exceeded
    if len(request_times[client_ip]) >= limit_per_minute:
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Too many requests per minute."
        )
    
    # Add current request
    request_times[client_ip].append(current_time)

def validate_todo_input(title: str, description: str = None):
    """Validate todo input to prevent abuse"""
    # Check for suspicious content
    suspicious_patterns = [
        'script', 'javascript', 'http://', 'https://', 'file://', 'data:',
        'system:', 'user:', 'assistant:', 'prompt:', 'ignore previous'
    ]
    
    text_to_check = f"{title} {description or ''}".lower()
    
    for pattern in suspicious_patterns:
        if pattern in text_to_check:
            raise HTTPException(
                status_code=400,
                detail="Invalid input detected"
            )
    
    # Check length limits
    if len(title) > 200:
        raise HTTPException(
            status_code=400,
            detail="Title too long (max 200 characters)"
        )
    
    if description and len(description) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Description too long (max 1000 characters)"
        )

@router.get("/api/todoapp", response_model=List[TodoSchema])
def get_todos(
    selected_date: Optional[date] = Query(default=None, description="Filter todos by date (YYYY-MM-DD)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    request: Request = None
):
    # Rate limiting for read operations
    if request:
        check_rate_limit(request, limit_per_minute=RATE_LIMIT_PER_MINUTE)
    
    # Default to today if no date specified
    if selected_date is None:
        selected_date = date.today()
    
    # Filter todos by selected date
    todos = db.query(Todo).filter(Todo.date == selected_date).offset(skip).limit(limit).all()
    return todos

@router.get("/api/todoapp/{todo_id}", response_model=TodoSchema)
def get_todo(todo_id: int, db: Session = Depends(get_db), request: Request = None):
    if request:
        check_rate_limit(request, limit_per_minute=RATE_LIMIT_PER_MINUTE)
    
    # Validate todo_id
    if todo_id < 1:
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.post("/api/todoapp", response_model=TodoSchema)
async def create_todo(
    todo: TodoCreate, 
    selected_date: date = Query(..., description="Date for the todo (YYYY-MM-DD)"),
    db: Session = Depends(get_db), 
    request: Request = None
):
    # Rate limiting for create operations (stricter)
    if request:
        check_rate_limit(request, limit_per_minute=RATE_LIMIT_PER_MINUTE)
    
    # Input validation
    validate_todo_input(todo.title, todo.description)
    
    # Create todo with automatically set date
    todo_data = todo.model_dump()
    todo_data['date'] = selected_date
    
    db_todo = Todo(**todo_data)
    
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    
    return db_todo

@router.put("/api/todoapp/{todo_id}", response_model=TodoSchema)
async def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db), request: Request = None):
    # Rate limiting for update operations
    if request:
        check_rate_limit(request, limit_per_minute=RATE_LIMIT_PER_MINUTE)
    
    # Validate todo_id
    if todo_id < 1:
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    update_data = todo.model_dump(exclude_unset=True)
    
    # Validate input if title/description is being updated
    if 'title' in update_data:
        validate_todo_input(update_data['title'], update_data.get('description', db_todo.description))
    elif 'description' in update_data:
        validate_todo_input(db_todo.title, update_data['description'])
    
    # If this todo is scheduled in calendar and title/description changed, update calendar
    if (db_todo.calendar_event_id and 
        calendar_integration.is_authenticated() and
        (update_data.get('title') or update_data.get('description'))):
        
        try:
            # Get current date for the todo
            target_date = update_data.get('date', db_todo.date)
            
            # Get free slots for the target date
            free_slots = calendar_integration.find_free_slots(target_date)
            
            if free_slots:
                # Use AI to select the best time slot
                selected_slot = calendar_integration.ai_schedule_todo(
                    update_data.get('title', db_todo.title),
                    update_data.get('description', db_todo.description),
                    target_date,
                    free_slots
                )
                
                if selected_slot:
                    # Update the calendar event
                    success = calendar_integration.update_calendar_event(
                        db_todo.calendar_event_id,
                        update_data.get('title', db_todo.title),
                        update_data.get('description', db_todo.description),
                        selected_slot,
                        target_date
                    )
                    
                    if success:
                        print(f"Calendar event updated for todo {todo_id}")
                    else:
                        print(f"Failed to update calendar event for todo {todo_id}")
                        
        except Exception as e:
            print(f"Error updating calendar event: {e}")
            # Continue with todo update even if calendar deletion fails
    
    # Apply updates to the todo
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.delete("/api/todoapp/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), request: Request = None):
    # Rate limiting for delete operations (more reasonable)
    if request:
        check_rate_limit(request, limit_per_minute=RATE_LIMIT_PER_MINUTE)
    
    # Validate todo_id
    if todo_id < 1:
        raise HTTPException(status_code=400, detail="Invalid todo ID")
    
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # If this todo is scheduled in calendar, delete the calendar event
    if db_todo.calendar_event_id and calendar_integration.is_authenticated():
        try:
            success = calendar_integration.delete_calendar_event(db_todo.calendar_event_id)
            if success:
                print(f"Calendar event deleted for todo {todo_id}")
            else:
                print(f"Failed to delete calendar event for todo {todo_id}")
        except Exception as e:
            print(f"Error deleting calendar event: {e}")
            # Continue with todo deletion even if calendar deletion fails

    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

# New Calendar Integration Endpoints
@router.get("/api/calendar/status")
def get_calendar_status():
    """Check if Google Calendar integration is authenticated"""
    return {
        "authenticated": calendar_integration.is_authenticated(),
        "message": "Calendar integration status"
    }

@router.post("/api/calendar/auth")
def authenticate_calendar():
    """Authenticate with Google Calendar"""
    try:
        success = calendar_integration.authenticate_google()
        if success:
            return {"message": "Successfully authenticated with Google Calendar"}
        else:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Google Calendar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@router.post("/api/calendar/logout")
def logout_calendar():
    """Logout from Google Calendar by clearing tokens"""
    try:
        success = calendar_integration.logout_google()
        if success:
            return {"message": "Successfully logged out from Google Calendar"}
        else:
            raise HTTPException(status_code=500, detail="Failed to logout from Google Calendar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout error: {str(e)}")

@router.get("/api/calendar/free-slots")
def get_free_slots(
    target_date: date = Query(..., description="Date to check for free slots (YYYY-MM-DD)"),
    min_duration: int = Query(default=30, description="Minimum duration in minutes")
):
    """Get free time slots in calendar for a specific date"""
    if not calendar_integration.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with Google Calendar")
    
    try:
        free_slots = calendar_integration.find_free_slots(target_date, min_duration)
        return {
            "date": target_date.isoformat(),
            "free_slots": free_slots,
            "total_slots": len(free_slots)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting free slots: {str(e)}")

@router.post("/api/calendar/schedule-todo/{todo_id}")
async def schedule_todo_in_calendar(
    todo_id: int,
    target_date: date = Query(..., description="Date to schedule the todo (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Schedule a todo item in Google Calendar using AI"""
    if request:
        check_rate_limit(request, limit_per_minute=RATE_LIMIT_PER_MINUTE)  # More reasonable for calendar operations
    
    if not calendar_integration.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with Google Calendar")
    
    # Get the todo
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    try:
        # Get free slots for the target date
        free_slots = calendar_integration.find_free_slots(target_date)
        
        if not free_slots:
            raise HTTPException(
                status_code=400, 
                detail=f"No free time slots available on {target_date.strftime('%Y-%m-%d')}"
            )
        
        # Use AI to select the best time slot
        selected_slot = calendar_integration.ai_schedule_todo(
            db_todo.title, 
            db_todo.description, 
            target_date, 
            free_slots
        )
        
        if not selected_slot:
            raise HTTPException(status_code=500, detail="Failed to select time slot")
        
        # Add the todo to Google Calendar
        event_id = calendar_integration.add_todo_to_calendar(
            db_todo.title,
            db_todo.description,
            selected_slot,
            target_date
        )
        
        if event_id:
            # Update the todo with the calendar event ID
            db_todo.calendar_event_id = event_id
            db.commit()
            
            return {
                "message": "Todo successfully scheduled in Google Calendar",
                "scheduled_time": selected_slot['start_time'],
                "duration": selected_slot.get('estimated_duration', 30),
                "ai_reasoning": selected_slot.get('ai_reasoning', 'AI selected this time'),
                "free_slots_available": len(free_slots),
                "calendar_event_id": event_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add todo to Google Calendar")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling todo: {str(e)}")

@router.post("/api/clear-rate-limit")
def clear_rate_limit():
    """Clear rate limit cache (for testing purposes)"""
    global request_times
    request_times = {}
    return {"message": "Rate limit cache cleared"} 