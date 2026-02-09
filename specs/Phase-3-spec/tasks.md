# Implementation Tasks: Phase 3 – Todo AI Chatbot (SPEC-COMPLIANT VERSION)

## Feature Overview

This document outlines Phase 3 implementation tasks for extending the existing Todo Application with an AI chatbot using MCP tools, OpenAI Agent SDK, and ChatKit, while fully preserving Phase 2 architecture, dependencies, and behavior. All tasks align with the detailed specification in prompt.md.

⚠️ Critical Enforcement Rule
Claude Code MUST first inspect, understand, and verify Phase 2 before creating or modifying any Phase 3 code.

**Feature Name**: Todo AI Chatbot
**Branch**: 001-phase3-architecture
**Priority Order**: US1 (P1) → US2 (P2) → US3 (P3)

## Global Rules for Claude Code (MANDATORY)

❌ Do NOT recreate existing folders or files

❌ Do NOT reinstall dependencies already present

❌ Do NOT refactor Phase 2 logic

✅ Inspect existing code before every change

✅ Extend existing files where possible

✅ Create new folders/files ONLY if missing

✅ After each phase, re-verify Phase 2 functionality

---

## Phase 0: Phase 2 Verification & Architecture Understanding (BLOCKING PHASE)

**Objective**: Build a complete and accurate understanding of the Phase 2 system.

### Goal

Ensure Claude Code knows what already exists, where to extend, and what must not be touched.

### Independent Test

Claude Code can accurately explain:

- Backend folder layout and responsibilities
- Frontend Next.js structure
- Auth flow (JWT / Better Auth)
- Task CRUD APIs and contracts

### Tasks

- [x] T000 [BLOCKER] Inspect backend folder structure (routers, services, models, middleware)
- [x] T001 [BLOCKER] Inspect frontend Next.js structure (app/pages, components, hooks, services)
- [x] T002 [BLOCKER] Inspect authentication flow (JWT issuance, validation, Better Auth)
- [x] T003 [BLOCKER] Verify Phase 2 task CRUD endpoints manually
- [x] T004 [BLOCKER] Identify existing backend dependencies (DO NOT install anything)
- [x] T005 [BLOCKER] Identify existing frontend dependencies (DO NOT install anything)
- [x] T006 [BLOCKER] Identify safe extension points for chat features
- [x] T007 [BLOCKER] Identify files that will be updated vs newly created
- [x] T008 [BLOCKER] Document findings in docs/phase2-analysis.md

🚫 No further tasks may start until Phase 0 is complete

## Phase 1: Setup & MCP Foundation (EXTEND-ONLY MODE)

**Objective**: Introduce MCP server and agent integration without disturbing Phase 2.

### Goal

Stand up MCP infrastructure using your existing MCP ↔ OpenAI Agent SDK skill --> (mcp-server-tools-skill).

### Independent Test

MCP server starts and agent can register a dummy tool.

**must use this skill for basic connection with mcp server and mcp tools to backend agent created by openai agent sdk **mcp-server-tools-skill** **

### Tasks

- [x] T009 [US1] Verify whether /mcp-server/ directory already exists
- [x] T010 [US1] Create /mcp-server/ ONLY if missing
- [x] T011 [US1] Create /mcp-server/index.ts ONLY if missing
- [x] T012 [US1] Create /mcp-server/tools/ ONLY if missing
- [x] T013 [US1] Create /mcp-server/config/ ONLY if missing
- [x] T014 [US1] Inspect existing environment variable handling
- [x] T015 [US1] Add MCP-related env vars ONLY if missing
- [x] T016 [US1] Verify existing OpenAI agent SDK usage
- [x] T017 [US1] Reuse existing MCP ↔ OpenAI Agent SDK connection logic
- [x] T018 [US1] Register agent with MCP using known working pattern
- [x] T019 [US1] Validate agent startup without task tools

## Phase 2: Chat Data Model Extension (SAFE DB EXTENSION)

**Objective**: Add chat persistence without altering Phase 2 tables.

### Goal

Persist conversations and messages scoped to authenticated users.

### Independent Test

Chat tables exist; Phase 2 task tables remain unchanged.

### Tasks

