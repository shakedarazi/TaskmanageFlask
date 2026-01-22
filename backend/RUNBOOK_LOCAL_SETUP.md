# Voltify Task Manager — Local Setup Runbook

> **One file to rule them all.**  
> Follow this guide step-by-step from a fresh clone to a running API on `localhost:5000`.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Prerequisites](#2-prerequisites)
3. [Repository Structure](#3-repository-structure)
4. [Python Local Environment (venv)](#4-python-local-environment-venv)
5. [Git Ignore Rules](#5-git-ignore-rules)
6. [Environment Variables Setup](#6-environment-variables-setup)
7. [Running with Docker (Primary Path)](#7-running-with-docker-primary-path)
8. [Running WITHOUT Docker (Local Flask)](#8-running-without-docker-local-flask)
9. [Verification Steps](#9-verification-steps)
10. [Common Failure Modes](#10-common-failure-modes)
11. [From Zero to Live — Summary Checklist](#11-from-zero-to-live--summary-checklist)

---

## 1. Project Overview

**What is this?**  
Voltify Task Manager is a Flask-based REST API for task management with AI-powered features. It uses MongoDB as its database and is fully containerized with Docker.

**Tech Stack:**
- **Backend:** Flask 3.x (Python 3.10)
- **Database:** MongoDB 5
- **Orchestration:** Docker Compose
- **Features:** User auth, task CRUD, AI assistance, Telegram notifications

**When to use this runbook:**
- First-time setup on a new machine
- Onboarding a new teammate
- Rebuilding a broken local environment
- Reference for Docker and Flask commands

---

## 2. Prerequisites

### Required Software

| Tool | Version | Verify Command |
|------|---------|----------------|
| Docker Desktop | Latest | `docker --version` |
| Docker Compose | v2.x (included in Docker Desktop) | `docker compose version` |
| Python | 3.10.x (must match Dockerfile) | `python --version` |
| Git | Any recent version | `git --version` |

### OS-Specific Notes

**Windows (Primary):**
- Use PowerShell or Windows Terminal
- Docker Desktop must be running (check system tray)
- WSL2 backend recommended for Docker Desktop

**macOS:**
- Use Terminal or iTerm2
- Docker Desktop must be running (check menu bar)
- Use `python3` instead of `python`

**Linux:**
- Install Docker Engine + Docker Compose plugin
- May need `sudo` for Docker commands (or add user to `docker` group)
- Use `python3` instead of `python`

---

## 3. Repository Structure

```
TaskmanageFlask/
├── backend/                    ← ALL COMMANDS RUN FROM HERE
│   ├── docker-compose.yml      # Docker orchestration
│   ├── Dockerfile              # Flask container build
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   ├── .env                    # Your local secrets (gitignored)
│   ├── .dockerignore           # Files excluded from Docker build
│   ├── .gitignore              # Files excluded from Git
│   ├── app.py                  # Flask entrypoint
│   ├── db.py                   # MongoDB connection
│   ├── auth_routes.py          # Authentication endpoints
│   ├── task_routes.py          # Task CRUD endpoints
│   ├── ai_routes.py            # AI feature endpoints
│   └── logic/                  # Business logic modules
└── frontend/                   # Static frontend (separate)
```

> **⚠️ Important:** All commands in this runbook assume you are in the `backend/` directory unless otherwise noted.

---

## 4. Python Local Environment (venv)

### Why Do I Need a venv?

Even though the app runs in Docker, a local virtual environment is essential for:

- **IDE Support:** Autocomplete, linting, type hints
- **Local Debugging:** Run Flask outside Docker for faster iteration
- **Script Execution:** Run one-off Python scripts
- **Dependency Inspection:** Check installed package versions

### Where to Create It

Create the venv inside the `backend/` directory. The folder will be named `.venv/`.

### How to Create and Activate

#### Windows (PowerShell)!!!!!!

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
py -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Upgrade pip (recommended)
py -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

> **Note:** If you get an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### Windows (CMD)

```cmd
cd backend
py -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS / Linux

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

### How to Deactivate

```bash
deactivate
```

### How to Verify Activation

When activated, your prompt shows `(.venv)`:

```
(.venv) PS C:\Users\shaked arazi\Desktop\Projects\TaskmanageFlask\backend>
```

Verify Python path:

```bash
# Windows
where python

# macOS/Linux
which python
```

Should point to `.venv/Scripts/python` or `.venv/bin/python`.

---

## 5. Git Ignore Rules

### Critical: Do NOT Commit These

The following must **never** be committed to version control:

| File/Folder | Reason |
|-------------|--------|
| `.venv/` | Local Python environment (large, machine-specific) |
| `.env` | Contains secrets (API keys, SECRET_KEY) |
| `__pycache__/` | Python bytecode cache |
| `*.log` | Log files |

### Verify .gitignore Contains These Lines

Open `backend/.gitignore` and ensure it includes:

```gitignore
# Virtual environment
.venv/
venv/
ENV/

# Environment variables
.env
.env.local
.env.*.local

# Python cache
__pycache__/
*.py[cod]

# Logs
*.log
voltify.log
```

### If `.venv/` Is Missing from .gitignore

Add it manually:

```bash
echo ".venv/" >> .gitignore
```

---

## 6. Environment Variables Setup

### Overview

The application requires environment variables for:

| Variable | Purpose |
|----------|---------|
| `MONGO_URI` | MongoDB connection string |
| `SECRET_KEY` | Flask session signing key |
| `OPENAI_API_KEY` | OpenAI API access |
| `TELEGRAM_BOT_TOKEN` | Telegram notifications (optional) |
| `FLASK_ENV` | Environment mode (development/production) |

### Step 1: Create .env from Template

```powershell
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### Step 2: Understand Key Variables

**MONGO_URI**
```
MONGO_URI=mongodb://mongo:27017/task_management_db
```
- `mongo` is the Docker service name (not `localhost`)
- `27017` is MongoDB's default port
- `task_management_db` is the database name (auto-created)

**SECRET_KEY**
```
SECRET_KEY=<random-64-character-hex-string>
```
- Used by Flask to sign session cookies
- Must be random and unpredictable
- Must **never** be committed to Git

### Step 3: Generate a Secure SECRET_KEY

#### Option A: Using Python

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Option B: Using OpenSSL (if available)

```bash
openssl rand -hex 32
```

Copy the output and paste it as the `SECRET_KEY` value in `.env`.

### Step 4: Complete Your .env File

Edit `.env` with your actual values:

```env
MONGO_URI=mongodb://mongo:27017/task_management_db
SECRET_KEY=paste_your_generated_key_here
OPENAI_API_KEY=sk-your-actual-openai-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
FLASK_ENV=development
```

### Where .env Must Live

```
backend/
├── .env          ← HERE (same level as docker-compose.yml)
├── .env.example
├── docker-compose.yml
└── ...
```

Docker Compose automatically reads `.env` from the same directory.

---

## 7. Running with Docker (Primary Path)

This is the **recommended** way to run the application.

### Step 1: Navigate to Backend

```powershell
cd backend
```

### Step 2: Create Environment File

```powershell
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` with your values (see Section 6).

### Step 3: Build and Start Services

```powershell
docker compose up --build
```

This will:
1. Build the Flask container image
2. Pull MongoDB 5 image (first time only)
3. Create the network `shaked_taskmgmt_network`
4. Create the volume `shaked_taskmgmt_mongo_data`
5. Start both containers
6. Stream logs to your terminal

### Step 4: Run in Background (Detached)

```powershell
docker compose up -d --build
```

### Step 5: Check Service Status

```powershell
docker compose ps
```

Expected output:
```
NAME                     SERVICE   STATUS    PORTS
shaked_taskmgmt_api      api       running   0.0.0.0:5000->5000/tcp
shaked_taskmgmt_mongo    mongo     running   27017/tcp
```

### Step 6: View Logs

```powershell
# All services
docker compose logs -f

# API only
docker compose logs -f api

# Last 50 lines
docker compose logs --tail=50 api
```

### Step 7: Stop Services

```powershell
# Stop containers (preserves data)
docker compose down

# Stop and DELETE all data
docker compose down -v
```

---

## 8. Running WITHOUT Docker (Local Flask)

### When to Use This

- Faster iteration during development
- Debugging with IDE breakpoints
- When Docker is unavailable or slow

### Prerequisites

1. **MongoDB must be running** — Start only the database via Docker:
   ```powershell
   docker compose up -d mongo
   ```

2. **Virtual environment must be activated** — See Section 4

3. **Environment variables must be set**

### Option A: Load from .env (Recommended)

The app uses `python-dotenv` which auto-loads `.env`. Just run:

```powershell
flask run --host=0.0.0.0 --port=5000
```

### Option B: Export Variables Manually

#### Windows (PowerShell)

```powershell
$env:MONGO_URI="mongodb://localhost:27017/task_management_db"
$env:SECRET_KEY="your-secret-key-here"
$env:FLASK_ENV="development"
flask run --host=0.0.0.0 --port=5000
```

> **Note:** When running locally (not in Docker), use `localhost` instead of `mongo` for MONGO_URI.

#### macOS/Linux

```bash
export MONGO_URI="mongodb://localhost:27017/task_management_db"
export SECRET_KEY="your-secret-key-here"
export FLASK_ENV="development"
flask run --host=0.0.0.0 --port=5000
```

### Expose MongoDB Port for Local Development

If you need to connect to MongoDB from your host machine, uncomment the ports in `docker-compose.yml`:

```yaml
mongo:
  image: mongo:5
  ports:
    - "27017:27017"  # Uncomment this line
```

Then restart: `docker compose up -d mongo`

---

## 9. Verification Steps

### 9.1 Test API Endpoint

```powershell
curl http://localhost:5000/
```

**Expected Response:**
```json
{"message":"Voltify Task Manager API"}
```

If `curl` is not available on Windows:

```powershell
Invoke-RestMethod -Uri http://localhost:5000/
```

### 9.2 Check Container Health

```powershell
docker compose ps
```

Both services should show `STATUS: running` (or `healthy` if healthchecks have passed).

### 9.3 Test MongoDB Connection

```powershell
docker exec shaked_taskmgmt_mongo mongo --eval "db.adminCommand('ping')"
```

**Expected Output:**
```
{ "ok" : 1 }
```

### 9.4 Verify Environment Variables in Container

```powershell
docker exec shaked_taskmgmt_api python -c "import os; print('MONGO_URI:', os.getenv('MONGO_URI')); print('SECRET_KEY set:', bool(os.getenv('SECRET_KEY')))"
```

**Expected Output:**
```
MONGO_URI: mongodb://mongo:27017/task_management_db
SECRET_KEY set: True
```

### 9.5 Verify Volume Exists

```powershell
docker volume ls | findstr shaked_taskmgmt
```

**Expected Output:**
```
local     shaked_taskmgmt_mongo_data
```

---

## 10. Common Failure Modes

### ❌ Port 5000 Already in Use

**Symptom:**
```
Error starting userland proxy: Bind for 0.0.0.0:5000 failed: port is already allocated
```

**Fix:**

```powershell
# Find the process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual PID)
taskkill /PID <PID> /F

# Or change the port in docker-compose.yml:
# ports:
#   - "5001:5000"
```

---

### ❌ MongoDB Connection Error

**Symptom:**
```
pymongo.errors.ServerSelectionTimeoutError: mongo:27017
```

**Causes & Fixes:**

| Check | Command | Fix |
|-------|---------|-----|
| Is Mongo running? | `docker compose ps` | `docker compose up -d mongo` |
| Using wrong host? | Check `.env` | Use `mongo` (Docker) or `localhost` (local) |
| Network issue? | `docker network ls` | Recreate: `docker compose down && docker compose up -d` |

---

### ❌ SECRET_KEY Missing

**Symptom:**
```
TypeError: 'NoneType' object...
# or session/cookie errors
```

**Fixes:**

1. Ensure `.env` file exists in `backend/`
2. Ensure `SECRET_KEY=<value>` is set (not empty)
3. Rebuild container: `docker compose up -d --build`

---

### ❌ venv Not Activated

**Symptom:**
- `pip install` installs globally
- Wrong Python version
- ModuleNotFoundError when running Flask

**Fix:**

```powershell
# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Verify with:
```powershell
where python   # Should show .venv path
```

---

### ❌ pip Installed Globally by Mistake

**Symptom:**
- Packages installed in system Python
- Conflicts with other projects

**Fix:**

1. Deactivate any venv: `deactivate`
2. Delete global packages (optional, be careful)
3. Recreate venv:
   ```powershell
   Remove-Item -Recurse -Force .venv
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

---

### ❌ Windows: File Changes Not Detected (Live Reload)

**Symptom:**
- Edit Python files but Flask doesn't restart

**Fixes:**

1. Add debug mode in `docker-compose.yml`:
   ```yaml
   environment:
     - FLASK_DEBUG=1
   ```

2. Manual restart:
   ```powershell
   docker compose restart api
   ```

---

### ❌ .env File Not Found

**Symptom:**
```
ERROR: Couldn't find env file: .env
```

**Fix:**
```powershell
copy .env.example .env
# Then edit .env with your values
```

---

## 11. From Zero to Live — Summary Checklist

```
□ Clone the repository
    git clone <repo-url>
    cd TaskmanageFlask/backend

□ Create Python virtual environment
    python -m venv .venv

□ Activate virtual environment
    .\.venv\Scripts\Activate.ps1        # Windows
    source .venv/bin/activate            # macOS/Linux

□ Install Python dependencies
    pip install -r requirements.txt

□ Create environment file
    copy .env.example .env               # Windows
    cp .env.example .env                 # macOS/Linux

□ Generate and set SECRET_KEY
    python -c "import secrets; print(secrets.token_hex(32))"
    # Paste output into .env

□ Build and start Docker services
    docker compose up --build -d

□ Verify services are running
    docker compose ps

□ Test API endpoint
    curl http://localhost:5000/
    # Expected: {"message":"Voltify Task Manager API"}

✅ DONE — App is live at http://localhost:5000
```

---

## Quick Reference Commands

| Action | Command |
|--------|---------|
| Start services | `docker compose up -d` |
| Start with rebuild | `docker compose up -d --build` |
| Stop services | `docker compose down` |
| View logs | `docker compose logs -f api` |
| Shell into API | `docker exec -it shaked_taskmgmt_api /bin/bash` |
| Shell into Mongo | `docker exec -it shaked_taskmgmt_mongo mongo` |
| Reset database | `docker compose down -v && docker compose up -d` |
| Activate venv (Win) | `.\.venv\Scripts\Activate.ps1` |
| Activate venv (Unix) | `source .venv/bin/activate` |

---

*Last updated: January 2026*
