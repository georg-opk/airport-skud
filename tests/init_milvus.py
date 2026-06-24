"""Инициализация Milvus - создание коллекции.
Запустить один раз перед первым использованием.
"""
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

print("Подключение к Milvus...")
connections.connect(host="localhost", port="19530")

# Проверяем, существует ли коллекция
collection_name = "face_embeddings"

if utility.has_collection(collection_name):
    print(f"✅ Коллекция '{collection_name}' уже существует")
    collection = Collection(collection_name)
else:
    print(f"Создание коллекции '{collection_name}'...")

    # Создаём схему
    fields = [
        FieldSchema(name="employee_id", dtype=DataType.INT64, is_primary=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=512),
        FieldSchema(name="zone_id", dtype=DataType.INT64, default_value=0)
    ]

    schema = CollectionSchema(fields, "Face embeddings for employees")

    # Создаём коллекцию
    collection = Collection(collection_name, schema)

    # Создаём индекс (косинусное сходство)
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "COSINE",
        "params": {"nlist": 128}
    }

    collection.create_index("embedding", index_params)
    collection.load()

    print(f"✅ Коллекция '{collection_name}' создана и готова!")

print(f"\nДоступные коллекции: {utility.list_collections()}")
print("Milvus готов к работе! 🎉")