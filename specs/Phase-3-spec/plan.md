# Implementation Plan: Phase 3 - Todo AI Chatbot

## Technical Context

### Overview
This plan implements Phase 3 of the Todo Application, which adds an AI chatbot interface to the existing Phase 2 full-stack todo application. The system will use OpenAI ChatKit UI, OpenAI Agent SDK, MCP Server, and integrate with the existing Phase 2 backend with JWT authentication.

### Architecture Components
- **Frontend**: Next.js with ChatKit UI components
- **Backend**: FastAPI handling authentication, chat orchestration, and database operations
- **AI Agent**: OpenAI Agent SDK performing reasoning and decision-making
- **MCP Server**: Model Context Protocol server acting as tool bridge
- **Database**: Neon PostgreSQL with existing Task table and new Conversation/Message tables
- **Authentication**: Better Auth with JWT tokens from Phase 2

### System Flow
```
User (ChatKit UI) → ChatKit SDK → OpenAI Agent SDK → MCP Server → FastAPI Backend → Neon PostgreSQL
```

### Dependencies
- OpenAI API key
- ChatKit domain key
- Neon DB credentials
- Phase 2 backend (assumed to be working with JWT auth)
- Phase 2 task CRUD endpoints (assumed to be verified)

### Constraints
- MCP server NEVER reads/writes DB directly
- Agent NEVER touches DB directly
- Backend OWNS all business logic and DB operations
- All operations must be scoped by user_id from JWT
- MCP tools must be stateless with no conversation memory
- Phase 2 functionality must remain unchanged

## Constitution Check

Based on the constitution file (`/mnt/d/TODO_APP/skills/TODOCHATBOT/.specify/memory/constitution.md`):

✅ **Phase Continuity Rule**: Will reuse Phase 2 codebase, existing database schema, and authentication logic
✅ **Spec-Driven Development**: Following this plan based on detailed specifications
✅ **Stateless Architecture**: MCP server will be stateless, conversation context persisted in DB
✅ **Separation of Responsibilities**: Clear separation between frontend, backend, agent, and MCP
✅ **Database Usage Rules**: Reusing existing Task table, adding only Conversation and Message tables
✅ **Authentication & User Isolation**: Using JWT from Phase 2 for user isolation
✅ **MCP & AI Constraints**: MCP server will be stateless with only task operations, AI agent will have no direct DB access

## Gates

### Gate 1: Prerequisites Validation
- [ ] Phase 2 backend is working
- [ ] JWT auth tested via REST
- [ ] Tasks CRUD endpoints verified
- [ ] Required accounts (OpenAI API key, ChatKit domain key, Neon DB credentials) available

### Gate 2: Architecture Compliance
- [ ] MCP server is stateless with no DB access
- [ ] AI agent has no direct DB access
- [ ] All operations scoped by user_id from JWT
- [ ] Phase 2 functionality remains unchanged

### Gate 3: Security Validation
- [ ] JWT verification happens in FastAPI backend
- [ ] User data isolation enforced by user_id
- [ ] MCP tools properly attach JWT to backend requests
- [ ] No direct DB access from MCP or agent

## Phase 0: Outline & Research

### 0.1 Unknowns Resolution
- [x] Database schema for Conversation and Message entities - resolved from database-extensions/spec.md
- [x] MCP server setup and tool contract definitions - resolved from mcp-tool-design/spec.md
- [x] ChatKit integration patterns - resolved from frontend-chatkit-integration/spec.md
- [x] Agent behavior model and tool invocation patterns - resolved from agent-behavior-model/spec.md
- [x] Natural language mapping to task operations - resolved from natural-language-mapping/spec.md

### 0.2 Technology Choices Research
- [x] OpenAI Agent SDK integration with MCP tools
- [x] ChatKit UI component setup and configuration
- [x] MCP SDK usage for tool bridge implementation
- [x] FastAPI integration with OpenAI Agent SDK

### 0.3 Integration Patterns
- [x] Frontend → Backend → Agent → MCP → Backend communication flow
- [x] JWT token propagation through the system
- [x] Error handling patterns across all components

## Phase 1: Design & Contracts

### 1.1 Data Model Design

#### Conversation Entity
- id: UUID (primary key)
- user_id: UUID (foreign key to Phase 2 users table)
- created_at: timestamp
- updated_at: timestamp

#### Message Entity
- id: UUID (primary key)
- conversation_id: UUID (foreign key to Conversation)
- user_id: UUID (foreign key to Phase 2 users table, for data isolation)
- role: string (enum: 'user', 'assistant')
- content: TEXT (not null)
- created_at: timestamp

#### Database Schema
- Phase 2 Task table: Reused as-is
- New chat_conversations table: For storing conversation metadata
- New chat_messages table: For storing message history

