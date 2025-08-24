export interface Todo {
  id: number
  title: string
  description?: string
  completed: boolean
  date: string
  calendar_event_id?: string
  created_at: string
  updated_at?: string
} 