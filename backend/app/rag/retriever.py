from app.rag.reranker import two_stage_retrieve
from app.rag.query_expander import expand_query


def retrieve_context(query, category_id=None, top_k=None, score_threshold=None):
    # Expander: genera query original + hasta 2 variantes
    queries = expand_query(query)

    # Buscar con cada variante; mantener el chunk con mayor score si aparece en varias
    seen_chunks: dict[str, dict] = {}  # key: doc_id + page + content[:60]
    for q in queries:
        results = two_stage_retrieve(
            query=q,
            top_k=top_k,
            score_threshold=score_threshold,
            category_id=category_id,
        )
        for r in results:
            key = f"{r['document_id']}_{r['page']}_{r['content'][:60]}"
            if key not in seen_chunks or r['score'] > seen_chunks[key]['score']:
                seen_chunks[key] = r

    if not seen_chunks:
        return '', []

    # Ordenar por score desc y tomar los top_k mejores
    final_k = top_k or 5
    final_results = sorted(seen_chunks.values(), key=lambda x: x['score'], reverse=True)[:final_k]

    context_parts = []
    sources = []
    seen_sources = set()

    for r in final_results:
        context_parts.append(f"[Documento: {r['title']}, Pagina: {r['page']}]\n{r['content']}")

        source_key = f"{r['document_id']}_{r['page']}"
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({
                'document_id': r['document_id'],
                'title': r['title'],
                'page': r['page'],
                'preview': r['content'][:150] + '...' if len(r['content']) > 150 else r['content'],
                'score': round(r['score'], 3),
            })

    context = '\n\n---\n\n'.join(context_parts)
    return context, sources
