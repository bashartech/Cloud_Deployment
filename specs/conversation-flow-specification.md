# Conversation Flow Specification for Todo AI Chatbot

## Overview
This document specifies the conversation flow between the user and the AI agent.

## Standard Conversation Flow

### 1. Initial Interaction
```
User: "Hi" or "Hello"
Agent: "Hello! I'm your AI task assistant. I can help you add, list, complete, delete, or update tasks. What would you like to do?"
```

### 2. Task Creation Flow
```
User: "Add a task to buy groceries"
System: [Calls add_task(user_id, "buy groceries")]
Agent: "I've created the task 'buy groceries' for you (ID: 123). Is there anything else you'd like to do?"
```

### 3. Task Listing Flow
```
User: "Show me my tasks"
System: [Calls list_tasks(user_id)]
Agent: "Here are your tasks:
1. Buy groceries - [Pending]
2. Finish report - [Pending]
3. Call mom - [Completed]
Would you like to modify any of these?"
```

### 4. Task Completion Flow
```
User: "Mark task #1 as done"
System: [Calls complete_task(user_id, 1)]
Agent: "Task 'Buy groceries' has been marked as completed. Great job!"
```

### 5. Task Deletion Flow
```
User: "Delete task #2"
System: [Calls delete_task(user_id, 2)]
Agent: "Task 'Finish report' has been deleted."
```

### 6. Task Update Flow
```
User: "Change task #1 title to 'Buy organic groceries'"
System: [Calls update_task(user_id, 1, "Buy organic groceries")]
Agent: "Task #1 has been updated to 'Buy organic groceries'."
```

## Multi-step Flows

### List Then Action
```
User: "Show me pending tasks"
System: [Calls list_tasks(user_id, status="pending")]
Agent: "Here are your pending tasks:
1. Buy groceries
2. Finish report
Which one would you like to work on?"
User: "Mark #1 as done"
System: [Calls complete_task(user_id, 1)]
Agent: "Task 'Buy groceries' has been completed!"
```

### Context Preservation
The agent maintains context within the same conversation:
- Referenced task IDs remain valid in the conversation
- Previous actions are remembered
- User's intent is preserved across turns

## Error Recovery Flows

### Invalid Task ID
```
User: "Complete task #999"
System: [Returns error from backend]
Agent: "I couldn't find a task with ID 999. Could you check the task number or ask me to list your tasks?"
```

### Ambiguous Request
```
User: "Do something"
Agent: "I'm not sure what you'd like to do. I can help you with these actions:
- Add a task
- List your tasks
- Complete a task
- Delete a task
- Update a task
What would you like to do?"
```

### Authentication Issues
```
System: [Authentication fails]
Agent: "I'm having trouble accessing your account. Please make sure you're logged in and try again."
```

## Conversation Termination
- Natural termination: "Thanks" or "Goodbye"
- Timeout: After 10 minutes of inactivity
- Explicit: "End conversation"

## State Management
- Conversations are stateless between sessions
- Each API call is independent
- Database persists conversation history
- No in-memory state is maintained between requests