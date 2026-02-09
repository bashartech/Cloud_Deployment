---
name: "Frontend API Integration & User-ID Aware Data Flow"
description: "Implement frontend-to-backend communication that strictly follows the documented API contract, including user_id in URLs, JWT authentication, and filtering/sorting support, ensuring frontend behavior is fully aligned with backend security rules."
version: "1.0.0"
---

# Frontend API Integration & User-ID Aware Data Flow

## When to Use This Skill

Use this skill when you need to:
- Connect a Next.js frontend (App Router) to a secured FastAPI backend
- Implement secure API communication with JWT authentication and user_id in URLs
- Create user-id aware data flows with filtering and sorting support
- Ensure proper API client architecture with centralized request handling
- Handle API responses and errors gracefully in the frontend
- Integrate all task operations (CRUD) with the backend API following the exact contract
- Support filtering and sorting capabilities in the frontend

This skill ensures frontend behavior is fully aligned with backend security rules.

## Process Steps

1. **Implement Centralized API Client**
   - Create a single API abstraction layer for all backend communication
   - Configure base URL using environment variables
   - Implement request interceptors for authentication headers
   - Set up proper error handling and response parsing
   - Create type definitions for API requests and responses

2. **Attach JWT to All Requests**
   - Implement logic to retrieve JWT from secure storage
   - Automatically add `Authorization: Bearer <token>` header to all requests
   - Block unauthenticated requests before sending
   - Handle token refresh if needed
   - Implement proper token storage (preferably httpOnly cookies or secure alternatives)

3. **User-ID Aware API Calls**
   - Extract authenticated user ID from session/auth context
   - Construct API URLs using `{user_id}` parameter (e.g., `/api/{user_id}/tasks`)
   - Never accept manual user ID input from UI
   - Ensure all API calls include the authenticated user ID in the URL

4. **Implement Task Operations**
   - Implement function to fetch user tasks from backend using user_id in URL
   - Create function to add new tasks to backend using user_id in URL
   - Implement function to update existing tasks using user_id in URL
   - Create function to delete tasks from backend using user_id in URL
   - Implement function to toggle task completion using user_id in URL

5. **Filtering & Sorting Integration**
   - Support status filters (all, pending, completed) via query parameters
   - Support sorting options (created, title, due_date) via query parameters
   - Sync UI state with API responses for filtered/sorted data
   - Implement proper parameter validation for filters and sorting

6. **Error Handling & Auth Sync**
   - Handle 401/403 errors centrally in API client
   - Trigger logout on authentication failure
   - Implement proper error message display to users
   - Ensure UI stays synchronized with backend state

## Output Format

The skill will produce:
- Centralized API client for backend communication
- Secure JWT handling in frontend requests with Authorization header
- User-ID aware API calls following backend contract
- Complete integration of task operations with backend API using user_id in URLs
- Filtering and sorting capabilities in UI
- Proper error handling and response management
- UI components that reflect user-ID aware data flow
- Documentation for frontend-backend communication

## Example

**Input:** Integrate Next.js frontend with secured FastAPI backend following user-id aware API contract

