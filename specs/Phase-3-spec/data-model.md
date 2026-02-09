# Data Model Design for Phase 3 - Todo AI Chatbot

## Overview
This document defines the data model extensions for Phase 3, which adds chat and conversation capabilities to the existing Phase 2 todo application. The design maintains compatibility with Phase 2 while adding new entities for chat functionality.

## Entity Definitions

### 1. Conversation Entity
Represents a user's chat session with the AI assistant, uniquely identified by a UUID and associated with a specific user.

**Fields:**
- `id`: UUID (Primary Key) - Unique identifier for the conversation
- `user_id`: UUID (Foreign Key) - References the user who owns this conversation (from Phase 2 users table)
- `created_at`: DateTime - Timestamp when conversation was created
- `updated_at`: DateTime - Timestamp when conversation was last updated
- `title`: String (Optional) - Auto-generated title based on first message or conversation topic

**Constraints:**
- `id` must be unique across all conversations
- `user_id` must reference an existing user in Phase 2 users table
- `created_at` defaults to current timestamp
- `updated_at` updates on any conversation activity

**Indexes:**
- Primary index on `id`
- Foreign key index on `user_id` for efficient user-scoped queries
- Composite index on `(user_id, created_at)` for chronological retrieval

### 2. ChatMessage Entity
Represents individual messages in a conversation, containing sender role (user/assistant), content, timestamp, and linking to both conversation and user.

**Fields:**
- `id`: UUID (Primary Key) - Unique identifier for the message
- `conversation_id`: UUID (Foreign Key) - References the conversation this message belongs to
- `user_id`: UUID (Foreign Key) - References the user who sent this message (for data isolation)
- `role`: String (Enum: 'user' | 'assistant') - Indicates whether message is from user or AI assistant
- `content`: TEXT (Not Null) - The actual message content
- `created_at`: DateTime - Timestamp when message was created
- `metadata`: JSONB (Optional) - Additional metadata (tool calls, agent reasoning, etc.)

**Constraints:**
- `id` must be unique across all messages
- `conversation_id` must reference an existing conversation
- `user_id` must reference an existing user in Phase 2 users table
- `role` must be either 'user' or 'assistant'
- `content` cannot be empty
- `created_at` defaults to current timestamp

**Indexes:**
- Primary index on `id`
- Foreign key index on `conversation_id` for conversation-scoped queries
- Foreign key index on `user_id` for user-scoped queries
- Composite index on `(conversation_id, created_at)` for chronological message retrieval
- Composite index on `(user_id, conversation_id)` for efficient user conversation queries

### 3. Relationship with Phase 2 Entities

#### Task Entity (from Phase 2 - UNCHANGED)
- The existing Task entity from Phase 2 remains completely unchanged
- No modifications to Phase 2 Task table schema
- All task operations continue through existing Phase 2 endpoints

#### User Entity (from Phase 2 - UNCHANGED)
- The existing User entity from Phase 2 remains completely unchanged
- MCP tools will use the existing user_id from Phase 2 authentication
- No modifications to Phase 2 User table schema

## Database Schema SQL

```sql
-- Conversation table
CREATE TABLE IF NOT EXISTS chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Chat message table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB,
    FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_chat_conversations_user_id ON chat_conversations(user_id);
CREATE INDEX idx_chat_conversations_user_created ON chat_conversations(user_id, created_at);
CREATE INDEX idx_chat_messages_conversation_id ON chat_messages(conversation_id);
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_conv_created ON chat_messages(conversation_id, created_at);
CREATE INDEX idx_chat_messages_user_conv ON chat_messages(user_id, conversation_id);
```

## Validation Rules

### Conversation Validation
- Creation requires valid user_id from authenticated session
- Title is optional and auto-generated if not provided
- Updated_at field automatically updates on any conversation activity

### Message Validation
- Role must be either 'user' or 'assistant'
- Content must not be empty or null
- Both conversation_id and user_id must exist and be valid
- Message must belong to a conversation owned by the same user

## Access Control Rules

### User Isolation
- All queries must include user_id filter to prevent cross-user access
- Conversation and message retrieval scoped by authenticated user
- MCP tools must verify user_id matches authenticated user from JWT

### Permission Model
- Users can only access their own conversations and messages
- Backend enforces user_id validation on all requests
- MCP tools inherit user context from JWT and enforce same restrictions

## Business Logic Constraints

### Atomic Operations
- User message and assistant response saved as atomic transaction pair
- If agent fails to respond, neither user nor assistant message is persisted
- MCP tools ensure transactional integrity for multi-step operations

### Data Integrity
- Foreign key constraints prevent orphaned records
- Cascade deletion removes messages when conversation is deleted
- Check constraints enforce valid role values

## Performance Considerations

### Query Optimization
- Common queries: user's conversations, conversation messages
- Indexes optimized for user-scoped and chronological access patterns
- Pagination support for large conversation histories

### Scalability
- UUID primary keys ensure global uniqueness
- Efficient indexing for high-volume message storage
- Metadata field supports flexible future requirements

## Migration Strategy

### Idempotent Migration
- CREATE TABLE IF NOT EXISTS prevents duplicate table creation
- Index creation is also idempotent
- Migration script can be safely re-run without data loss

### Backward Compatibility
- Phase 2 functionality remains unchanged
- Existing Task and User tables are unaffected
- All Phase 2 operations continue to work identically

## Security Measures

### Data Protection
- No sensitive information stored in plaintext
- User isolation enforced at database level
- Audit trail through created_at timestamps

### Access Validation
- All operations validated against authenticated user context
- MCP tools must verify user permissions before database operations
- Backend enforces same security rules regardless of access path