"""Клиент векторного хранилища Milvus (§2.7).
Файл: backend/app/db/milvus_client.py"""
import logging
import numpy as np
from pymilvus import MilvusClient as PyMilvusClient
from pymilvus import DataType

logger = logging.getLogger(__name__)


class MilvusClient:
    """Обёртка над pymilvus.MilvusClient для коллекции face_embeddings."""

    def __init__(self, host="localhost", port="19530",
                 collection="face_embeddings"):
        uri = f"http://{host}:{port}"
        self.collection_name = collection
        self._client = None
        try:
            self._client = PyMilvusClient(uri=uri)
            self._ensure_collection()
            self._client.load_collection(collection)
            logger.info("Подключение к Milvus: %s:%s", host, port)
        except Exception as exc:
            logger.error("Не удалось подключиться к Milvus: %s", exc)

    def _ensure_collection(self):
        """Создание коллекции если не существует."""
        if self._client.has_collection(self.collection_name):
            logger.info("Коллекция '%s' найдена", self.collection_name)
            return
        logger.info("Коллекция '%s' не найдена, создаю...", self.collection_name)
        schema = self._client.create_schema(auto_id=False, enable_dynamic_field=False)
        schema.add_field("employee_id", datatype=DataType.INT64, is_primary=True)
        schema.add_field("embedding",   datatype=DataType.FLOAT_VECTOR, dim=512)
        schema.add_field("zone_id",     datatype=DataType.INT64, default_value=0)
        index_params = self._client.prepare_index_params()
        index_params.add_index("embedding", index_type="IVF_FLAT",
                                metric_type="COSINE", params={"nlist": 128})
        self._client.create_collection(self.collection_name, schema=schema,
                                       index_params=index_params)
        logger.info("Коллекция '%s' создана", self.collection_name)

    def insert_embedding(self, employee_id, embedding, zone_id=0):
        try:
            data = [{"employee_id": int(employee_id),
                     "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding),
                     "zone_id": int(zone_id)}]
            self._client.insert(collection_name=self.collection_name, data=data)
        except Exception as exc:
            logger.error("Ошибка вставки в Milvus: %s", exc)

    def search(self, embedding, top_k=1):
        """ANN-поиск. Возвращает список dict или пустой список."""
        if self._client is None:
            return []
        try:
            vec = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
            res = self._client.search(
                collection_name=self.collection_name,
                data=[vec],
                limit=top_k,
                output_fields=["employee_id"],
                search_params={"metric_type": "COSINE", "params": {"nlist": 128}}
            )
            if res and len(res) > 0 and len(res[0]) > 0:
                hit = res[0][0]
                emp_id = hit.get("employee_id") or hit.get("id")
                score = float(hit.get("distance", 0.0))
                if emp_id is not None:
                    return [{"employee_id": int(emp_id), "score": score}]
        except Exception as exc:
            logger.error("Ошибка поиска в Milvus: %s", exc)
        return []

    def get_embedding(self, employee_id):
        if self._client is None:
            return None
        try:
            res = self._client.query(
                collection_name=self.collection_name,
                filter=f"employee_id == {int(employee_id)}",
                output_fields=["embedding"]
            )
            if res and len(res) > 0:
                return np.array(res[0]["embedding"], dtype=np.float32)
        except Exception as exc:
            logger.error("Ошибка запроса из Milvus: %s", exc)
        return None

    def delete_embedding(self, employee_id):
        if self._client is None:
            return
        try:
            self._client.delete(
                collection_name=self.collection_name,
                filter=f"employee_id == {int(employee_id)}"
            )
        except Exception as exc:
            logger.error("Ошибка удаления из Milvus: %s", exc)