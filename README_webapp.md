# SmartThread: NLP-Based Communication Assistant

This repository contains the backend (Flask) and frontend (React) for the SmartThread project.  
This README guides you through setting up the project from scratch.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup (Flask)](#backend-setup-flask)
3. [Frontend Setup (React)](#frontend-setup-react)
4. [Environment Variables](#environment-variables)
5. [Running the Project](#running-the-project)
6. [Optional: Updating Dependencies](#optional-updating-dependencies)

---

## Prerequisites

Before starting, make sure you have the following installed:

- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js 18+ and npm](https://nodejs.org/)
- [MongoDB](https://www.mongodb.com/try/download/community) (if using a local database)

---

## Backend Setup (Flask)

1. **Navigate to the backend folder:**

```bash
cd backend
```

2. **Create and activate a virtual environment:**

```bash
# Windows(cmd)
python -m venv venv
.\venv\Scripts\activate.bat
```

3. **Install dependencies:**

```bash
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt

```

## Frontend Setup (React)

1. **Navigate to the frontend folder:**

```bash
cd ../frontend
```

2. **Install dependencies:**

```bash
npm install
```

3. **Start the development server:**

```bash
npm start
```

## Environment Variables

Both backend and frontend require environment variables. Create a .env file in the backend:

```bash
# Backend .env example
OPENROUTER_API_KEY_1 = <your_openrouter_key>
GOOGLE_CLIENT_SECRET_FILE= client_secret.json
GOOGLE_REDIRECT_URI= http://localhost:8000/auth/callback
GOOGLE_SCOPES = https://www.googleapis.com/auth/gmail.readonly
FLASK_SECRET_KEY = <your_secret>
REACT_APP_FRONTEND_URL=http://localhost:3000
```

For frontend React, you can create a .env in the frontend root folder:

```bash
REACT_APP_BACKEND_URL = http://localhost:8000
```

## Running the Project

1. **Start backend:**

```bash
# Activate venv first
cd backend
.\venv\Scripts\activate.bat #On Windows(cmd)
python app.py
```

1. **Start frontend:**

```bash
# Activate venv first
cd frontend
npm start
```

## Optional: Updating Dependencies

If you add new packages to backend:

```bash
# Add new package to requirements.in
pip-compile requirements.in
pip install -r requirements.txt
```

For frontend:

```bash
npm install new-package
```
