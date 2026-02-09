# Todo AI Chatbot - Phase 3 Implementation

## Overview
This repository contains the Todo AI Chatbot, an extension of the Phase 2 Todo Application that adds AI-powered task management capabilities using natural language processing.

## Features
- Natural language task management (add, list, complete, delete, update tasks)
- AI-powered chat interface with conversation history
- Secure user authentication and data isolation
- MCP (Model Context Protocol) integration for AI tools
- Real-time chat interface with ChatKit UI

## Architecture
- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, ChatKit UI
- **Backend**: FastAPI with SQLModel ORM, Neon PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **AI Agent**: OpenAI Agent SDK with MCP tools
- **MCP Tools**: Custom tools for task management operations

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL or Neon database
- Better Auth configured

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
DATABASE_URL="your_database_url"
NEXT_PUBLIC_BETTER_AUTH_URL="your_auth_url"
NEXT_PUBLIC_BETTER_AUTH_SECRET="your_auth_secret"
GEMINI_API_KEY="your_gemini_api_key"
MCP_SERVER_URL="http://localhost:3001"
```

4. Run the backend:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables in `.env`:
```env
NEXT_PUBLIC_BETTER_AUTH_URL="your_auth_url"
NEXT_PUBLIC_BETTER_AUTH_SECRET="your_auth_secret"
NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
```

4. Run the development server:
```bash
npm run dev
```

### MCP Server Setup
1. Navigate to the MCP server directory:
```bash
cd mcp-server
```

2. Install dependencies:
```bash
npm install
```

3. Run the MCP server:
```bash
npm start
```

## ChatKit Domain Configuration

For the chat interface to work properly, you need to configure ChatKit domain allowlist:

1. In your ChatKit configuration, add your domain to the allowed origins
2. For local development: `http://localhost:3000`
3. For production: your production domain

## Usage

### Chat Interface
The AI chatbot is available as a floating chat widget on all authenticated pages:
- Click the chat icon in the bottom-right corner
- Type natural language commands to manage tasks
- Examples:
  - "Add a task to buy groceries"
  - "Show me all my tasks"
  - "Mark task #1 as complete"
  - "Delete task #2"

### API Endpoints
- `POST /api/{user_id}/chat` - Chat with the AI agent
- Standard task endpoints remain available from Phase 2

## Security Features
- JWT-based authentication
- User data isolation
- MCP tool authentication
- Rate limiting on chat endpoints
- Input validation and sanitization

## Troubleshooting

### ChatKit Domain Issues
- Ensure your domain is added to the ChatKit allowlist
- Check browser console for CORS errors
- Verify that the ChatKit domain matches your application domain

### Authentication Issues
- Verify JWT tokens are properly configured
- Check that Better Auth is properly set up
- Ensure frontend and backend URLs match

### MCP Server Connectivity
- Verify MCP server is running
- Check that backend can connect to MCP server
- Confirm authentication tokens are properly passed

### Database Issues
- Ensure database connection string is correct
- Run migrations if needed
- Verify database permissions

## API Documentation

### Chat Endpoint
`POST /api/{user_id}/chat`

Request body:
```json
{
  "conversation_id": number, // optional
  "message": "string"
}
```

Response:
```json
{
  "conversation_id": number,
  "response": "string",
  "tool_calls": []
}
```

## Environment Variables

### Backend
- `DATABASE_URL`: Database connection string
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth URL
- `NEXT_PUBLIC_BETTER_AUTH_SECRET`: Better Auth secret
- `GEMINI_API_KEY`: Gemini API key
- `MCP_SERVER_URL`: MCP server URL

### Frontend
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth URL
- `NEXT_PUBLIC_BETTER_AUTH_SECRET`: Better Auth secret
- `NEXT_PUBLIC_BACKEND_URL`: Backend API URL

## Health Checks
- `/health` - General health check
- `/ready` - Readiness check

## Contributing
See the contributing guidelines in the repository.

## License
MIT License