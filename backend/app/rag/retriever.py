from app.rag.vector_store import search_similar


def retrieve_context(query, category_id=None, top_k=None, score_threshold=None):
    results = search_similar(
        query=query,
        top_k=top_k,
        score_threshold=score_threshold,
        category_id=category_id,
    )

    if not results:
        return '', []

    # Build context string
    context_parts = []
    sources = []
    seen_sources = set()

    for r in results:
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
