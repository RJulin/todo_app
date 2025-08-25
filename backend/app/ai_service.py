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
        """Use AI to determine the best time slot and specific time for a todo"""
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
            You will schedule todo items to users calendar. Please analyze the available time slots and suggest the best one WITH a specific start time within that slot.
            
            Todo: {todo_title}
            Description: {todo_description or 'No description'}
            Date: {target_date.strftime('%A, %B %d, %Y')}
            Current time: {current_time.strftime('%H:%M')}
            
            Available time slots (only future times):
            {self._format_slots_for_ai([slot for _, slot in valid_slots])}
            
            Consider:
            1. The nature of the todo (work, personal, urgent, etc.)
            2. Time of day preferences:
               - MORNING (06:00-12:00): Work tasks, important meetings, high-energy activities
               - AFTERNOON (12:00-18:00): Routine tasks, personal errands, moderate energy
               - EVENING (18:00-22:00): Relaxing tasks, bedtime activities, low energy
               - NIGHT (22:00-06:00): Sleep-related, quiet activities
            3. Choose the slot AND specific time in that slot that matches the activity's natural timing
            4. Duration needed (estimate based on title/description)
            5. Energy levels at different times
            6. Only select from the available future time slots
            
            Examples:
            - "Take sleeping pills before bed" → Choose available evening slot (18:00-22:00) and suggest 21:00
            - "Morning workout" → Choose available morning slot (06:00-12:00) and suggest 07:00
            - "Afternoon meeting" → Choose available afternoon slot (12:00-18:00) and suggest 14:00
            - "Evening relaxation" → Choose available evening slot (18:00-22:00) and suggest 19:00

            Return only a JSON response with:
            {{
                "selected_slot_index": <index of best slot from the valid_slots list>,
                "suggested_start_time": "<HH:MM format - specific time within the slot>",
                "reasoning": "<brief explanation of why this time is best>",
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
                    suggested_time = result.get('suggested_start_time', '')
                    
                    print(f"DEBUG: AI selected slot_index: {slot_index}")
                    print(f"DEBUG: AI suggested time: {suggested_time}")
                    print(f"DEBUG: valid_slots length: {len(valid_slots)}")
                    print(f"DEBUG: valid_slots content: {valid_slots}")
                    
                    if 0 <= slot_index < len(valid_slots):
                        # Get the slot from valid_slots, not free_slots
                        selected_slot = valid_slots[slot_index][1].copy()  # valid_slots contains (index, slot) tuples
                        
                        # Validate and use the suggested time if it's within the slot
                        if suggested_time and self._is_time_in_slot(suggested_time, selected_slot):
                            # Convert suggested time to minutes for better precision
                            suggested_minutes = self._time_to_minutes(suggested_time)
                            selected_slot['start_minutes'] = suggested_minutes
                            selected_slot['start_time'] = suggested_time
                            print(f"AI Successfully Selected: Slot {slot_index} at {suggested_time} (within slot {selected_slot['start_time']}-{selected_slot['end_time']})")
                        else:
                            print(f"AI suggested time {suggested_time} not valid for slot, using slot start time")

                        selected_slot['ai_reasoning'] = result.get('reasoning', 'AI selected this time')
                        selected_slot['estimated_duration'] = result.get('estimated_duration', 30)
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
        evening_keywords = ['sleep', 'bed', 'relax', 'dinner', 'evening', 'night', 'rest']
        
        text_to_analyze = f"{todo_title} {todo_description or ''}".lower()
        
        # Determine if it's work, personal, or evening
        is_work = any(keyword in text_to_analyze for keyword in work_keywords)
        is_personal = any(keyword in text_to_analyze for keyword in personal_keywords)
        is_evening = any(keyword in text_to_analyze for keyword in evening_keywords)
        
        # Estimate duration based on content
        estimated_duration = 30  # Default
        if any(word in text_to_analyze for word in ['meeting', 'call', 'appointment']):
            estimated_duration = 60
        elif any(word in text_to_analyze for word in ['grocery', 'shopping']):
            estimated_duration = 45
        elif any(word in text_to_analyze for word in ['exercise', 'gym', 'workout']):
            estimated_duration = 60
        
        # Select best slot based on type and suggest specific time
        selected_slot = valid_slots[0].copy()  # Default to first valid slot
        suggested_time = selected_slot['start_time']  # Default to slot start time
        
        if is_work and len(valid_slots) > 1:
            # Prefer morning slots for work (first few slots)
            selected_slot = valid_slots[0].copy()
            # Suggest a time within the actual slot, not a fixed time
            slot_start_minutes = self._time_to_minutes(selected_slot['start_time'])
            slot_end_minutes = self._time_to_minutes(selected_slot['end_time'])
            # Suggest early in the slot, but not before it starts
            suggested_minutes = max(slot_start_minutes, 8 * 60)  # 8 AM or slot start, whichever is later
            suggested_time = self._minutes_to_time(suggested_minutes)
        elif is_personal and len(valid_slots) > 1:
            # Prefer afternoon slots for personal (later slots)
            selected_slot = valid_slots[-1].copy()
            # Suggest a time within the actual slot
            slot_start_minutes = self._time_to_minutes(selected_slot['start_time'])
            slot_end_minutes = self._time_to_minutes(selected_slot['end_time'])
            # Suggest middle of the slot
            suggested_minutes = slot_start_minutes + (slot_end_minutes - slot_start_minutes) // 2
            suggested_time = self._minutes_to_time(suggested_minutes)
        elif is_evening:
            # For evening tasks, find the latest available slot
            evening_slots = [slot for slot in valid_slots if self._time_to_minutes(slot['start_time']) >= 18 * 60]  # 6 PM or later
            if evening_slots:
                selected_slot = evening_slots[-1].copy()
                # Suggest a time within the actual slot
                slot_start_minutes = self._time_to_minutes(selected_slot['start_time'])
                slot_end_minutes = self._time_to_minutes(selected_slot['end_time'])
                # Suggest evening time, but not after slot ends
                suggested_minutes = min(slot_end_minutes - 60, 20 * 60)  # 8 PM or 1 hour before slot ends
                suggested_minutes = max(suggested_minutes, slot_start_minutes)  # But not before slot starts
                suggested_time = self._minutes_to_time(suggested_minutes)
        
        # Validate and use the suggested time if it's within the slot
        if self._is_time_in_slot(suggested_time, selected_slot):
            suggested_minutes = self._time_to_minutes(suggested_time)
            selected_slot['start_minutes'] = suggested_minutes
            selected_slot['start_time'] = suggested_time
            print(f"Fallback Selected: {'Work' if is_work else 'Personal' if is_personal else 'Evening'} task at {suggested_time} (within slot {selected_slot['start_time']}-{selected_slot['end_time']})")
        else:
            print(f"Fallback: Suggested time {suggested_time} not valid for slot, using slot start time {selected_slot['start_time']}")
        
        selected_slot['ai_reasoning'] = f"Fallback scheduling: {'Work' if is_work else 'Personal' if is_personal else 'Evening'} task scheduled at {selected_slot['start_time']}"
        selected_slot['estimated_duration'] = estimated_duration
        
        print(f"Fallback Reasoning: {selected_slot['ai_reasoning']}")
        
        return selected_slot

    def _format_slots_for_ai(self, free_slots: List[Dict]) -> str:
        """Format time slots for AI prompt"""
        formatted = []
        for i, slot in enumerate(free_slots):
            formatted.append(f"Slot {i}: {slot['start_time']} - {slot['end_time']} ({slot['duration_minutes']} min)")
        return "\n".join(formatted)
    
    def _is_time_in_slot(self, suggested_time: str, slot: Dict) -> bool:
        """Check if a suggested time is within a slot's time range"""
        try:
            suggested_minutes = self._time_to_minutes(suggested_time)
            
            # Handle both start_minutes/end_minutes and start_time/end_time formats
            if 'start_minutes' in slot and 'end_minutes' in slot:
                slot_start = slot['start_minutes']
                slot_end = slot['end_minutes']
            elif 'start_time' in slot and 'end_time' in slot:
                slot_start = self._time_to_minutes(slot['start_time'])
                slot_end = self._time_to_minutes(slot['end_time'])
            else:
                return False
            
            return slot_start <= suggested_minutes <= slot_end
        except Exception as e:
            print(f"Error validating time in slot: {e}")
            return False
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string (HH:MM) to minutes since midnight"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to time string (HH:MM)"""
        try:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours:02d}:{mins:02d}"
        except:
            return "00:00" 