'use client'

import { Trash2, CheckCircle, Circle, Pencil, X, Save, Calendar, CalendarCheck } from 'lucide-react'
import { useState } from 'react'
import { Todo } from '../types/todo'

interface TodoListProps {
  todos: Todo[]
  onToggle: (id: number, completed: boolean) => void
  onDelete: (id: number) => void
  onUpdate: (id: number, update: { title?: string; description?: string }) => void
  onScheduleInCalendar?: (id: number) => void
  selectedDate: string
}

export default function TodoList({ todos, onToggle, onDelete, onUpdate, onScheduleInCalendar, selectedDate }: TodoListProps) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')

  const startEdit = (todo: Todo) => {
    setEditingId(todo.id)
    setEditTitle(todo.title)
    setEditDescription(todo.description ?? '')
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditTitle('')
    setEditDescription('')
  }

  const saveEdit = async (id: number) => {
    const payload: { title?: string; description?: string } = {}
    const titleTrim = editTitle.trim()
    const descTrim = editDescription.trim()
    if (titleTrim.length > 0) payload.title = titleTrim
    payload.description = descTrim.length > 0 ? descTrim : undefined
    
    await onUpdate(id, payload)
    cancelEdit()
  }

  const isScheduled = (todo: Todo) => todo.calendar_event_id != null

  if (todos.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-lg text-gray-500 dark:text-gray-400">No todos yet. Add one above!</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {todos.map((todo) => (
        <div
          key={todo.id}
          className={`rounded-lg bg-white p-4 shadow-md dark:bg-gray-800 ${
            todo.completed ? 'opacity-75' : ''
          }`}
        >
          <div className="flex items-start gap-3">
            <button
              onClick={() => onToggle(todo.id, !todo.completed)}
              className="mt-1 text-gray-400 hover:text-green-500 dark:text-gray-500"
            >
              {todo.completed ? (
                <CheckCircle size={24} className="text-green-500" />
              ) : (
                <Circle size={24} />
              )}
            </button>
            
            <div className="min-w-0 flex-1">
              {editingId === todo.id ? (
                <div className="space-y-3">
                  <input
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-base focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
                    placeholder="Title"
                  />
                  <textarea
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200"
                    placeholder="Description (optional)"
                    rows={3}
                  />
                </div>
              ) : (
                <>
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className={`text-lg font-medium ${
                      todo.completed ? 'text-gray-500 line-through dark:text-gray-400' : 'text-gray-900 dark:text-gray-100'
                    }`}>
                      {todo.title}
                    </h3>
                    {isScheduled(todo) && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800 dark:bg-green-900/20 dark:text-green-300">
                        <CalendarCheck size={12} />
                        Scheduled
                      </span>
                    )}
                  </div>
                  {todo.description && (
                    <p className={`text-sm ${
                      todo.completed ? 'text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-300'
                    }`}>
                      {todo.description}
                    </p>
                  )}
                </>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              {editingId === todo.id ? (
                <>
                  <button onClick={() => saveEdit(todo.id)} className="rounded-md border border-gray-300 bg-white p-2 text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800">
                    <Save size={18} />
                  </button>
                  <button onClick={cancelEdit} className="rounded-md border border-gray-300 bg-white p-2 text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800">
                    <X size={18} />
                  </button>
                </>
              ) : (
                <>
                  <button onClick={() => startEdit(todo)} className="rounded-md border border-gray-300 bg-white p-2 text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800">
                    <Pencil size={18} />
                  </button>
                  {onScheduleInCalendar && !todo.completed && !isScheduled(todo) && (
                    <button
                      onClick={() => onScheduleInCalendar(todo.id)}
                      className="rounded-md border border-blue-300 bg-blue-50 p-2 text-blue-700 hover:bg-blue-100 dark:border-blue-600 dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/30"
                      title="Schedule in Google Calendar"
                    >
                      <Calendar size={18} />
                    </button>
                  )}
                  {isScheduled(todo) && (
                    <span className="rounded-md border border-green-300 bg-green-50 p-2 text-green-700 dark:border-green-600 dark:bg-green-900/20 dark:text-green-300" title="Already scheduled in Google Calendar">
                      <CalendarCheck size={18} />
                    </span>
                  )}
                </>
              )}
              <button onClick={() => onDelete(todo.id)} className="p-1 text-gray-400 hover:text-red-500 dark:text-gray-500">
                <Trash2 size={20} />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
} 