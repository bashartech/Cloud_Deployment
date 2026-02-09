---
name: Responsive Todo UI Rendering & Interaction
description: Implements a fully responsive, authenticated, task-management UI that allows users to interact with all Todo features visually, synchronized with the secured REST API
version: 1.0.0
---

# Responsive Todo UI Rendering & Interaction

## Skill Type
Frontend UI Implementation

## Applicable Phase
Project 2 – Phase II (Full-Stack Web Application)

## Purpose
To implement a **fully responsive, authenticated, task-management UI** that allows users to interact with all Todo features visually, synchronized with the secured REST API.

This skill ensures Project 2 meets the explicit requirement:
"Build responsive frontend interface".

---

## Responsibilities

1. **Authenticated UI Layout**
   - Render UI only for authenticated users
   - Redirect unauthenticated users to login
   - Display user-specific data only

2. **Task List Rendering**
   - Display tasks fetched from backend
   - Show title, completion status, timestamps
   - Visually distinguish completed vs pending

3. **Task CRUD Interactions**
   - Create task via form
   - Edit task title/description
   - Delete task with confirmation
   - Toggle completion state

4. **Filtering & Sorting UI**
   - Filter by: all / pending / completed
   - Sort by: created / title
   - Sync UI state with API query params

5. **Responsive Design**
   - Mobile-first layout
   - Desktop-friendly layout
   - Consistent UX across screen sizes

6. **State Synchronization**
   - Optimistic UI updates where safe
   - Re-fetch on mutation failure
   - Error states surfaced to user

---

## Implementation Rules

- Do NOT render tasks without auth
- Do NOT store state outside React lifecycle
- Do NOT bypass API client
- Do NOT expose other users' data

---

## Outputs

- Fully interactive Todo UI
- Secure, user-scoped rendering
- Responsive layout

---

## Acceptance Criteria

- All CRUD actions available via UI
- UI reflects backend state accurately
- Works on mobile and desktop

---

## Enforcement Priority
HIGH