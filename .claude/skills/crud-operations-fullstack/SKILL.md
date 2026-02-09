---
name: "crud-operations-fullstack"
description: "Complete CRUD (Create, Read, Update, Delete) operations implementation across frontend, backend, and database layers. Provides a comprehensive workflow for building full-stack CRUD applications with proper data flow, validation, and error handling."
version: "1.0.0"
---

# Full-Stack CRUD Operations Skill

## When to Use
- Building full-stack applications with data management capabilities
- Implementing Create, Read, Update, Delete operations for entities
- Setting up frontend-backend communication for data operations
- Creating database-backed applications with user interfaces
- Establishing proper data validation and error handling across layers

## Procedure

### 1. Frontend Implementation
1. Create data models and TypeScript interfaces for entities
2. Implement API client for backend communication
3. Build reusable UI components for CRUD operations
4. Create forms with validation and error handling
5. Implement data fetching and state management
6. Add loading states and user feedback mechanisms

### 2. Backend Implementation
1. Design RESTful API endpoints for CRUD operations
2. Implement request validation and sanitization
3. Create service layer for business logic
4. Implement proper authentication and authorization
5. Add error handling and logging
6. Set up database connection and query execution

### 3. Database Implementation
1. Design database schema with proper relationships
2. Create migration files for schema changes
3. Implement database models/entities
4. Set up connection pooling and optimization
5. Add indexes for performance optimization
6. Implement data validation at database level

### 4. Integration and Testing
1. Connect frontend to backend API
2. Test all CRUD operations end-to-end
3. Implement proper error handling across layers
4. Add security measures and input validation
5. Set up monitoring and logging
6. Document API endpoints and data structures

## Output Format

### Frontend Components Structure
```
components/
├── forms/
│   ├── EntityCreateForm.tsx
│   ├── EntityEditForm.tsx
│   └── EntityDeleteModal.tsx
├── lists/
│   └── EntityList.tsx
├── items/
│   └── EntityItem.tsx
└── shared/
    ├── LoadingSpinner.tsx
    └── ErrorMessage.tsx
```

### Backend API Structure
```
routes/
├── entities/
│   ├── create.py
│   ├── read.py
│   ├── update.py
│   └── delete.py
services/
├── entity_service.py
└── validation_service.py
models/
├── entity_model.py
└── request_models.py
```

### Database Schema Structure
```
tables/
├── entities
├── relationships
└── indexes
migrations/
├── 001_create_entities_table.sql
├── 002_add_indexes.sql
└── 003_add_relationships.sql
```

## Complete CRUD Implementation Guide

### Frontend CRUD Implementation

#### 1. Entity Model Definition
```typescript
// types/entity.ts
export interface BaseEntity {
  id: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Entity extends BaseEntity {
  title: string;
  description?: string;
  status: 'active' | 'inactive' | 'archived';
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  tags: string[];
}

export interface CreateEntityRequest {
  title: string;
  description?: string;
  status?: 'active' | 'inactive';
  priority?: 'low' | 'medium' | 'high';
  dueDate?: Date;
  tags?: string[];
}

export interface UpdateEntityRequest {
  title?: string;
  description?: string;
  status?: 'active' | 'inactive' | 'archived';
  priority?: 'low' | 'medium' | 'high';
  dueDate?: Date;
  tags?: string[];
}
```

