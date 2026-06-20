// Клиент WebSocket для оповещений. Файл: frontend/js/websocket.js
class WebSocketClient {
  /** @param {function} onAlert — обработчик оповещения. */
  constructor(onAlert) {
    this.url = "ws://localhost:8000/api/v1/ws/alerts";
    this.onAlert = onAlert;
    this.connect();
  }

  /** Установка соединения и подписка на сообщения. */
  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onmessage = (event) => this.onAlert(JSON.parse(event.data));
    this.ws.onclose = () => {
      console.warn("WebSocket закрыт, переподключение через 3 с");
      setTimeout(() => this.connect(), 3000);   // переподключение
    };
    this.ws.onerror = (err) => console.error("Ошибка WebSocket:", err);
  }
}
