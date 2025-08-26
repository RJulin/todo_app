'use client'

import { useState, useEffect } from 'react'
import { Todo } from '../types/todo'
import TodoForm from '../components/TodoForm'
import TodoList from '../components/TodoList'
import DatePicker from '../components/DatePicker'
import ThemeToggle from '../components/ThemeToggle'
import Toast from '../components/Toast'
import { getTodos, createTodo, updateTodo, deleteTodo, getCalendarStatus, authenticateCalendar, logoutCalendar, scheduleTodoInCalendar } from '../libraries/api'

interface ToastMessage {
  message: string;
  type: 'success' | 'error' | 'info';
}

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [calendarAuthenticated, setCalendarAuthenticated] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)

  useEffect(() => {
    const initApp = async () => {
      const calendarStatus = await getCalendarStatus();
      setCalendarAuthenticated(calendarStatus.authenticated);
      const fetchedTodos = await fetchTodos(selectedDate);
      setTodos(fetchedTodos);
    };
    initApp();
  }, [selectedDate]);

  const checkCalendarStatus = async () => {
    try {
      const status = await getCalendarStatus()
      setCalendarAuthenticated(status.authenticated)
    } catch (error) {
      setCalendarAuthenticated(false)
    }
  }

  const fetchTodos = async (date: Date) => {
    try {
      const formattedDate = date.toISOString().split('T')[0];
      const fetchedTodos = await getTodos(formattedDate);
      setTodos(fetchedTodos);
      return fetchedTodos;
    } catch (error) {
      console.error('Failed to fetch todos:', error);
      return [];
    }
  };

  const handleAddTodo = async (todo: { title: string; description?: string }) => {
    try {
      const newTodo = await createTodo(todo, selectedDate.toISOString().split('T')[0]);
      setTodos(prev => [...prev, newTodo]);
      setToast({ message: '✅ Todo created successfully!', type: 'success' });
    } catch (error) {
      setToast({ message: '❌ Failed to create todo', type: 'error' });
    }
  };

  const handleUpdateTodo = async (id: number, update: { title?: string; description?: string; completed?: boolean }) => {
    try {
      const updatedTodo = await updateTodo(id, update);
      setTodos(prev => prev.map(todo => todo.id === id ? updatedTodo : todo));
      setToast({ message: '✅ Todo updated successfully!', type: 'success' });
    } catch (error) {
      console.error('Failed to update todo:', error);
      setToast({ message: '❌ Failed to update todo', type: 'error' });
    }
  };

  const handleToggleTodo = async (id: number, completed: boolean) => {
    try {
      const updatedTodo = await updateTodo(id, { completed });
      setTodos(prev => prev.map(todo => todo.id === id ? updatedTodo : todo));
      setToast({ 
        message: completed ? '✅ Todo marked as completed!' : '🔄 Todo marked as pending', 
        type: 'success' 
      });
    } catch (error) {
      console.error('Failed to toggle todo:', error);
      setToast({ message: '❌ Failed to update todo', type: 'error' });
    }
  };

  const handleDeleteTodo = async (id: number) => {
    try {
      await deleteTodo(id);
      setTodos(prev => prev.filter(todo => todo.id !== id));
      setToast({ message: '🗑️ Todo deleted successfully!', type: 'success' });
    } catch (error) {
      console.error('Failed to delete todo:', error);
      setToast({ message: '❌ Failed to delete todo', type: 'error' });
    }
  };

  const handleCalendarAuth = async () => {
    try {
      await authenticateCalendar();
      const calendarStatus = await getCalendarStatus();
      setCalendarAuthenticated(calendarStatus.authenticated);
      setToast({ message: 'Calendar connected successfully!', type: 'success' });
    } catch (error) {
      setToast({ message: 'Failed to connect calendar', type: 'error' });
    }
  };

  const handleCalendarLogout = async () => {
    try {
      await logoutCalendar();
      setCalendarAuthenticated(false);
      setToast({ message: 'Calendar disconnected successfully!', type: 'success' });
    } catch (error) {
      setToast({ message: 'Failed to disconnect calendar', type: 'error' });
    }
  };

  const handleScheduleInCalendar = async (todoId: number) => {
    try {
      const result = await scheduleTodoInCalendar(todoId, selectedDate.toISOString().split('T')[0]);
      setToast({ 
        message: `📅 Todo scheduled at ${result.scheduled_time} for ${result.duration} minutes`, 
        type: 'success' 
      });
      // Refresh todos to show the updated calendar_event_id
      const updatedTodos = await fetchTodos(selectedDate);
      setTodos(updatedTodos);
    } catch (error) {
      setToast({ message: '❌ Failed to schedule todo in calendar', type: 'error' });
    }
  };

  const handleDateChange = (date: Date) => {
    setSelectedDate(date);
  };

  const closeToast = () => setToast(null);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI boosted Todo Calendar App</h1>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            {!calendarAuthenticated ? (
              <button
                onClick={handleCalendarAuth}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Connect Calendar
              </button>
            ) : (
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full dark:bg-green-900/20 dark:text-green-300">
                  📅 Calendar Connected
                </span>
                <button
                  onClick={handleCalendarLogout}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                >
                  Disconnect
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <DatePicker selectedDate={selectedDate} onDateChange={handleDateChange} />
        </div>

        <div className="mb-6">
          <TodoForm onAdd={handleAddTodo} onUpdate={handleUpdateTodo} />
        </div>

        <TodoList
          todos={todos}
          onUpdate={handleUpdateTodo}
          onDelete={handleDeleteTodo}
          onScheduleInCalendar={handleScheduleInCalendar}
          onToggle={handleToggleTodo}
          selectedDate={selectedDate.toISOString().split('T')[0]}
        />

        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            isVisible={true}
            onClose={closeToast}
          />
        )}
      </main>
    </div>
  )
} 