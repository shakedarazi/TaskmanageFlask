

---

## 🚀 Features

- 👤 User authentication (register/login/logout)
- ✅ Create, update, delete, and view tasks
- 🧠 AI-powered task insights via OpenAI
- 📬 Telegram alerts for new and completed tasks
- 📊 Weekly AI-generated summaries sent to Telegram
- 🧹 Modular Flask backend using Blueprints
- 🔒 Session-based security and input validation

---

## 💻 Frontend

The project includes a simple HTML/CSS/JS frontend, located in the `frontend/` folder.

- `frontend/index.html` — main UI
- `frontend/script.js` — task logic + API calls
- `frontend/style.css` — styles

Just open `index.html` in a browser and test it live with the Flask backend.

---

## 📁 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ronbitton1/Task-Management-Project.git
cd Task-Management-Project
```

### 2. Create a `.env` file

```env
MONGO_URI=mongodb://localhost:27017/task_management_db
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_token
```

> You can use `.env.example` as a reference.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Then open `index.html` in your browser to start using the frontend.

---

## 📚 API Endpoints

### 🔐 Auth

- `POST /api/auth/register` – Create user
- `POST /api/auth/login` – Log in
- `POST /api/auth/logout` – Log out
- `GET /api/auth/me` – Get current user

### 📋 Tasks

- `GET /api/tasks` – List tasks (with optional filters: `status`, `category`)
- `POST /api/tasks` – Create new task
- `GET /api/tasks/<task_id>` – Get task details
- `PUT /api/tasks/<task_id>` – Update task
- `DELETE /api/tasks/<task_id>` – Delete task
- `POST /api/tasks/update-chat-id` – Save Telegram chat ID for notifications
- `POST /api/tasks/weekly-summary` – Get OpenAI summary of open tasks

### 🧠 AI

- `POST /api/ai/recommend` – Get task recommendations from OpenAI

---

## 🔒 Security

- Session-based login with Flask, including secure cookie settings and session expiration
- User input validation (`validators.py`)
- CORS enabled via `flask-cors`
- Secrets loaded from `.env`
- Secure cookie settings with proper flags

---

## 🧪 Project Structure

```
backend/
├── app.py                  # Main Flask app
├── auth_routes.py         # Auth endpoints
├── task_routes.py         # Task endpoints
├── ai_routes.py           # AI endpoint
├── telegram_notifier.py   # Telegram integration
├── db.py                  # MongoDB setup
├── validators.py          # Input validation
├── limiter_config.py      # Request limiting
├── logic/
│   ├── ai_helpers.py      # OpenAI utilities
│   ├── task_utills.py     # Task-related helpers
├── .env.example           # Environment config template
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

frontend/
├── index.html             # Main frontend page
├── script.js              # Frontend JS logic
└── style.css              # Frontend styling
```

---

## 🎥 Demo Video Shows:

1. Run the backend (`python app.py`)
2. Open `index.html` in the browser
3. Register/login
4. Add a task (see Telegram notification)
5. Mark a task as done (see Telegram update)
6. Create multiple tasks, then trigger weekly summary (`/api/tasks/weekly-summary`)
7. Show OpenAI-generated summary in Telegram
8. Optional: show `/api/ai/recommend` result
9. End with a quick scroll of the code + README

> Recorded with Loom.