### 1.2 API Contract Design

#### Backend API Endpoints
- POST `/api/chat/message` - Send user message to AI agent
- GET `/api/chat/history` - Retrieve conversation history
- POST `/api/chat/start` - Start new conversation
- GET `/api/conversations` - List user conversations

#### MCP Tool Contracts
- `add_task`: Create new task through backend API
- `list_tasks`: Retrieve tasks through backend API
- `update_task`: Update existing task through backend API
- `complete_task`: Mark task as complete through backend API
- `delete_task`: Delete task through backend API

### 1.3 Quickstart Documentation

#### Development Setup
1. Install frontend dependencies: `npm install @chatkit/react @chatkit/core`
2. Set environment variables:
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
   - `NEXT_PUBLIC_BACKEND_URL`
   - `DATABASE_URL`
   - `MCP_BACKEND_URL`

#### Running the System
1. Start backend: `uvicorn main:app --reload`
2. Start MCP server: `node mcp-server/index.ts`
3. Start frontend: `npm run dev`

## Phase 2: Implementation Plan

### 2.1 MCP Server Setup 
**Objective**: Create MCP server with tool contracts for task operations

#### Tasks:

##### MANDATORY CLAUDE SKILL

- Claude Code MUST use:
**mcp-server-tools-skill**

###### Allowed:

- Create basic MCP server
- Register tools
- Connect MCP to OpenAI Agent SDK

##### Forbidden:

Implement business logic

Add database access

Implement reasoning logic

🔒 This must be explicit, not implied

1. [ ] Scaffold MCP server directory structure
   - Create `/mcp-server` directory
   - Create `/mcp-server/index.ts` entry point
   - Create `/mcp-server/tools/` for tool implementations
   - Create `/mcp-server/config/` for configuration

2. [ ] Install MCP SDK and dependencies
   - Install official MCP SDK
   - Install required dependencies for HTTP requests to backend

3. [ ] Implement MCP tool contracts
   - Create `add_task` tool with validation and backend API call
   - Create `list_tasks` tool with validation and backend API call
   - Create `update_task` tool with validation and backend API call
   - Create `complete_task` tool with validation and backend API call
   - Create `delete_task` tool with validation and backend API call

4. [ ] Implement JWT token attachment
   - Ensure each MCP tool receives and attaches JWT to backend requests
   - Backend passes JWT to Agent
   - Agent passes JWT to MCP tool call context
   - Validate user_id isolation in MCP tools
   - **MCP forwards JWT; backend enforces user isolation**

5. [ ] Test MCP server locally
   - Verify tool contracts work correctly
   - Confirm stateless operation

### 2.2 Backend API Extensions 
**Objective**: Extend Phase 2 backend with chat-specific endpoints and database models

#### Tasks:
1. [ ] Create database models for chat entities
   - Define `Conversation` SQLModel
   - Define `ChatMessage` SQLModel
   - Add proper foreign key relationships to Phase 2 users

2. [ ] Create database migration scripts
   - Generate Alembic migration for new tables
   - Ensure idempotent migration for production safety

3. [ ] Create chat API endpoints
   - POST `/api/chat/message` - Process user message through agent
   - GET `/api/chat/history` - Retrieve conversation history
   - POST `/api/chat/start` - Initialize new conversation

4. [ ] Implement chat orchestration logic
   - Validate JWT and extract user_id
   - Call OpenAI Agent SDK with conversation context
   - Persist user and assistant messages atomically
   - Handle agent and MCP failures gracefully

5. [ ] Integrate with OpenAI Agent SDK
   - Configure agent to use MCP tools
   - Pass conversation context to agent
   - Handle agent responses

### 2.3 Frontend ChatKit Integration 
**Objective**: Integrate ChatKit UI components with backend chat API

- ChatKit manages UI state only.
Database is the single source of truth for conversations and messages.
ChatKit history must always be hydrated from backend.

#### Tasks:
1. [ ] Install ChatKit dependencies
   - Install `@chatkit/react` and `@chatkit/core`
   - Configure with domain key


2. [ ] Create chat UI components
   - ChatWindow component
   - MessageList component
   - MessageInput component
   - Loading and error states

3. [ ] Implement authentication integration
   - Extract JWT from Phase 2 auth
   - Pass to ChatKit provider
   - Handle authentication errors

4. [ ] Connect to backend API
   - Send messages to `/api/chat/message`
   - Load history from `/api/chat/history`
   - Handle responses and errors

5. [ ] Add conversation management
   - Create new conversations
   - Switch between conversations
   - Display conversation history

### 2.4 Agent Behavior Configuration
**Objective**: Configure OpenAI Agent to properly use MCP tools for task operations

