"""Нагрузочное тестирование REST API. Файл: backend/tests/locustfile.py"""
from locust import HttpUser, task, between


class ScudUser(HttpUser):
    """Виртуальный пользователь, имитирующий запросы с КПП."""

    wait_time = between(1, 2)

    def on_start(self):
        """Аутентификация перед началом сценария."""
        resp = self.client.post("/api/v1/auth/login",
                                params={"username": "operator",
                                        "password": "pass"})
        token = resp.json().get("access_token", "")
        self.headers = {"Authorization": f"Bearer {token}"}

    @task(3)
    def identify(self):
        """Запрос идентификации (основная нагрузка)."""
        with open("tests/data/sample_face.jpg", "rb") as f:
            self.client.post("/api/v1/cv/identify",
                             params={"checkpoint_id": 1},
                             files={"frame": f}, headers=self.headers)

    @task(1)
    def events(self):
        """Чтение журнала событий (фоновая нагрузка)."""
        self.client.get("/api/v1/events", headers=self.headers)
