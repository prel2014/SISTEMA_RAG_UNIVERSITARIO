from flask import current_app
from app.rag.vector_store import search_similar


def two_stage_retrieve(query, category_id=None, top_k=None, score_threshold=None):
    """
    Stage 1 (Summary): Busca en chunks de resumen para identificar documentos candidatos.
    Stage 2 (Content): Busca chunks de contenido, restringido a los documentos del Stage 1.
    Fallback: Si Stage 2 no devuelve nada con el filtro, busca en todos los documentos.
    Diversity filter: acepta máximo RAG_MAX_CHUNKS_PER_DOC chunks por documento.
    """
    cfg = current_app.config
    if top_k is None:
        top_k = cfg.get('RAG_TOP_K', 5)
    if score_threshold is None:
        score_threshold = cfg.get('RAG_SCORE_THRESHOLD', 0.35)

    multiplier = cfg.get('RAG_CANDIDATE_MULTIPLIER', 4)
    factor = cfg.get('RAG_CANDIDATE_THRESHOLD_FACTOR', 0.70)

    candidate_k = min(top_k * multiplier, 40)
    candidate_threshold = max(score_threshold * factor, 0.20)

    # NIVEL 1: buscar en resúmenes para identificar documentos relevantes
    summary_hits = search_similar(
        query=query,
        top_k=min(top_k * 3, 15),
        score_threshold=max(score_threshold * 0.6, 0.20),
        category_id=category_id,
        chunk_type='summary',
    )
    candidate_doc_ids = list({h['document_id'] for h in summary_hits}) if summary_hits else None

    # NIVEL 2: buscar chunks de contenido restringido a los docs candidatos
    candidates = search_similar(
        query=query,
        top_k=candidate_k,
        score_threshold=candidate_threshold,
        category_id=category_id,
        document_ids=candidate_doc_ids,
        chunk_type='content',
    )

    # Fallback: si no hay resultados con el filtro, buscar en todos los documentos
    if not candidates and candidate_doc_ids:
        candidates = search_similar(
            query=query,
            top_k=candidate_k,
            score_threshold=candidate_threshold,
            category_id=category_id,
            chunk_type='content',
        )

    if not candidates:
        return []

    # Diversity-aware selection: máximo RAG_MAX_CHUNKS_PER_DOC por documento
    max_per_doc = cfg.get('RAG_MAX_CHUNKS_PER_DOC', 2)
    doc_counts: dict = {}
    final = []
    for chunk in candidates:          # sorted by score DESC (pgvector ORDER BY <=>)
        doc_id = chunk['document_id']
        if doc_counts.get(doc_id, 0) < max_per_doc:
            final.append(chunk)
            doc_counts[doc_id] = doc_counts.get(doc_id, 0) + 1
        if len(final) >= top_k:
            break

    return final
