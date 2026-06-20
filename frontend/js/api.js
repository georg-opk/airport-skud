// Клиент REST API на основе Fetch API. Файл: frontend/js/api.js
const BASE_URL = "http://localhost:8000/api/v1";

class ApiClient {
  /** Базовый запрос с подстановкой JWT-токена. */
  async request(path, options = {}) {
    const token = localStorage.getItem("token");
    const headers = { "Content-Type": "application/json", ...options.headers };
    if (token) headers["Authorization"] = "Bearer " + token;
    try {
      const res = await fetch(BASE_URL + path, { ...options, headers });
      if (res.status === 401) { window.location.href = "login.html"; return null; }
      if (!res.ok) throw new Error("HTTP " + res.status);
      return await res.json();
    } catch (err) {
      console.error("Ошибка запроса:", err);
      throw err;
    }
  }

  /** Аутентификация и сохранение токена. */
  async login(username, password) {
    const data = await this.request("/auth/login", {
      method: "POST", body: JSON.stringify({ username, password }) });
    if (data) localStorage.setItem("token", data.access_token);
    return data;
  }

  getEmployees() { return this.request("/employees"); }
  getEvents(query = "") { return this.request("/events" + query); }
  getEventsStats() { return this.request("/events/stats"); }
}
