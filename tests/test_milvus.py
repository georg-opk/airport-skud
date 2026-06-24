"""Тест подключения к Milvus (обновлённый API)."""
from pymilvus import MilvusClient

print("Подключение к Milvus...")

try:
    # Новый API (вместо connections.connect)
    client = MilvusClient(uri="http://localhost:19530")

    print("✅ Успешное подключение к Milvus!")

    # Проверяем версию
    version = client.get_server_version()
    print(f"Версия Milvus: {version}")

    # Показываем коллекции
    collections = client.list_collections()
    print(f"Коллекции: {collections}")

    print("\nMilvus готов к работе! 🎉")

except Exception as e:
    print(f"❌ Ошибка: {e}")