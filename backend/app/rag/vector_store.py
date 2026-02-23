from psycopg2.extras import Json
from flask import current_app
from app.db import call_fn, get_conn
from app.rag.embeddings import get_embeddings

BATCH_SIZE = 32


def add_chunks_to_postgres(chunks_data):
    """
    Genera embeddings en batch y guarda cada chunk con su vector en PostgreSQL.
    chunks_data: list of dicts: content, document_id, title, category_id, page, chunk_index
    """
    embeddings = get_embeddings()
    # Embebir con contexto del documento para mejor coincidencia semántica.
    # Se almacena c['content'] sin el prefijo; solo el embedding lleva el contexto.
    texts = [f"[{c['title']}]\n{c['content']}" for c in chunks_data]

    all_vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        all_vectors.extend(embeddings.embed_documents(batch))

    conn = get_conn()
    for i, chunk in enumerate(chunks_data):
        metadata = Json({'page': chunk['page'], 'title': chunk['title']})
        call_fn('fn_create_chunk', (
            chunk['document_id'],
            chunk['chunk_index'],
            chunk['content'],
            all_vectors[i],
            metadata,
        ), fetch_one=True, conn=conn)

    return len(chunks_data)


def search_similar(query, top_k=None, score_threshold=None, category_id=None,
                   document_ids=None, chunk_type='content'):
    """Busca chunks similares usando pgvector."""
    embeddings = get_embeddings()

    if top_k is None:
        top_k = current_app.config.get('RAG_TOP_K', 5)
    if score_threshold is None:
        score_threshold = current_app.config.get('RAG_SCORE_THRESHOLD', 0.35)
    if category_id is None:
        category_id = ''

    query_vector = embeddings.embed_query(query)

    rows = call_fn('fn_search_similar', (
        query_vector,
        top_k,
        score_threshold,
        category_id,
        False,           # p_include_excluded
        document_ids,    # lista de UUIDs o None
        chunk_type,
    ), fetch_all=True)

    if not rows:
        return []

    return [{
        'content': r['content'],
        'document_id': r['document_id'],
        'title': r['title'],
        'category_id': r['category_id'],
        'page': r['page'],
        'score': r['score'],
    } for r in rows]


def delete_document_vectors(document_id):
    """Elimina los chunks (y sus embeddings) de un documento."""
    call_fn('fn_delete_chunks_by_document', (document_id,))
