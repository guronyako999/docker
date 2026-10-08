// Проверка статуса PostgreSQL через nginx-прокси (/api/db-status -> backend:8000)
async function checkDb() {
  const dot = document.getElementById('db-dot');
  const msg = document.getElementById('db-msg');
  const list = document.getElementById('db-list');
  if (!dot) return;

  try {
    const res = await fetch('/api/db-status');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();

    if (data.database_connected) {
      dot.className = 'dot ok';
      msg.textContent = 'PostgreSQL подключён ✅  (версия: ' + (data.version || '?') + ')';
      if (Array.isArray(data.tables) && data.tables.length) {
        list.innerHTML = data.tables.map(t => `<li>📄 ${t}</li>`).join('');
      }
    } else {
      dot.className = 'dot error';
      msg.textContent = 'Нет соединения с базой данных ❌';
    }
  } catch (e) {
    dot.className = 'dot error';
    msg.textContent = 'Backend недоступен (' + e.message + '). Проверьте сервис db в docker compose.';
  }
}

document.addEventListener('DOMContentLoaded', checkDb);
