from __future__ import annotations

import structlog
from pinecone import Pinecone, ServerlessSpec

from src.config import get_settings

log = structlog.get_logger()
settings = get_settings()

_pinecone: Pinecone | None = None
_index = None


def get_pinecone_index():
    global _pinecone, _index
    if _index is None:
        _pinecone = Pinecone(api_key=settings.pinecone_api_key)
        existing = [idx.name for idx in _pinecone.list_indexes()]
        if settings.pinecone_index_name not in existing:
            _pinecone.create_index(
                name=settings.pinecone_index_name,
                dimension=settings.openai_embedding_dimensions,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.pinecone_cloud,
                    region=settings.pinecone_region,
                ),
            )
            log.info("pinecone_index_created", index=settings.pinecone_index_name)
        _index = _pinecone.Index(settings.pinecone_index_name)
    return _index


async def upsert_vector(
    vector_id: str,
    vector: list[float],
    metadata: dict,
    namespace: str,
) -> None:
    """Upsert a single vector into Pinecone."""
    index = get_pinecone_index()
    index.upsert(
        vectors=[{"id": vector_id, "values": vector, "metadata": metadata}],
        namespace=namespace,
    )
    log.info("pinecone_upsert", vector_id=vector_id, namespace=namespace)


async def query_vectors(
    query_vector: list[float],
    namespace: str,
    *,
    top_k: int = 10,
    filter: dict | None = None,
    include_metadata: bool = True,
) -> list[dict]:
    """Query Pinecone for similar vectors."""
    index = get_pinecone_index()
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        namespace=namespace,
        filter=filter,
        include_metadata=include_metadata,
        include_values=False,
    )
    return [
        {
            "id": match["id"],
            "score": match["score"],
            "metadata": match.get("metadata", {}),
        }
        for match in results.get("matches", [])
    ]


async def delete_vector(vector_id: str, namespace: str) -> None:
    """Delete a vector from Pinecone."""
    index = get_pinecone_index()
    index.delete(ids=[vector_id], namespace=namespace)
    log.info("pinecone_delete", vector_id=vector_id, namespace=namespace)