#### 2. API Client Implementation
```typescript
// lib/api-client.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

class ApiClient {
  private client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Add authentication token to requests
  setAuthToken(token: string) {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  removeAuthToken() {
    delete this.client.defaults.headers.common['Authorization'];
  }

  // Create Entity
  async createEntity(entity: CreateEntityRequest): Promise<ApiResponse<Entity>> {
    try {
      const response = await this.client.post('/entities', entity);
      return { data: response.data };
    } catch (error: any) {
      return {
        data: {} as Entity,
        error: error.response?.data?.message || error.message
      };
    }
  }

  // Read All Entities
  async getEntities(
    page: number = 1,
    limit: number = 10,
    filters?: { status?: string; priority?: string; search?: string }
  ): Promise<ApiResponse<{ entities: Entity[]; total: number; page: number; pages: number }>> {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        ...(filters?.status && { status: filters.status }),
        ...(filters?.priority && { priority: filters.priority }),
        ...(filters?.search && { search: filters.search }),
      });

      const response = await this.client.get(`/entities?${params}`);
      return { data: response.data };
    } catch (error: any) {
      return {
        data: { entities: [], total: 0, page: 1, pages: 1 },
        error: error.response?.data?.message || error.message
      };
    }
  }

  // Read Single Entity
  async getEntity(id: number): Promise<ApiResponse<Entity>> {
    try {
      const response = await this.client.get(`/entities/${id}`);
      return { data: response.data };
    } catch (error: any) {
      return {
        data: {} as Entity,
        error: error.response?.data?.message || error.message
      };
    }
  }

  // Update Entity
  async updateEntity(id: number, entity: UpdateEntityRequest): Promise<ApiResponse<Entity>> {
    try {
      const response = await this.client.put(`/entities/${id}`, entity);
      return { data: response.data };
    } catch (error: any) {
      return {
        data: {} as Entity,
        error: error.response?.data?.message || error.message
      };
    }
  }

  // Delete Entity
  async deleteEntity(id: number): Promise<ApiResponse<void>> {
    try {
      await this.client.delete(`/entities/${id}`);
      return { data: undefined };
    } catch (error: any) {
      return {
        data: undefined,
        error: error.response?.data?.message || error.message
      };
    }
  }
}

export const apiClient = new ApiClient();
```

#### 3. Form Components with Validation
```tsx
// components/forms/EntityCreateForm.tsx
import React, { useState } from 'react';
import { CreateEntityRequest, Entity } from '@/types/entity';
import { apiClient } from '@/lib/api-client';

interface EntityCreateFormProps {
  onSuccess?: (entity: Entity) => void;
  onCancel?: () => void;
}

export const EntityCreateForm: React.FC<EntityCreateFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<CreateEntityRequest>({
    title: '',
    description: '',
    status: 'active',
    priority: 'medium',
    dueDate: undefined,
    tags: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tagInput, setTagInput] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.createEntity(formData);
      if (result.error) {
        setError(result.error);
      } else if (result.data) {
        onSuccess?.(result.data);
      }
    } catch (err) {
      setError('Failed to create entity');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title *
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700">
            Status
          </label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="archived">Archived</option>
          </select>
        </div>

        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
            Priority
          </label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700">
          Due Date
        </label>
        <input
          type="date"
          id="dueDate"
          name="dueDate"
          value={formData.dueDate ? new Date(formData.dueDate).toISOString().split('T')[0] : ''}
          onChange={(e) => setFormData(prev => ({ ...prev, dueDate: e.target.value ? new Date(e.target.value) : undefined }))}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Tags
        </label>
        <div className="flex mt-1">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
            placeholder="Add a tag and press Enter"
            className="flex-1 rounded-l-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <button
            type="button"
            onClick={handleAddTag}
            className="inline-flex items-center px-3 rounded-r-md border border-l-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm"
          >
            Add
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {formData.tags.map((tag, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
            >
              {tag}
              <button
                type="button"
                onClick={() => handleRemoveTag(tag)}
                className="flex-shrink-0 ml-1.5 h-4 w-4 rounded-full inline-flex items-center justify-center text-indigo-600 hover:bg-indigo-200 hover:text-indigo-800 focus:outline-none focus:bg-indigo-500 focus:text-white"
              >
                <span className="sr-only">Remove</span>
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">{error}</h3>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex justify-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {loading ? 'Creating...' : 'Create Entity'}
        </button>
      </div>
    </form>
  );
};
```