- [x] T020 [US1] Inspect existing database models directory
- [x] T021 [US1] Create Conversation model ONLY if missing with fields: user_id, id, created_at, updated_at
- [x] T022 [US1] Create ChatMessage model ONLY if missing with fields: user_id, id, conversation_id, role (user/assistant), content, created_at
- [x] T023 [US1] Link chat models to existing User model with proper foreign keys
- [x] T024 [US1] Inspect existing migration system
- [x] T025 [US1] Create migration for conversations table ONLY with correct schema
- [x] T026 [US1] Create migration for chat_messages table ONLY with correct schema
- [x] T027 [US1] Verify migrations do NOT modify Phase 2 tables
- [x] T028 [US1] Create conversation DB utility functions ensuring updated_at changes correctly
- [x] T029 [US1] Create message DB utility functions ensuring role validation (user/assistant only)
- [x] T030 [US1] Test DB CRUD operations for chat models ensuring proper user isolation

## Phase 3: US1 – AI Chat for Task Management (CORE FEATURE)

**User Story**
As a user, I can manage my tasks using natural language via AI.

**Critical Constraint**

MCP tools MUST call existing Phase 2 task APIs — never duplicate logic.


### MCP Tooling (Task Operations) - EXACT SPEC COMPLIANCE

- [x] T031 [US1] Inspect existing task API contracts to ensure MCP tools match spec exactly
- [x] T032 [US1] Implement add_task MCP tool with EXACT spec: {user_id (string, required), title (string, required), description (string, optional)} → {"task_id": 5, "status": "created", "title": "Buy groceries"}
- [x] T033 [US1] Implement list_tasks MCP tool with EXACT spec: {user_id (string, required), status (string, optional: "all", "pending", "completed")} → Array of task objects
- [x] T034 [US1] Implement complete_task MCP tool with EXACT spec: {user_id (string, required), task_id (integer, required)} → {"task_id": 3, "status": "completed", "title": "Call mom"}
- [x] T035 [US1] Implement delete_task MCP tool with EXACT spec: {user_id (string, required), task_id (integer, required)} → {"task_id": 2, "status": "deleted", "title": "Old task"}
- [x] T036 [US1] Implement update_task MCP tool with EXACT spec: {user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional)} → {"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}
- [x] T037 [US1] Attach JWT to MCP → backend calls ensuring user_id validation
- [x] T038 [US1] Validate MCP tool input schemas match spec exactly
- [x] T039 [US1] Test MCP tools independently with spec examples
- [x] T040 [US1] Verify MCP tools are STATELESS (no memory/cache held between calls)

### Backend Chat Orchestration - EXACT API CONTRACT

- [x] T041 [US1] Inspect existing backend router patterns
- [x] T042 [US1] Create EXACT endpoint: POST /api/{user_id}/chat with spec-defined request/response
- [x] T043 [US1] Implement request body validation: {"conversation_id": number?, "message": string}
- [x] T044 [US1] Implement response body validation: {"conversation_id": number, "response": string, "tool_calls": []}
- [x] T045 [US1] Implement chat orchestration service ensuring stateless server (no memory held)
- [x] T046 [US1] Implement fetch conversation history from database (step 2 in spec flow)
- [x] T047 [US1] Implement build message array for agent (history + new message) (step 3 in spec flow)
- [x] T048 [US1] Implement store user message in database (step 4 in spec flow)
- [x] T049 [US1] Implement run agent with MCP tools (step 5 in spec flow)
- [x] T050 [US1] Implement store assistant response in database (step 7 in spec flow)
- [x] T051 [US1] Implement return response to client (step 8 in spec flow)
- [x] T052 [US1] Verify server holds NO state (ready for next request) (step 9 in spec flow)
- [x] T053 [US1] Test statelessness: server restart → conversation continues functionality
- [x] T054 [US1] Implement tool_calls array in response as required by spec

### Agent Behavior Specification

- [x] T055 [US1] Configure agent for task creation behavior: when user mentions adding/creating/remembering, use add_task
- [x] T056 [US1] Configure agent for task listing behavior: when user asks to see/show/list, use list_tasks with appropriate filter
- [x] T057 [US1] Configure agent for task completion behavior: when user says done/complete/finished, use complete_task
- [x] T058 [US1] Configure agent for task deletion behavior: when user says delete/remove/cancel, use delete_task
- [x] T059 [US1] Configure agent for task update behavior: when user says change/update/rename, use update_task
- [x] T060 [US1] Configure agent for confirmation behavior: always confirm actions with friendly response
- [x] T061 [US1] Configure agent for error handling: gracefully handle task not found and other errors
- [x] T062 [US1] Verify agent can handle natural language examples from spec: "Add a task to buy groceries", "Show me all my tasks", etc.
- [x] T063 [US1] Implement agent behavior for tool chaining when needed (e.g., list then delete)

### Frontend Chat UI (EXTEND EXISTING NEXT.JS)

- [x] T064 [US1] Inspect existing auth hooks
- [x] T065 [US1] Inspect existing API service layer
- [x] T066 [US1] Create ChatProvider component with ChatKit domain key configuration
- [x] T067 [US1] Create ChatWindow component
- [x] T068 [US1] Create MessageList component
- [x] T069 [US1] Create MessageInput component
- [x] T070 [US1] Implement loading/error states
- [x] T071 [US1] Reuse existing JWT/auth state
- [x] T072 [US1] Connect frontend to EXACT API: POST /api/{user_id}/chat
- [x] T073 [US1] Verify end-to-end chat flow with correct request/response format
- [x] T074 [US1] Test ChatKit domain allowlist configuration and failure handling

## Phase 4: US2 – Secure & Isolated Conversations

**Objective**: Enforce strict user isolation.

### Tasks

- [x] T075 [US2] Verify JWT validation middleware
- [x] T076 [US2] Enforce user_id scoping in DB queries
- [x] T077 [US2] Prevent cross-user conversation access
- [x] T078 [US2] Enforce auth in MCP middleware
- [x] T079 [US2] Handle JWT expiry during active chat
- [x] T080 [US2] Test multi-user isolation scenarios

## Phase 5: US3 – Phase 2 Regression Protection

**Objective**: Guarantee Phase 2 still works.

### Tasks

- [x] T081 [US3] Re-test Phase 2 task APIs
- [x] T082 [US3] Re-test Phase 2 UI task flows
- [x] T083 [US3] Verify tasks created via chat appear in UI
- [x] T084 [US3] Verify tasks created via UI appear in chat
- [x] T085 [US3] Fix any detected regressions
- [x] T086 [US3] Document compatibility notes

## Phase 6: Specs & Documentation (SPEC DELIVERABLES)

**Objective**: Create specification files for agent and MCP tools as required.

### Tasks

- [x] T087 Create /specs folder for agent and MCP tool specifications
- [x] T088 Create agent specification file documenting behavior rules
- [x] T089 Create MCP tool specification file documenting exact contracts
- [x] T090 Document natural language command mappings to tool calls
- [x] T091 Document conversation flow specification
- [x] T092 Document error handling specifications

## Phase 7: Polish, Stability & Final Validation

### Tasks

- [x] T093 Add structured logging (no sensitive data)
- [x] T094 Add rate limiting for chat endpoints
- [x] T095 Add retry logic for MCP → backend calls
- [x] T096 Add health checks for backend & MCP
- [x] T097 Add graceful shutdown for MCP server
- [x] T098 Add input validation schemas
- [x] T099 Add security audit logging
- [x] T100 Write MCP tool contracts documentation
- [x] T101 Write chat API documentation
- [x] T102 Update README with Phase 3 instructions including ChatKit domain setup
- [x] T103 Write troubleshooting guide for ChatKit domain issues
- [x] T104 Perform load testing on chat endpoints
- [x] T105 Perform security checklist review
- [x] T106 Final end-to-end test (UI → Agent → MCP → Backend → DB) with spec compliance
- [x] T107 Final Phase 2 regression verification
- [x] T108 Verify all MCP tools return exact spec-compliant responses
- [x] T109 Verify tool_calls array is included in API responses
- [x] T110 Verify stateless architecture compliance across all components

## Final Summary

**Total Tasks**: 110 (Spec-Compliant, Detailed, Non-Skipping)
**Completed Tasks**: 110/110
**Execution Model**: Inspect → Extend → Validate → Re-test
**Claude Code Risk Level**: MINIMIZED
**Spec Compliance**: 100% (Addresses all gaps from requirements analysis)
**Status**: COMPLETE - All Phase 3 features implemented successfully