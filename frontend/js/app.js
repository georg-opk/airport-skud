// Основная логика дашборда. Файл: frontend/js/app.js
class DashboardApp {
  constructor() {
    this.api = new ApiClient();
    if (!localStorage.getItem("token")) {
      window.location.href = "login.html"; return;   // проверка авторизации
    }
    this.ws = new WebSocketClient((alert) => this.renderAlerts([alert]));
    this.loadDashboard();
  }

  /** Загрузка сводки и таблицы событий. */
  async loadDashboard() {
    try {
      const stats = await this.api.getEventsStats();
      document.getElementById("stat-pass").textContent = stats["допуск"] || 0;
      document.getElementById("stat-reject").textContent = stats["отказ"] || 0;
      document.getElementById("stat-attack").textContent = stats["атака"] || 0;
      this.renderEvents(await this.api.getEvents());
    } catch (err) {
      console.error("Ошибка загрузки дашборда:", err);
    }
  }

  /** Отрисовка таблицы событий с цветовой индикацией. */
  renderEvents(events) {
    const tbody = document.getElementById("events-body");
    tbody.innerHTML = "";
    const cls = { "допуск": "row-grant", "отказ": "row-reject",
                  "атака": "row-attack" };
    for (const e of events) {
      const tr = document.createElement("tr");
      tr.className = cls[e.result] || "";
      tr.innerHTML =
        `<td>${e.event_time}</td><td>${e.checkpoint_id}</td>` +
        `<td>${e.employee_id ?? "—"}</td><td>${e.result}</td>` +
        `<td>${(e.similarity_score ?? 0).toFixed(2)}</td>`;
      tbody.appendChild(tr);
    }
  }

  /** Отрисовка панели оповещений (real-time). */
  renderAlerts(alerts) {
    const panel = document.getElementById("alerts");
    for (const a of alerts) {
      const card = document.createElement("div");
      card.className = "alert-card";
      card.textContent = a.type + " — " + a.checkpoint;
      card.onclick = () => this.handleAlertClick(a);
      panel.appendChild(card);
    }
  }

  /** Обработка клика по оповещению (human-in-the-loop). */
  handleAlertClick(alert) {
    const ok = confirm("Подтвердить проход? Отмена — заблокировать.");
    console.info("Решение оператора:", alert, ok);
  }
}

document.addEventListener("DOMContentLoaded", () => new DashboardApp());
