# Quickstart Guide: Phase 3 - Todo AI Chatbot

## Overview
This guide provides step-by-step instructions to set up and run the Phase 3 Todo AI Chatbot system, which extends Phase 2 with natural language task management capabilities.

## Prerequisites

### System Requirements
- Node.js v18+ (for frontend and MCP server)
- Python 3.9+ (for backend)
- PostgreSQL (Neon DB compatible)
- OpenAI API key
- ChatKit domain key

### Environment Setup
1. Ensure Phase 2 backend is running and tested
2. Verify JWT authentication works via REST endpoints
3. Confirm task CRUD endpoints are functional

## Installation Steps

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd /mnt/d/TODO_APP/skills/TODOCHATBOT
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install fastapi uvicorn openai sqlmodel httpx
# Plus other Phase 2 dependencies
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install @chatkit/react @chatkit/core
```

### 4. Install MCP Server Dependencies
```bash
mkdir -p mcp-server
cd mcp-server
npm init -y
npm install @modelcontextprotocol/sdk node-fetch
```

## Environment Configuration

### Backend (.env)
```env
DATABASE_URL="postgresql://..."
JWT_SECRET_KEY="your-jwt-secret-from-phase2"
OPENAI_API_KEY="sk-..."
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_OPENAI_DOMAIN_KEY="your-chatkit-domain-key"
REACT_APP_BACKEND_URL="http://localhost:8000"  # or your backend URL
```

### MCP Server (.env)
```env
MCP_BACKEND_URL="http://localhost:8000"  # your backend URL
BACKEND_JWT_SECRET="same-as-backend"
OPENAI_API_KEY="sk-..."
```

## Database Setup

### 1. Run Phase 2 Migrations
First ensure Phase 2 tables are created:
```bash
cd backend
alembic upgrade head  # This runs Phase 2 migrations
```

### 2. Run Phase 3 Migrations
Apply the new chat-related tables:
```bash
# Run the Phase 3 migration to add chat_conversations and chat_messages tables
# The migration files should include both Phase 2 and Phase 3 tables
```

## Component Startup Sequence

### 1. Start Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Start MCP Server
```bash
cd mcp-server
node index.js
```

### 3. Start Frontend
```bash
cd frontend
npm run dev
```

## Basic Usage

### 1. Navigate to Chat Interface
Open your frontend (typically http://localhost:3000) and navigate to the chat page.

### 2. Authenticate
Log in using Phase 2 authentication system to get valid JWT token.

### 3. Start Chatting
Try these commands:
- "Add a task to buy groceries"
- "Show me my tasks"
- "Mark task 1 as complete"
- "Delete the meeting task"

## API Endpoints

### Backend Chat Endpoints
- `POST /api/chat/message` - Send user message to AI agent
- `GET /api/chat/history` - Get conversation history
- `POST /api/chat/start` - Start new conversation

### MCP Tool Endpoints
- `add_task` - Create new task
- `list_tasks` - Retrieve user's tasks
- `update_task` - Update existing task
- `complete_task` - Mark task as complete
- `delete_task` - Delete task

## Testing the System

### 1. Verify Backend Connection
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/tasks
```

### 2. Test MCP Server
Ensure the MCP server is accessible and tools are registered.

### 3. End-to-End Test
Send a message through the UI and verify:
- Message appears in chat interface
- Task is created in the database
- Confirmation message appears

## Troubleshooting

### Common Issues

#### JWT Token Problems
- Ensure the same JWT_SECRET_KEY is used across all components
- Verify Phase 2 authentication is working
- Check that tokens are properly passed to MCP tools

#### MCP Server Not Responding
- Verify MCP server is running and listening
- Check that backend can reach MCP server
- Confirm tool contracts are properly registered

#### ChatKit Not Initializing
- Verify domain key is correct
- Check network connectivity to ChatKit service
- Ensure frontend environment variables are set

#### Database Connection Issues
- Verify DATABASE_URL is correct
- Ensure Phase 2 tables exist before running Phase 3 migrations
- Check that user isolation is properly configured

## Development Tips

### Local Development
- Use `--reload` flag for backend hot reloading
- MCP server changes require restart
- Frontend hot reloads automatically

### Debugging the Flow
- Check frontend network tab for API calls
- Monitor backend logs for agent processing
- Verify MCP server receives and processes tool calls
- Confirm database operations are successful

## Next Steps

Once the basic system is running:
1. Customize the agent's system prompt for better task management
2. Fine-tune natural language understanding
3. Add more sophisticated error handling
4. Implement conversation threading features
5. Optimize performance for large conversation histories

## Support

For issues with Phase 3 implementation:
- Check that all Phase 2 functionality is intact
- Verify all environment variables are correctly configured
- Confirm JWT tokens are flowing properly through all components
- Review the complete system architecture flow if components aren't communicating