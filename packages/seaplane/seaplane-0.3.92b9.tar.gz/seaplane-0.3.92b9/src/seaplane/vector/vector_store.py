from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, PointVectors, VectorParams

from ..configuration import config
from ..model.vector import Distance as SPDistance
from ..model.vector import Vector, Vectors


class VectorStore:
    def __init__(self) -> None:
        self.client: Optional[QdrantClient] = None
        self.TIME_OUT_IN_SECONDS = 30
        pass

    def _get_client(self) -> Optional[QdrantClient]:
        if not self.client:
            self.connect()

        return self.client

    def _get_auth_header(self, force_renew: bool = False) -> str:
        token = config._token_api.access_token
        if not token or force_renew:
            token = config._token_api.renew_token()

        return f"Bearer {token}"

    def connect(self) -> QdrantClient:
        ret = QdrantClient(
            url=config.vector_db_endpoint, port=443, timeout=self.TIME_OUT_IN_SECONDS
        )

        def auth_middleware(request: Any, call_next: Any) -> Any:
            request.headers["Authorization"] = self._get_auth_header()
            response = call_next(request)

            if response.status_code == 401:
                request.headers["Authorization"] = self._get_auth_header(force_renew=True)
                response = call_next(request)

            return response

        http_client = ret.http.client
        http_client.add_middleware(auth_middleware)

        self.client = ret

        return ret

    def map_status(self, status: Any) -> str:
        return str(status).removeprefix("UpdateStatus.")

    def check_connection(self) -> QdrantClient:
        if not self.client:
            client = self.connect()
        else:
            client = self.client

        return client

    def create_index(
        self,
        name: str,
        vector_size: int = 768,
        distance: SPDistance = SPDistance.COSINE,
    ) -> bool:
        client = self.check_connection()

        return client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size, distance=self._map_to_qdrant_distance(distance)
            ),
            timeout=self.TIME_OUT_IN_SECONDS,
        )

    def recreate_index(
        self,
        name: str,
        vector_size: int = 768,
        distance: SPDistance = SPDistance.COSINE,
    ) -> bool:
        client = self.check_connection()

        return client.recreate_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size, distance=self._map_to_qdrant_distance(distance)
            ),
            timeout=self.TIME_OUT_IN_SECONDS,
        )

    def delete_index(self, name: str) -> bool:
        client = self.check_connection()

        return client.delete_collection(collection_name=name, timeout=self.TIME_OUT_IN_SECONDS)

    def list_indexes(self) -> List[str]:
        client = self.check_connection()

        collections = client.get_collections()
        return [idx.name for idx in collections.collections]

    def insert(self, index_name: str, vectors: Vectors) -> Dict[str, Any]:
        client = self.check_connection()

        ids = [vector.id for vector in vectors]

        result = client.upsert(
            collection_name=index_name,
            points=[
                PointStruct(id=vector.id, vector=vector.vector, payload=vector.metadata)
                for vector in vectors
            ],
        )

        return {"id": ids, "status": self.map_status(result.status)}

    def delete(self, index_name: str, id: List[str]) -> str:
        client = self.check_connection()

        result = client.delete_vectors(collection_name=index_name, vectors=[""], points=id)

        return self.map_status(result.status)

    def update(self, index_name: str, vectors: Vectors) -> Dict[str, Any]:
        client = self.check_connection()

        ids = [vector.id for vector in vectors]

        result = client.update_vectors(
            collection_name=index_name,
            vectors=[PointVectors(id=vector.id, vector=vector.vector) for vector in vectors],
        )

        return {"id": ids, "status": self.map_status(result.status)}

    def _map_to_qdrant_distance(self, distance: SPDistance) -> Distance:
        if distance == SPDistance.COSINE:
            return Distance.COSINE
        elif distance == SPDistance.EUCLID:
            return Distance.EUCLID
        elif distance == SPDistance.DOT:
            return Distance.DOT
        else:
            return Distance.COSINE

    def knn_search(self, index_name: str, vector: Vector, neighbors: int = 10) -> object:
        client = self.check_connection()

        return client.search(
            collection_name=index_name, query_vector=vector.vector, limit=neighbors
        )


vector_store = VectorStore()
