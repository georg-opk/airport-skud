class DashboardApp {
  constructor() {
    this.api = new ApiClient();
    if (!localStorage.getItem("token")) {
      window.location.href = "login.html"; return;
    }
    this.ws = new WebSocketClient((alert) => this.renderAlerts([alert]));
    this.base = { pass: 0, reject: 0, attack: 0 };
    this.cam = { grant: 0, reject: 0, attack: 0 };
    this._initCamera();
    this._initLogout();
    this.loadDashboard();
  }

  _initLogout() {
    const btn = document.getElementById("logout");
    if (btn) btn.onclick = () => {
      if (this.camera) this.camera.stopCamera();
      localStorage.removeItem("token");
      window.location.href = "login.html";
    };
  }

  _initCamera() {
    this.camera = new CameraVerification();
    this.camera.onCounters = (c) => { this.cam = c; this._renderCounters(); };
    const on = (id, fn) => { const el = document.getElementById(id); if (el) el.onclick = fn; };
    on("btn-start-camera", () => this.camera.startCamera());
    on("btn-identify", () => this.camera.identifyFrame());
    on("btn-auto", () => this.camera.toggleAuto());
    on("btn-stop-camera", () => this.camera.stopCamera());
  }

  async loadDashboard() {
    try {
      const stats = await this.api.getEventsStats();
      this.base.pass   = stats["допуск"] || 0;
      this.base.reject = stats["отказ"] || 0;
      this.base.attack = stats["атака"] || 0;
      this._renderCounters();
    } catch (err) {
      console.error("Ошибка загрузки дашборда:", err);
      this._renderCounters();
    }
  }

  _renderCounters() {
    document.getElementById("stat-pass").textContent   = this.base.pass + this.cam.grant;
    document.getElementById("stat-reject").textContent = this.base.reject + this.cam.reject;
    document.getElementById("stat-attack").textContent = this.base.attack + this.cam.attack;
  }

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

  handleAlertClick(alert) {
    const ok = confirm("Подтвердить проход? Отмена — заблокировать.");
    console.info("Решение оператора:", alert, ok);
  }
}

document.addEventListener("DOMContentLoaded", () => new DashboardApp());