**Process:**
```typescript
// lib/api-client.ts
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext'; // Assuming you have an auth context

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('jwt_token'); // Or use secure alternative
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle authentication errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Trigger logout on auth failure
      localStorage.removeItem('jwt_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// types/task.ts
export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

// services/task-service.ts
import apiClient from '../lib/api-client';
import { Task, TaskCreate, TaskUpdate } from '../types/task';

interface TaskFilters {
  status?: 'all' | 'pending' | 'completed';
  sort?: 'created' | 'title' | 'due_date';
}

export const taskService = {
  // Fetch user tasks with filtering and sorting
  getUserTasks: async (userId: number, filters?: TaskFilters): Promise<Task[]> => {
    const params = new URLSearchParams();
    if (filters?.status && filters.status !== 'all') {
      params.append('status', filters.status);
    }
    if (filters?.sort) {
      params.append('sort', filters.sort);
    }

    const queryString = params.toString();
    const url = `/api/${userId}/tasks${queryString ? `?${queryString}` : ''}`;

    const response = await apiClient.get(url);
    return response.data;
  },

  // Create a new task for user
  createUserTask: async (userId: number, taskData: TaskCreate): Promise<Task> => {
    const response = await apiClient.post(`/api/${userId}/tasks`, taskData);
    return response.data;
  },

  // Get specific task for user
  getUserTask: async (userId: number, taskId: number): Promise<Task> => {
    const response = await apiClient.get(`/api/${userId}/tasks/${taskId}`);
    return response.data;
  },

  // Update a task for user
  updateUserTask: async (userId: number, taskId: number, taskData: TaskUpdate): Promise<Task> => {
    const response = await apiClient.put(`/api/${userId}/tasks/${taskId}`, taskData);
    return response.data;
  },

  // Delete a task for user
  deleteUserTask: async (userId: number, taskId: number): Promise<void> => {
    await apiClient.delete(`/api/${userId}/tasks/${taskId}`);
  },

  // Toggle task completion for user
  toggleTaskCompletion: async (userId: number, taskId: number): Promise<Task> => {
    const response = await apiClient.patch(`/api/${userId}/tasks/${taskId}/complete`);
    return response.data;
  },
};

// components/TodoList.tsx (using App Router pattern)
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Task, TaskCreate, TaskUpdate } from '../types/task';
import { taskService } from '../services/task-service';

type StatusFilter = 'all' | 'pending' | 'completed';
type SortField = 'created' | 'title' | 'due_date';

const TodoList = () => {
  const { state: authState } = useAuth(); // Get authenticated user ID from context
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [sortField, setSortField] = useState<SortField>('created');
  const [newTaskTitle, setNewTaskTitle] = useState('');

  useEffect(() => {
    if (authState.isAuthenticated && authState.user?.id) {
      fetchTasks();
    }
  }, [authState.isAuthenticated, authState.user?.id, statusFilter, sortField]);

  const fetchTasks = async () => {
    if (!authState.user?.id) return;

    try {
      setLoading(true);
      const tasksData = await taskService.getUserTasks(authState.user.id, {
        status: statusFilter,
        sort: sortField
      });
      setTasks(tasksData);
    } catch (err) {
      setError('Failed to load tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async () => {
    if (!authState.user?.id || !newTaskTitle.trim()) return;

    try {
      const newTask = await taskService.createUserTask(authState.user.id, {
        title: newTaskTitle,
        description: ''
      });
      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
    } catch (err) {
      setError('Failed to add task');
    }
  };

  const handleUpdateTask = async (id: number, updates: TaskUpdate) => {
    if (!authState.user?.id) return;

    try {
      const updatedTask = await taskService.updateUserTask(authState.user.id, id, updates);
      setTasks(tasks.map(task => task.id === id ? updatedTask : task));
    } catch (err) {
      setError('Failed to update task');
    }
  };

  const handleDeleteTask = async (id: number) => {
    if (!authState.user?.id) return;

    try {
      await taskService.deleteUserTask(authState.user.id, id);
      setTasks(tasks.filter(task => task.id !== id));
    } catch (err) {
      setError('Failed to delete task');
    }
  };

  const handleToggleCompletion = async (id: number) => {
    if (!authState.user?.id) return;

    try {
      const updatedTask = await taskService.toggleTaskCompletion(authState.user.id, id);
      setTasks(tasks.map(task => task.id === id ? updatedTask : task));
    } catch (err) {
      setError('Failed to update task completion');
    }
  };

  if (loading) return <div>Loading tasks...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Your Tasks</h2>

      {/* Filtering and Sorting Controls */}
      <div className="filters">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
        >
          <option value="all">All Tasks</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>

        <select
          value={sortField}
          onChange={(e) => setSortField(e.target.value as SortField)}
        >
          <option value="created">Sort by Created</option>
          <option value="title">Sort by Title</option>
          <option value="due_date">Sort by Due Date</option>
        </select>
      </div>

      {/* Add Task Form */}
      <div className="add-task">
        <input
          type="text"
          value={newTaskTitle}
          onChange={(e) => setNewTaskTitle(e.target.value)}
          placeholder="Add a new task..."
        />
        <button onClick={handleAddTask}>Add Task</button>
      </div>

      {/* Task List */}
      <ul>
        {tasks.map(task => (
          <li key={task.id} className={task.completed ? 'completed' : ''}>
            <span>{task.title}</span>
            <button
              onClick={() => handleToggleCompletion(task.id)}
              className="toggle-btn"
            >
              {task.completed ? 'Undo' : 'Complete'}
            </button>
            <button
              onClick={() => handleDeleteTask(task.id)}
              className="delete-btn"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TodoList;
```

**Output:** A fully integrated frontend that securely communicates with the backend API using user_id in URLs, with proper JWT authentication, filtering and sorting capabilities, ensuring users can only access their own tasks.

## Implementation Rules

- Do NOT hardcode user IDs in API calls (always extract from auth context)
- Do NOT bypass API client for backend communication
- Do NOT call backend without JWT authentication
- Do NOT desync UI from backend state
- Do NOT hardcode API URLs (use environment variables)
- Do NOT store JWT tokens insecurely (avoid plain localStorage for sensitive tokens)
- Do NOT implement direct database access from frontend
- Ensure all API calls include user_id in the URL path
- Implement proper error handling to prevent frontend crashes