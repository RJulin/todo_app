import json
import os
import openai
from datetime import date, datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        # Initialize OpenAI client if API key is available
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None

    def schedule_todo(self, todo_title: str, todo_description: str, target_date: date, 
                     free_slots: List[Dict]) -> Optional[Dict]:
        """Use AI to determine the best time slot for a todo"""
        if not free_slots:
            return None
        # If no OpenAI client, use fallback
        if not self.openai_client:
            return self._fallback_schedule_todo(todo_title, todo_description, free_slots)
        
        try:
            # Filter out past time slots
            current_time = datetime.now()
            valid_slots = []
            for i, slot in enumerate(free_slots):
                slot_time = datetime.combine(target_date, datetime.strptime(slot['start_time'], '%H:%M').time())
                if slot_time > current_time:
                    valid_slots.append((i, slot))
            if not valid_slots:
                print(f"No valid future time slots available. Current time: {current_time.strftime('%H:%M')}")
                return self._fallback_schedule_todo(todo_title, todo_description, free_slots)
            
            # Create prompt for AI scheduling
            prompt = f"""
            You will schedule todo items to users calendar. Please analyze the available time slots and suggest the best one.
            
            Todo: {todo_title}
            Description: {todo_description or 'No description'}
            Date: {target_date.strftime('%A, %B %d, %Y')}
            Current time: {current_time.strftime('%H:%M')}
            
            Available time slots (only future times):
            {self._format_slots_for_ai([slot for _, slot in valid_slots])}
            
            Consider:
            1. The nature of the todo (work, personal, urgent, etc.)
            2. Time of day preferences:
               - MORNING (early slots): Work tasks, important meetings, high-energy activities
               - AFTERNOON (middle slots): Routine tasks, personal errands, moderate energy
               - EVENING (late slots): Relaxing tasks, bedtime activities, low energy
            3. Choose the slot and specific time in that slot that matches the activity's natural timing
            4. Duration needed (estimate based on title/description)
            5. Energy levels at different times
            6. Only select from the available future time slots
            
            Examples:
            - "Take sleeping pills before bed" → MUST choose time in evening 18:00-22:00)
            - "Morning workout" → MUST choose time inmorning 06:00-12:00)
            - "Afternoon meeting" → MUST choose time in afternoon 12:00-18:00)

            Return only a JSON response with:
            {{
                "selected_slot_index": <index of best slot from the valid_slots list>,
                "reasoning": "<brief explanation>",
                "estimated_duration": <minutes needed>
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            print(f"AI Response: {ai_response}")
            
            # Extract JSON from response
            if '{' in ai_response and '}' in ai_response:
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                json_str = ai_response[start_idx:end_idx]
                
                try:
                    result = json.loads(json_str)
                    slot_index = result.get('selected_slot_index', 0)
                    
                    print(f"DEBUG: AI selected slot_index: {slot_index}")
                    print(f"DEBUG: valid_slots length: {len(valid_slots)}")
                    print(f"DEBUG: valid_slots content: {valid_slots}")
                    
                    if 0 <= slot_index < len(valid_slots):
                        # Get the slot from valid_slots, not free_slots
                        selected_slot = valid_slots[slot_index][1].copy()  # valid_slots contains (index, slot) tuples
                        selected_slot['ai_reasoning'] = result.get('reasoning', 'AI selected this time')
                        selected_slot['estimated_duration'] = result.get('estimated_duration', 30)
                        print(f"AI Successfully Selected: Slot {slot_index} at {selected_slot['start_time']}")
                        return selected_slot
                    else:
                        print(f"DEBUG: Slot index {slot_index} is out of range for valid_slots (0-{len(valid_slots)-1})")
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"AI response parsing failed: {e}")
                    # Continue to fallback
                    pass
            
            # Fallback if AI response parsing fails
            return self._fallback_schedule_todo(todo_title, todo_description, free_slots)
            
        except Exception as e:
            print(f"AI scheduling failed: {e}")
            return self._fallback_schedule_todo(todo_title, todo_description, free_slots)

    def _fallback_schedule_todo(self, todo_title: str, todo_description: str, free_slots: List[Dict]) -> Optional[Dict]:
        """Fallback scheduling when AI is not available or fails"""
        print(f"Fallback Scheduling: Using basic logic for '{todo_title}'")
        
        if not free_slots:
            return None
        
        # Filter out past time slots
        current_time = datetime.now()
        valid_slots = []
        for slot in free_slots:
            slot_time = datetime.combine(datetime.now().date(), datetime.strptime(slot['start_time'], '%H:%M').time())
            if slot_time > current_time:
                valid_slots.append(slot)
        
        if not valid_slots:
            print(f"Fallback: No valid future time slots available. Current time: {current_time.strftime('%H:%M')}")
            return None
        
        # Simple heuristic: prefer morning slots for work tasks, afternoon for personal
        work_keywords = ['work', 'meeting', 'call', 'project', 'report', 'email', 'client', 'business']
        personal_keywords = ['grocery', 'shopping', 'exercise', 'gym', 'personal', 'family', 'home']
        
        text_to_analyze = f"{todo_title} {todo_description or ''}".lower()
        
        # Determine if it's work or personal
        is_work = any(keyword in text_to_analyze for keyword in work_keywords)
        is_personal = any(keyword in text_to_analyze for keyword in personal_keywords)
        
        # Estimate duration based on content
        estimated_duration = 30  # Default
        if any(word in text_to_analyze for word in ['meeting', 'call', 'appointment']):
            estimated_duration = 60
        elif any(word in text_to_analyze for word in ['grocery', 'shopping']):
            estimated_duration = 45
        elif any(word in text_to_analyze for word in ['exercise', 'gym', 'workout']):
            estimated_duration = 60
        
        # Select best slot based on type
        selected_slot = valid_slots[0].copy()  # Default to first valid slot
        
        if is_work and len(valid_slots) > 1:
            # Prefer morning slots for work (first few slots)
            selected_slot = valid_slots[0].copy()
        elif is_personal and len(valid_slots) > 1:
            # Prefer afternoon slots for personal (later slots)
            selected_slot = valid_slots[-1].copy()
        
        selected_slot['ai_reasoning'] = f"Fallback scheduling: {'Work' if is_work else 'Personal'} task scheduled at {selected_slot['start_time']}"
        selected_slot['estimated_duration'] = estimated_duration
        
        print(f"Fallback Selected: {'Work' if is_work else 'Personal'} task at {selected_slot['start_time']}")
        print(f"Fallback Reasoning: {selected_slot['ai_reasoning']}")
        
        return selected_slot

    def _format_slots_for_ai(self, free_slots: List[Dict]) -> str:
        """Format time slots for AI prompt"""
        formatted = []
        for i, slot in enumerate(free_slots):
            formatted.append(f"Slot {i}: {slot['start_time']} - {slot['end_time']} ({slot['duration_minutes']} min)")
        return "\n".join(formatted) 