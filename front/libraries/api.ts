import { Todo } from '../types/todo'

const API_BASE = 'http://localhost:8000'

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json()
}

export async function getTodos(selectedDate?: string): Promise<Todo[]> {
  const url = selectedDate ? `${API_BASE}/api/todoapp?selected_date=${selectedDate}` : `${API_BASE}/api/todoapp`
  const response = await fetch(url)
  return handleResponse(response)
}

export async function createTodo(todo: { title: string; description?: string }, selectedDate: string): Promise<Todo> {
  const response = await fetch(`${API_BASE}/api/todoapp?selected_date=${selectedDate}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(todo),
  })
  return handleResponse(response)
}

export async function updateTodo(id: number, update: { title?: string; description?: string; completed?: boolean; date?: string }): Promise<Todo> {
  const response = await fetch(`${API_BASE}/api/todoapp/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(update),
  })
  return handleResponse(response)
}

export async function deleteTodo(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/api/todoapp/${id}`, { method: 'DELETE' })
  await handleResponse(response)
}

// Calendar Integration
export async function getCalendarStatus(): Promise<{ authenticated: boolean; message: string }> {
  const response = await fetch(`${API_BASE}/api/calendar/status`)
  return handleResponse(response)
}

export async function authenticateCalendar(): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/api/calendar/auth`, { method: 'POST' })
  return handleResponse(response)
}

export async function scheduleTodoInCalendar(todoId: number, targetDate: string): Promise<{
  message: string;
  scheduled_time: string;
  duration: number;
  ai_reasoning: string;
  free_slots_available: number;
}> {
  const response = await fetch(`${API_BASE}/api/calendar/schedule-todo/${todoId}?target_date=${targetDate}`, {
    method: 'POST',
  })
  return handleResponse(response)
} 