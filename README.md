# Kanban Board API (Core)

A professional, robust Backend API for a Kanban Task Management System, engineered with **Django** and **Django REST Framework (DRF)**. This system enables teams to collaborate on projects, track task progress, and discuss requirements in a secure, permission-controlled environment.

## 🌟 Key Features

*   **User Authentication**: Secure registration and login system using Token-based authentication.
*   **Board Management**: Create personal or team boards. Owners can invite members to collaborate.
*   **Dynamic Task Tracking**: Comprehensive Task CRUD with statuses (`To Do`, `In Progress`, `Review`, `Done`) and priority levels (`Low`, `Medium`, `High`).
*   **Task Assignment**: Assign tasks to team members and designate reviewers for quality control.
*   **Real-time Discussions**: Commenting system for every task to keep the team aligned.
*   **Advanced Permissions**: Granular access control ensuring only authorized members can view, edit, or delete resources.
*   **Admin Interface**: Fully configured Django Admin for high-level data management.

---

## 📁 Project Structure & Conventions

Following the project's **Definition of Done (DoD)**, the architecture is modular and strictly follows clean code principles:

*   **Core Naming**: Central project configuration resides in the `core/` directory.
*   **Modular Design**: Logic is strictly separated into `auth_app` (Identity) and `kanban_app` (Business Logic).
*   **API Encapsulation**: All serializers, views, and routes are encapsulated in `api/` sub-packages.
*   **Clean Code Standards**:
    *   Methods are limited to **max. 14 lines** for maintainability.
    *   Full **PEP8** compliance with optimized and grouped imports.
    *   Detailed **Docstrings** for all modules and classes.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   pip (Python package manager)
*   Virtualenv

### Installation & Setup

1.  **Clone and Navigate**:
    ```bash
    git clone <your-repository-url>
    cd <project-folder>
    ```

2.  **Environment Setup**:
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables & Security**:
    Create a `.env` file in the root directory. You **must** generate and add a `SECRET_KEY` for the application to work:
    ```env
    SECRET_KEY=your_generated_secret_key_here
    DEBUG=True
    ```
    *(Note: Use a tool like `django.core.management.utils.get_random_secret_key()` to generate a secure key.)*

5.  **Database & Migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Run Server**:
    ```bash
    python manage.py runserver
    ```
    The API is now live at: **http://127.0.0.1**

---

## 📡 API Endpoints

All endpoints (except registration/login) require: `Authorization: Token <your-token>`

### Authentication


| Method | Endpoint             | Description                           |
| :----- | :------------------- | :------------------------------------ |
| POST   | `/api/registration/` | Register a new user account           |
| POST   | `/api/login/`        | Login and receive auth token          |
| GET    | `/api/email-check/`  | Verify if an email is already in use  |

### Boards


| Method | Endpoint                  | Description                               |
| :----- | :------------------------ | :---------------------------------------- |
| GET    | `/api/boards/`            | List all boards for the current user      |
| POST   | `/api/boards/`            | Create a new board instance               |
| GET    | `/api/boards/{id}/`       | Retrieve detailed board information       |
| PATCH  | `/api/boards/{id}/`       | Update board members or title             |
| DELETE | `/api/boards/{id}/`       | Permanently delete a board (Owner only)   |

### Tasks


| Method | Endpoint                    | Description                                |
| :----- | :-------------------------- | :----------------------------------------- |
| GET    | `/api/tasks/assigned-to-me/`| List tasks assigned to you                 |
| GET    | `/api/tasks/reviewing/`     | List tasks where you are the reviewer      |
| POST   | `/api/tasks/`               | Create a new task within a board           |
| PATCH  | `/api/tasks/{id}/`          | Update task details, status, or assignee   |
| DELETE | `/api/tasks/{id}/`          | Delete task (Author or Board Owner only)   |

### Comments


| Method | Endpoint                                 | Description                        |
| :----- | :--------------------------------------- | :--------------------------------- |
| GET    | `/api/tasks/{id}/comments/`              | List all comments for a task       |
| POST   | `/api/tasks/{id}/comments/`              | Add a new comment to a task        |
| DELETE | `/api/tasks/{id}/comments/{comment_id}/` | Delete a comment (Author only)     |

---

## 🛡 Security & Status Codes

The API strictly follows the documented HTTP status code conventions:
*   **201 Created**: Resource successfully generated.
*   **204 No Content**: Resource successfully deleted.
*   **400 Bad Request**: Invalid input data or logic error (e.g., ID mismatch).
*   **401 Unauthorized**: Authentication token missing or invalid.
*   **403 Forbidden**: User lacks permission for the specific resource.
*   **404 Not Found**: Target resource does not exist.

---
*Note: Sensitive files like `db.sqlite3` and `.env` are excluded from version control to ensure security.*
