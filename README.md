# Kanban Board API (Core)

This is a robust Backend API for a Kanban Task Management System, built with **Django** and **Django REST Framework (DRF)**. The project provides comprehensive features for user authentication, board organization, task tracking, and team discussions.

## 🚀 Getting Started

To get the project running locally, follow these steps:

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtualenv (recommended)

### Installation & Setup

1. **Clone the repository:**
```bash
git clone <your-repository-url>
cd <project-folder>
```

2. **Set up a virtual environment:**
```bash
python -m venv venv
# Activate on Windows:
.\venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Environment Variables:**
Create a .env file in the root directory and add your SECRET_KEY:
```bash
SECRET_KEY=your_secure_django_secret_key
```

5. **Database Initialization:**
```bash
python manage.py migrate
```

6. **Start the Development Server:**
```bash
python manage.py runserver
```

The API is now available at http://127.0.0.1:8000/

### 🛠 Project Structure & Conventions
- Core Naming: The main project configuration is located in the core/ directory.
- Modular Design: Features are separated into auth_app and kanban_app.
- API Encapsulation: Following the project requirements, all API logic (serializers, views, urls, permissions) is strictly contained within api/ sub-packages of each app.
- Clean Code (DoD):
    - Methods are kept under 14 lines of code for better maintainability.
    - Full PEP8 compliance with grouped and sorted imports.
    - Comprehensive Docstrings for all modules, classes, and methods.

### 🛡 Security & Permissions
Access control is strictly enforced based on user roles:
- Board Permissions: Only the owner can delete a board. Members can view and update.
- Task Permissions: Only the task author or the board owner can permanently delete a task.
- Comment Permissions: Only the original author of a comment is allowed to delete it.
- Authentication: All sensitive endpoints require a valid TokenAuthentication header.

### 📡 API Status Codes & Responses
The API is fully aligned with the official documentation and provides specific localized error messages:
- 201 Created: Successful resource creation.
- 204 No Content: Successful deletion.
- 400 Bad Request: Invalid data format or failed business logic (e.g., mismatched IDs).
- 403 Forbidden: Permission denied (e.g., non-member trying to access a private board).
- 404 Not Found: Resource (Board/Task/Comment) does not exist.

### 🗄 Administration
The Django Admin interface is fully configured and usable. You can manage users, boards, tasks, and comments at /admin/.

Note: The db.sqlite3 database and .env files are excluded from version control to ensure security and a clean deployment environment.