The OpenAI Agent SDK is instantiated and invoked only inside FastAPI backend, never in frontend or MCP.

#### Tasks:
1. [ ] Define agent system prompt
   - Task management capabilities
   - Safety and security boundaries
   - Error handling instructions

2. [ ] Configure tool access
   - Register MCP tools with agent
   - Define tool permissions and scope
   - Set up tool validation

3. [ ] Implement intent classification
   - Map natural language to appropriate tools
   - Agent uses natural language reasoning via OpenAI Agent SDK to select appropriate MCP tools
   - Handle parameter extraction
   - Manage ambiguous requests

4. [ ] Test agent behavior
   - Verify tool usage patterns
   - Confirm safety compliance
   - Validate error handling

### 2.5 Integration & Testing
**Objective**: Integrate all components and test end-to-end functionality

#### Tasks:
1. [ ] End-to-end testing
   - Test complete user journey: chat → agent → MCP → backend → DB
   - Verify JWT token flow through all components
   - Confirm user data isolation

2. [ ] Error scenario testing
   - Test MCP server unavailability
   - Test JWT expiration scenarios
   - Test network failures

3. [ ] Performance testing
   - Test chat history loading with 100+ messages
   - Measure response times
   - Verify database query performance

4. [ ] Security validation
   - Confirm user isolation
   - Verify no direct DB access from agent/MCP
   - Validate authentication enforcement

5. [ ] Clarify
- Backend may retry DB ops
- MCP NEVER retries
- Agent NEVER retries
- This aligns with stateless MCP design.

### 2.6 Deployment Configuration
**Objective**: Prepare system for deployment with proper environment configuration

#### Tasks:
1. [ ] Configure environment variables
   - Set up NEXT_PUBLIC_OPENAI_DOMAIN_KEY
   - Configure  NEXT_PUBLIC_BACKEND_URL
   - Set DATABASE_URL and use JWT who used in backend created by better auth while authentication 
   - Configure MCP_BACKEND_URL

2. [ ] Create deployment scripts
   - Backend deployment script
   - MCP server deployment script
   - Frontend deployment script

3. [ ] Test deployment process
   - Deploy to staging environment
   - Verify all components communicate properly
   - Test end-to-end functionality in deployed environment

## Phase 3: Deployment & Validation

### 3.1 Production Deployment
- Deploy frontend to Vercel
- Deploy backend to VPS/Render
- Deploy MCP server as Node server
- Verify all environment variables are set correctly

### 3.2 Post-Deployment Validation
- Verify Phase 2 functionality remains operational
- Confirm AI chatbot works as expected
- Validate user data isolation
- Monitor system performance

## Success Criteria Validation

### Measurable Outcomes
- [ ] Phase 2 task management functionality remains 100% operational after Phase 3 integration
- [ ] Users can successfully create, read, update, and delete tasks through natural language commands (target: 90% accuracy)
- [ ] All user data remains properly isolated with no cross-user access to tasks or conversations (target: 100% accuracy)
- [ ] The system maintains security compliance with JWT-based authentication and authorization
- [ ] Natural language task management operations complete with at least 90% accuracy for common commands
- [ ] Chat messages are successfully stored in the database with proper user ownership and conversation grouping
- [ ] Chat history loads within 3 seconds for conversations containing up to 100 messages
- [ ] Agent correctly classifies user intent with 90% accuracy across different natural language expressions
- [ ] Agent maintains 99% compliance with safety and architectural boundaries (no direct DB access attempts)
- [ ] MCP tools successfully validate 99% of input arguments before making backend API calls
- [ ] All API endpoints successfully authenticate 100% of requests using JWT tokens from Phase 2 Better Auth
- [ ] User data isolation is maintained with 100% accuracy (no cross-user data access)

## Risk Mitigation

### High-Risk Areas
1. **Security**: Implement strict input validation and user isolation
2. **Performance**: Optimize database queries and implement proper indexing
3. **Reliability**: Implement proper error handling and retry mechanisms
4. **Integration**: Thorough testing of component communication

### Contingency Plans
1. **MCP Server Failure**: Implement graceful degradation to error messages
2. **Agent Unavailability**: Provide fallback responses to users
3. **Database Issues**: Implement proper error handling and alerting
4. **Authentication Problems**: Ensure secure fallback mechanisms

## Timeline
- **Week 1**: MCP Server setup and Backend API extensions (partial)
- **Week 2**: Backend API completion and Frontend integration
- **Week 3**: Agent configuration, integration testing, and deployment

## Resources Required
- OpenAI API subscription
- ChatKit domain access
- Hosting infrastructure for backend and MCP server
- Time allocation for comprehensive testing