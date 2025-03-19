# Complete Route Guide for a New User

Here's a step-by-step guide for a new user to interact with the Task Management API:

## Step 1: Create a User Account
- **Route**: `POST /api/register/`
- **Body**:
  ```json
  {
    "username": "newuser",
    "email": "user@example.com", 
    "password": "securepass123",
    "password2": "securepass123"
  }
  ```
- **Response**: Returns user details with 201 status code
- **Notes**: This endpoint doesn't require authentication

## Step 2: Obtain Access Token
- **Route**: `POST /api/token/`
- **Body**:
  ```json
  {
    "username": "newuser",
    "password": "securepass123"
  }
  ```
- **Response**:
  ```json
  {
    "access": "eyJ0eXAiOiJKV...",
    "refresh": "eyJ0eXAiOiJKV..."
  }
  ```
- **Notes**: Save both tokens; the access token expires in 1 hour

## Step 3: Create Your First Task
- **Route**: `POST /api/tasks/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...` (access token)
- **Body**:
  ```json
  {
    "title": "My First Task",
    "description": "Getting started with the Task API",
    "priority": "high",
    "status": "pending"
  }
  ```
- **Response**: Returns created task with id and timestamps

## Step 4: Get All Your Tasks
- **Route**: `GET /api/tasks/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`
- **Optional Query Parameters**:
  - Filter: `?status=pending&priority=high`
  - Pagination: `?page=1`
  - Ordering: `?ordering=-created_at`

## Step 5: Get a Single Task
- **Route**: `GET /api/tasks/{id}/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`
- **Response**: Single task details

## Step 6: Update a Task
- **Route**: `PATCH /api/tasks/{id}/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`
- **Body**:
  ```json
  {
    "status": "completed"
  }
  ```
- **Notes**: Use PATCH for partial updates, PUT for complete replacement

## Step 7: View Task Statistics
- **Route**: `GET /api/tasks/statistics/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`
- **Response**: Summary of task counts by status and priority

## Step 8: View Priority-Based Task Schedule
- **Route**: `GET /api/tasks/scheduled/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`
- **Response**: Tasks ordered by priority algorithm

## Step 9: Mark a Task as Complete
- **Route**: `POST /api/tasks/{id}/complete/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`

## Step 10: Delete a Task
- **Route**: `DELETE /api/tasks/{id}/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`

## Step 11: Refresh Access Token When Expired
- **Route**: `POST /api/token/refresh/`
- **Body**:
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV..."
  }
  ```
- **Response**: New access token

## Step 12: Clear All Completed Tasks
- **Route**: `DELETE /api/tasks/clear_completed/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`

## Step 13: Reopen a Completed Task
- **Route**: `POST /api/tasks/{id}/reopen/`
- **Headers**: `Authorization: Bearer eyJ0eXAiOiJKV...`

Each step builds on the previous one, taking you from account creation through the complete task management workflow.