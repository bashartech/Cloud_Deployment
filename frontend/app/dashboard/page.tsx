
"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { api, type Task } from "@/lib/api"
import { useRouter } from "next/navigation"
import TaskItem from "@/components/task/TaskItem"
import TaskReminder from "@/components/task/TaskReminder"
import Logout from "@/components/logout"
import LoadingSpinner from "@/components/LoadingSpinner"
import FloatingChatbot from "@/components/chat/FloatingChatbot"
import { authClient } from "@/lib/auth-client"

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [authChecked, setAuthChecked] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const checkAuthAndLoadData = async () => {
      try {
        // Check if user is authenticated
        const session = await authClient.getSession();
        if (!session) {
          // If not authenticated, redirect to login
          router.push("/login");
          return;
        }
        
        // Wait a bit for session to be fully established
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Now fetch tasks
        const tasksData = await api.tasks.getTasks();
        setTasks(tasksData);
      } catch (error) {
        console.error("Auth check or task fetch failed:", error);
        router.push("/login");
      } finally {
        setLoading(false);
        setAuthChecked(true);
      }
    };

    checkAuthAndLoadData();
  }, [router]);
  const [newTaskTitle, setNewTaskTitle] = useState("")
  const [newTaskDescription, setNewTaskDescription] = useState("")
  const [newTaskPriority, setNewTaskPriority] = useState<"low" | "medium" | "high">("medium")
  const [newTaskTags, setNewTaskTags] = useState("")
  const [newTaskDueDate, setNewTaskDueDate] = useState("")
  const [newTaskIsRecurring, setNewTaskIsRecurring] = useState(false)
  const [newTaskRecurrenceType, setNewTaskRecurrenceType] = useState<"daily" | "weekly" | "monthly">("weekly")
  const [newTaskRecurrenceInterval, setNewTaskRecurrenceInterval] = useState(1)
  const [newTaskReminderAt, setNewTaskReminderAt] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [filterCompleted, setFilterCompleted] = useState<"all" | "pending" | "completed">("all")
  const [filterPriority, setFilterPriority] = useState<"all" | "low" | "medium" | "high">("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [sortField, setSortField] = useState<"created_at" | "due_date" | "priority" | "title">("created_at")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")
  const [isCreatingTask, setIsCreatingTask] = useState(false)
  const [deletingTaskId, setDeletingTaskId] = useState<number | null>(null)
  const [togglingTaskId, setTogglingTaskId] = useState<number | null>(null)
  // const router = useRouter()

  useEffect(() => {
    const checkAuthAndFetchTasks = async () => {
      try {
        // Check if user is authenticated first
        const session = await authClient.getSession();
        if (!session) {
          // If not authenticated, redirect to login
          router.push("/login");
          return;
        }
        
        // Wait a moment for session to be fully established
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Now fetch tasks
        fetchTasks();
      } catch (error) {
        console.error("Auth check failed:", error);
        router.push("/login");
      }
    };
    
    checkAuthAndFetchTasks();
  }, [filterCompleted, filterPriority, searchQuery, sortField, sortOrder, router])


  const fetchTasks = async () => {
    try {
      setLoading(true)
      const tasksData = await api.tasks.getTasks(
        filterCompleted !== "all" ? filterCompleted : undefined,
        filterPriority !== "all" ? filterPriority : undefined,
        searchQuery || undefined,
        sortField,
        sortOrder,
      )
      setTasks(tasksData)
      setError(null)
    } catch (err) {
      setError("Failed to load tasks. Please try again.")
      console.error("Error fetching tasks:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newTaskTitle.trim()) {
      setError("Task title is required")
      return
    }

    try {
      setIsCreatingTask(true)
      setError(null)

      const tagsArray = newTaskTags
        ? newTaskTags
            .split(",")
            .map((tag) => tag.trim())
            .filter((tag) => tag)
        : []

      const newTask = await api.tasks.createTask({
        title: newTaskTitle,
        description: newTaskDescription,
        completed: false,
        priority: newTaskPriority,
        tags: tagsArray,
        due_date: newTaskDueDate || undefined,
        is_recurring: newTaskIsRecurring,
        recurrence_type: newTaskIsRecurring ? newTaskRecurrenceType : undefined,
        recurrence_interval: newTaskIsRecurring ? newTaskRecurrenceInterval : 1,
        reminder_at: newTaskReminderAt || undefined,
      })

      setTasks([newTask, ...tasks])
      setNewTaskTitle("")
      setNewTaskDescription("")
      setNewTaskPriority("medium")
      setNewTaskTags("")
      setNewTaskDueDate("")
      setNewTaskIsRecurring(false)
      setNewTaskRecurrenceType("weekly")
      setNewTaskRecurrenceInterval(1)
      setNewTaskReminderAt("")
      setSuccess("Task created successfully!")

      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError("Failed to create task. Please try again.")
      console.error("Error creating task:", err)
    } finally {
      setIsCreatingTask(false)
    }
  }

  const handleUpdateTask = (updatedTask: Task) => {
    setTasks(tasks.map((task) => (task.id === updatedTask.id ? updatedTask : task)))
  }

  const handleDeleteTask = async (taskId: number) => {
    if (!window.confirm("Are you sure you want to delete this task?")) {
      return
    }

    try {
      setDeletingTaskId(taskId)
      setError(null)
      await api.tasks.deleteTask(taskId)
      setTasks(tasks.filter((task) => task.id !== taskId))
      setSuccess("Task deleted successfully!")

      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError("Failed to delete task. Please try again.")
      console.error("Error deleting task:", err)
    } finally {
      setDeletingTaskId(null)
    }
  }

  const handleToggleTaskCompletion = async (taskId: number) => {
    try {
      setTogglingTaskId(taskId)
      setError(null)
      const updatedTask = await api.tasks.toggleTaskCompletion(taskId)

      setTasks(tasks.map((task) => (task.id === taskId ? updatedTask : task)))
    } catch (err) {
      setError("Failed to update task. Please try again.")
      console.error("Error updating task:", err)
    } finally {
      setTogglingTaskId(null)
    }
  }

  const handleSignOut = async () => {
    try {
      await authClient.signOut()
      router.push("/")
    } catch (err) {
      setError("Failed to sign out. Please try again.")
      console.error("Error signing out:", err)
    }
  }

  const totalTasks = tasks.length
  const completedTasks = tasks.filter((t) => t.completed).length
  const pendingTasks = totalTasks - completedTasks
  const highPriorityTasks = tasks.filter((t) => t.priority === "high" && !t.completed).length

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-600/15 rounded-full blur-3xl animate-pulse"></div>
        <div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-600/15 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: "1s" }}
        ></div>
        <div
          className="absolute top-1/2 right-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: "2s" }}
        ></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12 animate-fade-in">
          <div>
            <h1 className="text-4xl md:text-5xl font-black bg-gradient-to-r from-white via-blue-200 to-cyan-200 bg-clip-text text-transparent mb-3">
              Task Dashboard
            </h1>
            <p className="text-gray-400 text-lg">Organize, prioritize, and achieve your goals</p>
          </div>
          <button
            onClick={handleSignOut}
            className="px-8 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-semibold rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-red-500/20 whitespace-nowrap"
          >
            Sign Out
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10 animate-slide-up">
          <div className="group bg-gradient-to-br from-neutral-900 to-neutral-950 border border-neutral-800/50 rounded-xl p-6 hover:border-blue-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10 hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium mb-2">Total Tasks</p>
                <p className="text-3xl md:text-4xl font-bold text-white">{totalTasks}</p>
                <p className="text-xs text-gray-500 mt-2">All your tasks</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center group-hover:bg-blue-500/30 transition-all">
                <svg className="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div className="group bg-gradient-to-br from-neutral-900 to-neutral-950 border border-neutral-800/50 rounded-xl p-6 hover:border-green-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-green-500/10 hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium mb-2">Completed</p>
                <p className="text-3xl md:text-4xl font-bold text-white">{completedTasks}</p>
                <p className="text-xs text-green-500 mt-2">
                  {totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0}% done
                </p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center group-hover:bg-green-500/30 transition-all">
                <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div className="group bg-gradient-to-br from-neutral-900 to-neutral-950 border border-neutral-800/50 rounded-xl p-6 hover:border-yellow-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-yellow-500/10 hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium mb-2">Pending</p>
                <p className="text-3xl md:text-4xl font-bold text-white">{pendingTasks}</p>
                <p className="text-xs text-yellow-500 mt-2">
                  {totalTasks > 0 ? Math.round((pendingTasks / totalTasks) * 100) : 0}% remaining
                </p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center group-hover:bg-yellow-500/30 transition-all">
                <svg className="w-6 h-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div className="group bg-gradient-to-br from-neutral-900 to-neutral-950 border border-neutral-800/50 rounded-xl p-6 hover:border-red-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-red-500/10 hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium mb-2">High Priority</p>
                <p className="text-3xl md:text-4xl font-bold text-white">{highPriorityTasks}</p>
                <p className="text-xs text-red-500 mt-2">Urgent items</p>
              </div>
              <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center group-hover:bg-red-500/30 transition-all">
                <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/15 border border-red-500/30 text-red-300 rounded-lg backdrop-blur-sm animate-slide-down">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414 1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              {error}
            </div>
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-green-500/15 border border-green-500/30 text-green-300 rounded-lg backdrop-blur-sm animate-slide-down">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              {success}
            </div>
          </div>
        )}

        <div className="bg-gradient-to-br from-neutral-900 to-neutral-950 border border-neutral-800/50 rounded-xl p-6 mb-8 animate-slide-up">
          <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            Search &amp; Filter Tasks
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="lg:col-span-2">
              <label className="block text-sm font-semibold text-gray-300 mb-2">Search</label>
              <div className="relative">
                <svg
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500 pointer-events-none"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                  placeholder="Search by title or description..."
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Status</label>
              <select
                value={filterCompleted}
                onChange={(e) => setFilterCompleted(e.target.value as "all" | "pending" | "completed")}
                className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300 cursor-pointer"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Priority</label>
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value as "all" | "low" | "medium" | "high")}
                className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300 cursor-pointer"
              >
                <option value="all">All Priorities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Sort By</label>
              <select
                value={sortField}
                onChange={(e) => setSortField(e.target.value as "created_at" | "due_date" | "priority" | "title")}
                className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300 cursor-pointer"
              >
                <option value="created_at">Created Date</option>
                <option value="due_date">Due Date</option>
                <option value="priority">Priority</option>
                <option value="title">Title A-Z</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-neutral-900 to-neutral-950 border border-neutral-800/50 rounded-xl p-8 mb-10 animate-slide-up">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <svg className="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create New Task
          </h2>
          <form onSubmit={handleCreateTask} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Task Title *</label>
              <input
                type="text"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                placeholder="What needs to be done?"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Description</label>
              <textarea
                value={newTaskDescription}
                onChange={(e) => setNewTaskDescription(e.target.value)}
                className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                placeholder="Add task details (optional)"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Priority</label>
                <select
                  value={newTaskPriority}
                  onChange={(e) => setNewTaskPriority(e.target.value as "low" | "medium" | "high")}
                  className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300 cursor-pointer"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Due Date</label>
                <input
                  type="date"
                  value={newTaskDueDate}
                  onChange={(e) => setNewTaskDueDate(e.target.value)}
                  className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Tags</label>
                <input
                  type="text"
                  value={newTaskTags}
                  onChange={(e) => setNewTaskTags(e.target.value)}
                  className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                  placeholder="work, urgent, bug"
                />
              </div>
            </div>

            {/* Recurring Task Section */}
            <div className="pt-4 border-t border-neutral-800/50">
              <div className="flex items-center mb-4">
                <input
                  type="checkbox"
                  id="isRecurring"
                  checked={newTaskIsRecurring}
                  onChange={(e) => setNewTaskIsRecurring(e.target.checked)}
                  className="w-5 h-5 text-blue-600 bg-neutral-800/50 border-neutral-700 rounded focus:ring-blue-500 focus:ring-2"
                />
                <label htmlFor="isRecurring" className="ml-2 text-sm font-semibold text-gray-300">
                  Make this a recurring task
                </label>
              </div>

              {newTaskIsRecurring && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Recurrence Type</label>
                    <select
                      value={newTaskRecurrenceType}
                      onChange={(e) => setNewTaskRecurrenceType(e.target.value as "daily" | "weekly" | "monthly")}
                      className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300 cursor-pointer"
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Interval</label>
                    <input
                      type="number"
                      min="1"
                      value={newTaskRecurrenceInterval}
                      onChange={(e) => setNewTaskRecurrenceInterval(parseInt(e.target.value) || 1)}
                      className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                      placeholder="1"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Reminder Section */}
            <div className="pt-4 border-t border-neutral-800/50">
              <label className="block text-sm font-semibold text-gray-300 mb-2">Set Reminder</label>
              <input
                type="datetime-local"
                value={newTaskReminderAt}
                onChange={(e) => setNewTaskReminderAt(e.target.value)}
                className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300"
                placeholder="Select reminder time"
              />
            </div>

            <button
              type="submit"
              disabled={isCreatingTask}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold rounded-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isCreatingTask ? (
                <>
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Creating...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create Task
                </>
              )}
            </button>
          </form>
        </div>

        <div className="bg-gradient-to-br from-neutral-900 to-neutral-950 border border-neutral-800/50 rounded-xl overflow-hidden animate-slide-up">
          <div className="px-6 py-5 border-b border-neutral-800/50 bg-gradient-to-r from-neutral-900 to-neutral-950">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
              Your Tasks ({totalTasks})
            </h2>
          </div>

          {loading ? (
            <div className="p-12 text-center">
              <LoadingSpinner message="Loading your tasks..." />
              <p className="mt-4 text-gray-400">Loading your tasks...</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="p-12 text-center">
              <svg
                className="w-16 h-16 text-gray-600 mx-auto mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
              <p className="text-gray-400 text-lg">No tasks yet. Create your first task above!</p>
              <p className="text-gray-500 text-sm mt-2">Get started by adding a new task to your dashboard.</p>
            </div>
          ) : (
            <ul className="divide-y divide-neutral-800/50">
              {tasks.map((task, idx) => (
                <div key={task.id} style={{ animationDelay: `${idx * 0.05}s` }} className="animate-fade-in">
                  <TaskItem
                    task={task}
                    onUpdate={handleUpdateTask}
                    onDelete={handleDeleteTask}
                    onToggleCompletion={handleToggleTaskCompletion}
                    isDeleting={deletingTaskId}
                    isToggling={togglingTaskId}
                  />
                </div>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Task Reminder Component - Handles browser notifications for task reminders */}
      <TaskReminder tasks={tasks} />

      {/* Floating chatbot component - only available on dashboard */}
      <FloatingChatbot />
    </div>
  )
}