#### 4. List Component for Displaying Entities
```tsx
// components/lists/EntityList.tsx
import React, { useState, useEffect } from 'react';
import { Entity } from '@/types/entity';
import { apiClient } from '@/lib/api-client';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { EntityItem } from '@/components/items/EntityItem';

interface EntityListProps {
  filters?: { status?: string; priority?: string; search?: string };
  onEdit?: (entity: Entity) => void;
  onDelete?: (entity: Entity) => void;
}

export const EntityList: React.FC<EntityListProps> = ({ filters, onEdit, onDelete }) => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    pages: 1
  });

  const fetchEntities = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.getEntities(pagination.page, pagination.limit, filters);
      if (result.error) {
        setError(result.error);
      } else {
        setEntities(result.data.entities);
        setPagination({
          page: result.data.page,
          limit: pagination.limit,
          total: result.data.total,
          pages: result.data.pages
        });
      }
    } catch (err) {
      setError('Failed to load entities');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntities();
  }, [pagination.page, filters]);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= pagination.pages) {
      setPagination(prev => ({ ...prev, page: newPage }));
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">{error}</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {entities.map((entity) => (
            <EntityItem
              key={entity.id}
              entity={entity}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </ul>
      </div>

      {/* Pagination */}
      {pagination.pages > 1 && (
        <nav className="flex items-center justify-between border-t border-gray-200 px-4 py-3 sm:px-0">
          <div className="-mt-px flex w-0 flex-1">
            <button
              onClick={() => handlePageChange(pagination.page - 1)}
              disabled={pagination.page === 1}
              className="inline-flex items-center border-t-2 border-transparent pr-1 pt-4 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700 disabled:opacity-50"
            >
              <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Previous
            </button>
          </div>

          <div className="hidden md:flex md:flex-1 md:items-center md:justify-center">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{(pagination.page - 1) * pagination.limit + 1}</span> to{' '}
                <span className="font-medium">
                  {Math.min(pagination.page * pagination.limit, pagination.total)}
                </span>{' '}
                of <span className="font-medium">{pagination.total}</span> results
              </p>
            </div>
          </div>

          <div className="-mt-px flex w-0 flex-1 justify-end">
            <button
              onClick={() => handlePageChange(pagination.page + 1)}
              disabled={pagination.page === pagination.pages}
              className="inline-flex items-center border-t-2 border-transparent pl-1 pt-4 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700 disabled:opacity-50"
            >
              Next
              <svg className="ml-3 h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </nav>
      )}
    </div>
  );
};
```

### Backend CRUD Implementation

#### 1. API Models and Validation
```python
# models/entity_model.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class EntityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: StatusEnum = StatusEnum.active
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    tags: List[str] = []

class EntityCreate(EntityBase):
    pass

class EntityUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

class EntityResponse(EntityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

#### 2. Database Models (SQLModel)
```python
# models/database_entity.py
from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional, List
from datetime import datetime

class DatabaseEntity(SQLModel, table=True):
    __tablename__ = "entities"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="active", max_length=20)
    priority: str = Field(default="medium", max_length=20)
    due_date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    tags: str = Field(default="[]", max_length=1000)  # JSON string for tags
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### 3. CRUD Service Layer
```python
# services/entity_service.py
from sqlmodel import Session, select, and_
from typing import List, Optional
from datetime import datetime
from ..models.database_entity import DatabaseEntity
from ..models.entity_model import EntityCreate, EntityUpdate

class EntityService:
    @staticmethod
    def create_entity(session: Session, entity_data: EntityCreate) -> DatabaseEntity:
        """Create a new entity in the database."""
        # Convert tags list to JSON string
        tags_json = str(entity_data.tags) if entity_data.tags else "[]"

        db_entity = DatabaseEntity(
            title=entity_data.title,
            description=entity_data.description,
            status=entity_data.status.value,
            priority=entity_data.priority.value,
            due_date=entity_data.due_date,
            tags=tags_json
        )

        session.add(db_entity)
        session.commit()
        session.refresh(db_entity)
        return db_entity

    @staticmethod
    def get_entity_by_id(session: Session, entity_id: int) -> Optional[DatabaseEntity]:
        """Get an entity by its ID."""
        return session.get(DatabaseEntity, entity_id)

    @staticmethod
    def get_entities(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[DatabaseEntity]:
        """Get multiple entities with optional filtering and pagination."""
        query = select(DatabaseEntity)

        # Apply filters
        conditions = []
        if status:
            conditions.append(DatabaseEntity.status == status)
        if priority:
            conditions.append(DatabaseEntity.priority == priority)
        if search:
            conditions.append(DatabaseEntity.title.contains(search))

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(DatabaseEntity.created_at.desc())

        return session.exec(query).all()

    @staticmethod
    def get_entities_count(
        session: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        """Get the count of entities with optional filtering."""
        query = select(DatabaseEntity)

        # Apply filters
        conditions = []
        if status:
            conditions.append(DatabaseEntity.status == status)
        if priority:
            conditions.append(DatabaseEntity.priority == priority)
        if search:
            conditions.append(DatabaseEntity.title.contains(search))

        if conditions:
            query = query.where(and_(*conditions))

        return session.exec(query).count()

    @staticmethod
    def update_entity(
        session: Session,
        entity_id: int,
        entity_data: EntityUpdate
    ) -> Optional[DatabaseEntity]:
        """Update an existing entity."""
        db_entity = session.get(DatabaseEntity, entity_id)
        if not db_entity:
            return None

        # Update fields that are provided
        update_data = entity_data.model_dump(exclude_unset=True)
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = str(update_data['tags'])

        for field, value in update_data.items():
            setattr(db_entity, field, value)

        # Update the updated_at timestamp
        db_entity.updated_at = datetime.utcnow()

        session.add(db_entity)
        session.commit()
        session.refresh(db_entity)
        return db_entity

    @staticmethod
    def delete_entity(session: Session, entity_id: int) -> bool:
        """Delete an entity by its ID."""
        db_entity = session.get(DatabaseEntity, entity_id)
        if not db_entity:
            return False

        session.delete(db_entity)
        session.commit()
        return True
```

