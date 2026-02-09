# Natural Language Command Mappings for Todo AI Chatbot

## Overview
This document maps natural language phrases to their corresponding MCP tool calls.

## Command Categories

### Task Creation Commands
| Natural Language Examples | MCP Tool | Parameters |
|---------------------------|----------|------------|
| "Add a task to buy groceries" | add_task | user_id, title="buy groceries" |
| "Create a task called 'Finish report'" | add_task | user_id, title="Finish report" |
| "Remember to call mom tomorrow" | add_task | user_id, title="call mom tomorrow" |
| "I need to do laundry" | add_task | user_id, title="do laundry" |

### Task Listing Commands
| Natural Language Examples | MCP Tool | Parameters |
|---------------------------|----------|------------|
| "Show me my tasks" | list_tasks | user_id, status="all" |
| "What tasks do I have?" | list_tasks | user_id, status="all" |
| "Show pending tasks" | list_tasks | user_id, status="pending" |
| "List completed tasks" | list_tasks | user_id, status="completed" |
| "Show all my tasks" | list_tasks | user_id, status="all" |

### Task Completion Commands
| Natural Language Examples | MCP Tool | Parameters |
|---------------------------|----------|------------|
| "Mark task #1 as done" | complete_task | user_id, task_id=1 |
| "Complete task 'Buy groceries'" | complete_task | user_id, task_id=lookup("Buy groceries") |
| "Finish task #3" | complete_task | user_id, task_id=3 |
| "Task #5 is done" | complete_task | user_id, task_id=5 |
| "I completed the meeting prep" | complete_task | user_id, task_id=lookup("meeting prep") |

### Task Deletion Commands
| Natural Language Examples | MCP Tool | Parameters |
|---------------------------|----------|------------|
| "Delete task #2" | delete_task | user_id, task_id=2 |
| "Remove the appointment task" | delete_task | user_id, task_id=lookup("appointment") |
| "Cancel task 'Call dentist'" | delete_task | user_id, task_id=lookup("Call dentist") |
| "Get rid of task #7" | delete_task | user_id, task_id=7 |
| "Remove completed tasks" | delete_task | user_id, task_id=lookup(completed tasks) |

### Task Update Commands
| Natural Language Examples | MCP Tool | Parameters |
|---------------------------|----------|------------|
| "Change task #1 title to 'Updated title'" | update_task | user_id, task_id=1, title="Updated title" |
| "Update task 'Old title' to 'New title'" | update_task | user_id, task_id=lookup("Old title"), title="New title" |
| "Modify the description of task #4" | update_task | user_id, task_id=4, description="new description" |
| "Rename task #6 to 'Pay bills'" | update_task | user_id, task_id=6, title="Pay bills" |

## Special Commands

### Confirmation Responses
- "Yes", "Confirm", "Okay", "Sure" → Confirms pending operations
- "No", "Cancel", "Never mind" → Cancels pending operations

### Contextual Commands
- "Repeat that" → Repeats last response
- "What did you say?" → Repeats last response
- "Explain again" → Provides detailed explanation

## Fuzzy Matching
The system uses fuzzy matching for:
- Task titles when exact ID is not provided
- Synonyms for command verbs
- Natural language parsing for dates and times

## Error Handling
- "I don't understand" → Prompts for clarification
- "Can you repeat that?" → Asks user to rephrase
- "Could you be more specific?" → Requests specific details