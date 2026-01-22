const API = 'http://localhost:5000/api';

const qs = id => document.getElementById(id);

window.onload = () => {
  setupThemeToggle();
  checkSession();
  setupSidebarNavigation();
  setupAuth();
  setupTaskHandlers();
  setupAI();
  setupTelegram();
};

function setupThemeToggle() {
  const btn = document.createElement('button');
  btn.id = 'dark-toggle';
  btn.textContent = '☀️ / 🌙';
  document.body.appendChild(btn);
  btn.onclick = () => document.body.classList.toggle('dark-mode');
}

function checkSession() {
  fetch(`${API}/auth/me`, {
    credentials: 'include'
  }).then(res => res.json()).then(data => {
    if (data.username) {
      showDashboard();
    } else {
      hideDashboard();
    }
  });
}

function showDashboard() {
  qs('auth').style.display = 'none';
  qs('logout-btn').style.display = 'block';
  qs('sidebar').style.display = 'flex';
  switchTab('dashboard');
}

function hideDashboard() {
  qs('auth').style.display = 'block';
  ['dashboard', 'ai-section', 'telegram-section', 'add-task-section'].forEach(id => {
    qs(id).style.display = 'none';
  });
  qs('logout-btn').style.display = 'none';
  qs('sidebar').style.display = 'none';
}

function switchTab(tabId) {
  ['dashboard', 'ai-section', 'telegram-section', 'add-task-section'].forEach(id => {
    qs(id).style.display = id === tabId ? 'block' : 'none';
  });
  if (tabId === 'dashboard') {
    loadTasks();
  }
}

function displayMessage(msg, isError = false) {
  const el = qs('auth-message');
  el.textContent = msg;
  el.className = isError ? 'error-message' : 'success-message';
  el.style.display = 'block';
}

function setupSidebarNavigation() {
  qs('tab-tasks').onclick = () => switchTab('dashboard');
  qs('tab-add-task').onclick = () => switchTab('add-task-section');
  qs('tab-ai').onclick = () => switchTab('ai-section');
  qs('tab-telegram').onclick = () => switchTab('telegram-section');
  qs('logout-btn').onclick = () => {
    fetch(`${API}/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    }).then(() => {
      hideDashboard();
    });
  };
}

function setupAuth() {
  qs('login-btn').onclick = () => {
    fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      credentials: 'include',
      body: JSON.stringify({
        username: qs('auth-username').value,
        password: qs('auth-password').value
      })
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(({ status, data }) => {
      if (status === 200) {
        showDashboard();
      } else {
        displayMessage(data.error || 'Login failed', true);
      }
    });
  };

  qs('register-btn').onclick = () => {
    fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      credentials: 'include',
      body: JSON.stringify({
        username: qs('auth-username').value,
        password: qs('auth-password').value
      })
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(({ status, data }) => {
      if (status === 201) {
        displayMessage("Registration successful! You can now log in.");
        qs('auth-username').value = "";
        qs('auth-password').value = "";
      } else {
        displayMessage(data.error || "Registration failed", true);
      }
    });
  };
}

function setupTaskHandlers() {
    const msg = document.createElement('div');
    msg.id = 'task-message';
    msg.className = 'auth-message';
    msg.style.display = 'none';
    qs('add-task-btn').after(msg);
  
    qs('add-task-btn').onclick = () => {
      const title = qs('new-title').value.trim();
      const desc = qs('new-desc').value.trim();
      const due = qs('new-due').value.trim();
      const category = qs('new-category').value.trim();
  
      // Simple frontend validation
      if (!title || !due) {
        msg.textContent = 'Title and Due Date are required.';
        msg.className = 'auth-message error-message';
        msg.style.display = 'block';
        return;
      }
  
      // Submit task to backend
      fetch(`${API}/tasks/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ title, description: desc, due_date: due, category })
      })
      .then(res => res.json().then(data => ({ status: res.status, data })))
      .then(({ status, data }) => {
        if (status === 201 || status === 200) {
          msg.style.display = 'none';
          qs('new-title').value = '';
          qs('new-desc').value = '';
          qs('new-due').value = '';
          qs('new-category').value = '';
          loadTasks();
        } else {
          msg.textContent = data.error || 'Failed to add task.';
          msg.className = 'auth-message error-message';
          msg.style.display = 'block';
        }
      });
    };
  }  
  

function loadTasks() {
  fetch(`${API}/tasks/`, {
    credentials: 'include'
  }).then(r => r.json()).then(tasks => {
    const list = qs('task-list');
    list.innerHTML = '';
    tasks.forEach(t => {
      const isDone = t.status === 'done';
      const statusLabel = isDone ? `${t.status} ✅` : t.status;
      const toggleLabel = isDone ? 'Mark as Open' : 'Mark as Done';
      const nextStatus = isDone ? 'open' : 'done';

      const div = document.createElement('div');
      const categoryText = t.category ? `<em>Category: ${t.category}</em><br>` : '';
      div.innerHTML = `
        <strong>${t.title}</strong> - ${statusLabel} - due ${t.due_date}<br>
        ${categoryText}
        ${t.description}<br>
        <button onclick="markDone('${t._id}', '${nextStatus}')">${toggleLabel}</button>
        <button onclick="deleteTask('${t._id}')">Delete</button>
        <hr>
      `;
      list.appendChild(div);
    });
  });
}

function markDone(id, status) {
  fetch(`${API}/tasks/${id}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    credentials: 'include',
    body: JSON.stringify({ status })
  }).then(() => loadTasks());
}

function deleteTask(id) {
  fetch(`${API}/tasks/${id}`, {
    method: 'DELETE',
    credentials: 'include'
  }).then(() => loadTasks());
}

function setupAI() {
  const btn = qs('ai-recommend-btn');
  if (btn) {
    btn.onclick = () => {
      fetch(`${API}/ai/recommend`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({ description: qs('ai-input').value })
      })
      .then(r => r.json())
      .then(d => qs('ai-result').textContent = d.recommendation || d.error || 'Error');
    };
  }
}

function setupTelegram() {
  qs('update-telegram-btn').onclick = () => {
    fetch(`${API}/tasks/update-chat-id`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      credentials: 'include',
      body: JSON.stringify({ telegram_chat_id: qs('telegram-id').value })
    });
  };
}