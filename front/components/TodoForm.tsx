'use client'

import { useState } from 'react'
import { Plus, X } from 'lucide-react'

interface TodoFormProps {
  onAdd: (todo: { title: string; description?: string }) => void
  onUpdate: (id: number, update: { title?: string; description?: string }) => void
}

export default function TodoForm({ onAdd, onUpdate }: TodoFormProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (title.trim()) {
      onAdd({ title: title.trim(), description: description.trim() || undefined })
      setTitle('')
      setDescription('')
      setIsExpanded(false)
    }
  }

  const handleCancel = () => {
    setTitle('')
    setDescription('')
    setIsExpanded(false)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What needs to be done?"
            className="flex-1 rounded-md border border-gray-300 px-4 py-2 text-base focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
            onFocus={() => setIsExpanded(true)}
          />
          <button
            type="submit"
            disabled={!title.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Plus size={20} />
          </button>
        </div>

        {isExpanded && (
          <>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add description (optional)"
              rows={3}
              className="w-full rounded-md border border-gray-300 px-4 py-2 text-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              >
                <X size={16} />
              </button>
            </div>
          </>
        )}
      </form>
    </div>
  )
} 