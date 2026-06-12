# Ticket Portal

**Ticket Portal** is a full-stack support workflow application built to practice **QA automation**, **role-based workflow validation**, and **end-to-end browser testing** across the backend, frontend, and CI pipeline. The project simulates a realistic internal ticketing system where employees submit support requests, agents investigate and progress tickets through a lifecycle, and administrators manage categories and system-level behavior.

---

## Project Goals

This project was built to strengthen skills in:

- backend API development and testing
- database validation and persistence testing
- frontend workflow implementation
- end-to-end browser automation with Playwright
- CI automation with GitHub Actions
- role-based access control and workflow validation

---

## Tech Stack

### Backend
- **FastAPI**
- **SQLAlchemy**
- **SQLite**
- **Pytest**

### Frontend
- **React**
- **Vite**
- **TypeScript**
- **React Router**

### End-to-End / Browser Testing
- **Playwright**

### CI
- **GitHub Actions**

---

## Core Features

### Authentication
- Login with JWT-based authentication
- Protected frontend routes
- Role-aware UI behavior

### User Roles
- **Employee**
  - creates tickets
  - adds public comments
  - closes resolved tickets
  - reopens resolved tickets
- **Agent**
  - reviews tickets
  - self-assigns tickets
  - adds internal comments
  - moves tickets through support workflow states
- **Admin**
  - manages categories
  - has broad workflow visibility and control

### Ticket Management
- Create tickets
- List tickets
- View ticket detail
- Role-based ticket visibility

### Comments
- Public comments visible to employees, agents, and admins
- Internal comments visible only to support/admin roles
- Role-based comment creation UI

### Assignment
- Agent self-assignment through the UI
- Backend support for assignment rules

### Workflow Transitions
Supported workflow states include:

- `new`
- `triaged`
- `in_progress`
- `waiting_for_customer`
- `resolved`
- `closed`

---

## Testing Strategy

This project uses **layered automated testing**.

### 1. API Tests
API tests validate:
- authentication rules
- role-based permissions
- ticket visibility
- category management
- comment rules
- assignment logic
- ticket workflow transitions

### 2. Database Validation Tests
DB tests validate important persistence behavior such as:
- assignment persistence
- comment internal/public flags
- workflow timestamps and lifecycle state changes

### 3. Playwright End-to-End Tests
Playwright tests validate real browser workflows such as:
- employee login and ticket creation
- employee public comment workflow
- internal comment visibility rules
- agent self-assignment
- agent/employee lifecycle actions

This structure helps keep:
- backend rules validated quickly at the API layer
- persistence behavior validated directly at the DB layer
- high-value user workflows validated in the browser

---

## Current Playwright Coverage

Current Playwright scenarios include:

- employee can log in and create a ticket
- employee can add a public comment
- agent can add an internal comment and employee cannot see it
- agent can self-assign a ticket
- agent can resolve a ticket and employee can close it
- employee can reopen a resolved ticket

---

## CI Workflows

GitHub Actions workflows currently validate:

### Backend CI
- installs backend dependencies
- runs API and DB tests

### Frontend CI
- installs frontend dependencies
- builds the frontend

### Playwright CI
- starts backend and frontend services
- seeds required data
- runs browser smoke tests

---

## Project Structure

```text
project-4-ticket-portal/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
│       ├── api/
│       └── db/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── routes/
│   │   └── types/
│   └── e2e/
│       ├── auth/
│       └── ticket/
└── .github/
    └── workflows/

```

---
## Author Notes

This project was built as a hands-on learning project to develop stronger skills in:

- QA automation
- Browser testing
- API testing 
- Test layering
- CI/CD
- Full-stack workflow validation