#### 4. API Route Handlers
```python
# routes/entities.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from ..db import get_session
from ..models.entity_model import EntityCreate, EntityUpdate, EntityResponse
from ..services.entity_service import EntityService
from ..auth import get_user_id_from_token  # Assuming authentication is required

router = APIRouter(prefix="/entities", tags=["entities"])

@router.post("/", response_model=EntityResponse)
def create_entity(
    entity: EntityCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_user_id_from_token)  # Authentication
):
    """Create a new entity."""
    try:
        db_entity = EntityService.create_entity(session, entity)
        # Convert tags JSON string back to list for response
        import json
        db_entity.tags = json.loads(db_entity.tags) if db_entity.tags else []
        return db_entity
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating entity: {str(e)}")

@router.get("/", response_model=List[EntityResponse])
def read_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    user_id: str = Depends(get_user_id_from_token)  # Authentication
):
    """Get multiple entities with optional filtering and pagination."""
    try:
        entities = EntityService.get_entities(
            session,
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            search=search
        )

        # Convert tags JSON strings back to lists
        for entity in entities:
            import json
            entity.tags = json.loads(entity.tags) if entity.tags else []

        return entities
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching entities: {str(e)}")

@router.get("/{entity_id}", response_model=EntityResponse)
def read_entity(
    entity_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_user_id_from_token)  # Authentication
):
    """Get a specific entity by ID."""
    try:
        db_entity = EntityService.get_entity_by_id(session, entity_id)
        if not db_entity:
            raise HTTPException(status_code=404, detail="Entity not found")

        # Convert tags JSON string back to list
        import json
        db_entity.tags = json.loads(db_entity.tags) if db_entity.tags else []

        return db_entity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching entity: {str(e)}")

@router.put("/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: int,
    entity: EntityUpdate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_user_id_from_token)  # Authentication
):
    """Update an existing entity."""
    try:
        db_entity = EntityService.update_entity(session, entity_id, entity)
        if not db_entity:
            raise HTTPException(status_code=404, detail="Entity not found")

        # Convert tags JSON string back to list
        import json
        db_entity.tags = json.loads(db_entity.tags) if db_entity.tags else []

        return db_entity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating entity: {str(e)}")

@router.delete("/{entity_id}")
def delete_entity(
    entity_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_user_id_from_token)  # Authentication
):
    """Delete an entity by ID."""
    try:
        success = EntityService.delete_entity(session, entity_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entity not found")

        return {"message": "Entity deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting entity: {str(e)}")

@router.get("/count", response_model=int)
def count_entities(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    user_id: str = Depends(get_user_id_from_token)  # Authentication
):
    """Get the count of entities with optional filtering."""
    try:
        count = EntityService.get_entities_count(
            session,
            status=status,
            priority=priority,
            search=search
        )
        return count
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error counting entities: {str(e)}")
```

