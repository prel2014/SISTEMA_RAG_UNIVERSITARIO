import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue
)
from flask import current_app
from app.rag.embeddings import get_embeddings


_client = None
VECTOR_SIZE = 768  # nomic-embed-text dimensions


def get_qdrant_client():
    global _client
    if _client is None:
        _client = QdrantClient(
            host=current_app.config['QDRANT_HOST'],
            port=current_app.config['QDRANT_PORT'],
        )
    return _client


def ensure_collection():
    client = get_qdrant_client()
    collection_name = current_app.config['QDRANT_COLLECTION']

    collections = [c.name for c in client.get_collections().collections]
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"Coleccion '{collection_name}' creada en Qdrant.")


def add_chunks_to_qdrant(chunks_data):
    """
    chunks_data: list of dicts with keys: content, document_id, title, category_id, page, chunk_index
    Returns list of qdrant point IDs.
    """
    client = get_qdrant_client()
    collection_name = current_app.config['QDRANT_COLLECTION']
    embeddings = get_embeddings()

    ensure_collection()

    texts = [c['content'] for c in chunks_data]
    vectors = embeddings.embed_documents(texts)

    points = []
    point_ids = []
    for i, chunk in enumerate(chunks_data):
        point_id = str(uuid.uuid4())
        point_ids.append(point_id)
        points.append(PointStruct(
            id=point_id,
            vector=vectors[i],
            payload={
                'content': chunk['content'],
                'document_id': chunk['document_id'],
                'title': chunk['title'],
                'category_id': chunk.get('category_id', ''),
                'page': chunk.get('page', 1),
                'chunk_index': chunk.get('chunk_index', 0),
            }
        ))

    # Upload in batches of 100
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(collection_name=collection_name, points=batch)

    return point_ids


def search_similar(query, top_k=None, score_threshold=None, category_id=None):
    client = get_qdrant_client()
    collection_name = current_app.config['QDRANT_COLLECTION']
    embeddings = get_embeddings()

    if top_k is None:
        top_k = current_app.config.get('RAG_TOP_K', 5)
    if score_threshold is None:
        score_threshold = current_app.config.get('RAG_SCORE_THRESHOLD', 0.35)

    query_vector = embeddings.embed_query(query)

    search_filter = None
    if category_id:
        search_filter = Filter(
            must=[FieldCondition(key='category_id', match=MatchValue(value=category_id))]
        )

    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=search_filter,
        limit=top_k,
        score_threshold=score_threshold,
    )

    return [{
        'content': r.payload.get('content', ''),
        'document_id': r.payload.get('document_id', ''),
        'title': r.payload.get('title', ''),
        'category_id': r.payload.get('category_id', ''),
        'page': r.payload.get('page', 1),
        'score': r.score,
    } for r in results]


def delete_document_vectors(document_id):
    client = get_qdrant_client()
    collection_name = current_app.config['QDRANT_COLLECTION']

    client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[FieldCondition(key='document_id', match=MatchValue(value=document_id))]
        ),
    )
