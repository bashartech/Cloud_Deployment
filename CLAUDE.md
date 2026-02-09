# Claude Code Operating Guide (Phase 3 – Todo AI Chatbot)

## 1. Purpose of This File

This file defines **how Claude Code must behave when working on this repository**.
It is a **governance and execution guide**, not an implementation document.

The goal is to ensure:

* Spec-driven development (SDD)
* Zero accidental rewrites of Phase 2
* Accurate, verifiable, and incremental implementation
* Predictable results with minimal hallucination

Claude Code must treat this file as **mandatory instructions**.

---

## 2. Project Context (Authoritative)

This repository contains a **multi-phase Hackathon II project**.

### Current Phase

* **Phase 3: Todo AI Chatbot**

### Completed Phase

* **Phase 2: Full-stack Todo Application** (already implemented and stable)

Phase 3 **extends Phase 2**. Nothing in Phase 2 should be rewritten unless a spec explicitly requires it.

---

## 3. Technology Stack (Locked)

Claude Code must assume and reuse the following stack:

### Frontend

* Next.js
* Tailwind CSS
* OpenAI ChatKit

### Backend

* FastAPI (Python)
* OpenAI Agents SDK
* Official MCP SDK

### Authentication

* Better Auth
* JWT (unchanged from Phase 2)

### Database

* Neon Serverless PostgreSQL
* SQLModel ORM

❌ No alternative frameworks or databases are allowed unless explicitly specified.

---

## 4. Spec-Driven Development Rules (Mandatory)

Claude Code **must not implement anything** unless:

1. A specification file exists in `/specs`
2. The spec is explicitly referenced
3. The scope of change is clearly defined

### Required Execution Order

1. Read `/sp.constitution`
2. Read the relevant spec(s)
3. Inspect the existing file & folder structure
4. Identify reuse points from Phase 2
5. Produce a short implementation plan
6. Implement the smallest possible change
7. Validate correctness

Skipping any step is **not allowed**.

---

## 5. File System Inspection Rule

Before writing or modifying code, Claude Code must:

* List relevant directories and files
* Identify existing services, models, and APIs
* Confirm whether logic already exists

Claude Code must **prefer reuse over creation**.

---

## 6. Database Safety Rules

* The existing `Task` SQLModel from Phase 2 must be reused
* No duplicate task tables or models may be created
* New tables allowed only:

  * `Conversation`
  * `Message`

All DB access must use:

* Existing `DATABASE_URL`
* SQLModel sessions

---

## 7. Authentication & Security Rules

* JWT verification happens in FastAPI only
* `user_id` must come from verified JWT
* MCP tools must never trust frontend-provided user IDs
* All task queries must be scoped by `user_id`

Security parity with Phase 2 must be maintained.

---

## 8. MCP Server Constraints

Claude Code must respect that MCP:

* Is stateless
* Does not manage authentication
* Does not store conversation history
* Accesses **only task-related tables**

MCP tools must call shared task services where possible.

---

## 9. AI Agent Constraints

Claude Code must ensure that the AI agent:

* Has no direct database access
* Uses MCP tools exclusively for task operations
* Follows behavior defined in `/specs/agent.md`
* Returns friendly confirmations and errors

---

## 10. Error Handling Expectations

Claude Code must:

* Handle task-not-found cases gracefully
* Return structured errors from MCP tools
* Avoid throwing unhandled exceptions

User-facing errors must be helpful and human-readable.

---

## 11. Validation & Verification

After each implementation:

* Confirm spec compliance
* Confirm no Phase 2 regression
* Confirm stateless behavior
* Confirm user isolation

If any uncertainty exists, Claude Code must **stop and ask for clarification via spec**, not guess.

---

## 12. Prohibited Behaviors

Claude Code must NOT:

* Rewrite existing working code unnecessarily
* Introduce new frameworks or libraries
* Store state in memory between requests
* Combine chat logic with MCP tools
* Modify Phase 2 logic without a spec

---

## 13. Authority Hierarchy

When conflicts arise, Claude Code must follow this order:

1. `/sp.constitution`
2. `/specs/*.md`
3. This `claude.md`
4. Existing codebase

---

## 14. Final Rule

Claude Code exists to **execute specifications**, not to redesign the system.

Accuracy, safety, and spec compliance are more important than speed.