### Database CRUD Implementation

#### 1. Database Configuration and Connection
```python
# db.py
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os

def get_database_url():
    """Get the database URL from environment variable with default fallback."""
    return os.getenv("DATABASE_URL", "sqlite:///./test.db")

def get_engine():
    """Get the database engine, dynamically configured from environment."""
    database_url = get_database_url()
    return create_engine(database_url, echo=True)

# Global engine instance
engine = get_engine()

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """
    Create all database tables defined in SQLModel models.

    This function creates the tables in the database based on the
    SQLModel classes defined throughout the application.
    """
    global engine
    # Reload the engine to pick up any environment variable changes
    engine = get_engine()
    print(f"Creating database tables at: {get_database_url()}")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")
```

#### 2. Database Migration Files
```sql
-- migrations/001_create_entities_table.sql
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    priority VARCHAR(20) DEFAULT 'medium',
    due_date TIMESTAMP,
    tags TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entities_status ON entities(status);
CREATE INDEX idx_entities_priority ON entities(priority);
CREATE INDEX idx_entities_created_at ON entities(created_at);
```

```sql
-- migrations/002_add_indexes.sql
CREATE INDEX idx_entities_title ON entities(title);
CREATE INDEX idx_entities_due_date ON entities(due_date);
```

```sql
-- migrations/003_add_relationships.sql
-- Add foreign key relationships if needed for related entities
-- Example: ALTER TABLE related_entities ADD CONSTRAINT fk_entity_id FOREIGN KEY (entity_id) REFERENCES entities(id);
```

#### 3. Database Connection Pooling and Optimization
```python
# db/connection_pool.py
from sqlmodel import create_engine
from sqlalchemy.pool import QueuePool
import os

def get_optimized_engine():
    """Get a database engine with optimized connection pooling."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=False           # Set to True for debugging
    )
```

### Integration and Security

#### 1. Authentication Integration
```python
# auth.py (integration with the CRUD operations)
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from typing import Dict, Optional
from .middleware.jwt_middleware import verify_token

async def get_current_user_id(request: Request) -> str:
    """Extract user ID from JWT token in request headers."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authorization header"
        )

    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )

    return user_id

def get_user_id_from_token(token: str = Depends(HTTPBearer())) -> str:
    """Dependency to get user ID from JWT token."""
    payload = verify_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return payload["sub"]
```

#### 2. Error Handling and Logging
```python
# utils/error_handler.py
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRUDErrorHandler:
    @staticmethod
    def handle_database_error(error: Exception, operation: str) -> HTTPException:
        """Handle database-related errors."""
        logger.error(f"Database error during {operation}: {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        if "duplicate key value violates unique constraint" in str(error):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Entity with this identifier already exists"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during {operation}"
        )

    @staticmethod
    def handle_validation_error(error: Exception, field: str) -> HTTPException:
        """Handle validation-related errors."""
        logger.warning(f"Validation error for field {field}: {str(error)}")

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid value for field {field}: {str(error)}"
        )

    @staticmethod
    def handle_not_found_error(entity_type: str, entity_id: int) -> HTTPException:
        """Handle entity not found errors."""
        logger.info(f"{entity_type} with ID {entity_id} not found")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type} with ID {entity_id} not found"
        )

# Error handling middleware
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the application."""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Path: {request.url.path}")
    logger.error(f"Traceback: {traceback.format_exc()}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

This comprehensive CRUD skill provides:

1. **Complete Frontend Implementation** - TypeScript interfaces, API client, form components, and list displays
2. **Complete Backend Implementation** - Pydantic models, SQLModel database models, service layer, and API routes
3. **Complete Database Implementation** - Schema design, migration files, and optimization
4. **Security Integration** - Authentication and authorization
5. **Error Handling** - Comprehensive error management across all layers
6. **Validation** - Proper input validation at all levels
7. **Performance Optimization** - Connection pooling, indexing, and efficient queries

The skill follows the proper structure from the skill-creator.md with YAML front matter, clear sections, and comprehensive implementation details.