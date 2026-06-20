"""Клиент векторного хранилища Milvus (§2.7).
Файл: backend/app/db/milvus_client.py"""
import logging
import numpy as np
from pymilvus import connections, Collection

logger = logging.getLogger(__name__)


class MilvusClient:
    """Обёртка над pymilvus для коллекции face_embeddings."""

    def __init__(self, host="localhost", port="19530",
                 collection="face_embeddings"):
        connections.connect(alias="default", host=host, port=port)
        self.collection = Collection(collection)
        self.collection.load()
        logger.info("Подключение к Milvus: %s:%s", host, port)

    def insert_embedding(self, employee_id, embedding, zone_id=0):
        """Вставка эмбеддинга сотрудника."""
        self.collection.insert([[employee_id], [embedding.tolist()], [zone_id]])
        self.collection.flush()

    def search(self, embedding, top_k=1):
        """ANN-поиск ближайших соседей (cosine)."""
        params = {"metric_type": "COSINE", "params": {"ef": 64}}
        res = self.collection.search([embedding.tolist()], "embedding", params,
                                     limit=top_k, output_fields=["employee_id"])
        return [{"employee_id": h.entity.get("employee_id"),
                 "score": float(h.score)} for h in res[0]]

    def get_embedding(self, employee_id):
        """Получение эталона по идентификатору (для 1:1)."""
        rows = self.collection.query(f"employee_id == {employee_id}",
                                     output_fields=["embedding"])
        return np.array(rows[0]["embedding"], dtype=np.float32) if rows else None

    def delete_embedding(self, employee_id):
        """Удаление эмбеддинга при увольнении."""
        self.collection.delete(f"employee_id == {employee_id}")
