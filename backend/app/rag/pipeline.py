from psycopg2.extras import Json
from app.db import call_fn, get_conn_raw, put_conn_raw
from app.document_processing.processor import get_processor
from app.document_processing.chunker import chunk_text
from app.rag.vector_store import add_chunks_to_postgres


def process_document(document_id, app=None):
    conn = get_conn_raw()
    try:
        doc = call_fn('fn_get_document_for_processing', (document_id,), fetch_one=True, conn=conn)
        if not doc:
            raise ValueError(f'Documento no encontrado: {document_id}')

        call_fn('fn_update_document_status', (document_id, 'processing'), conn=conn)

        try:
            # 1. Extract text
            processor = get_processor(doc['file_type'])
            pages = processor.extract_text(doc['file_path'], app=app)

            # 2. Auto-categorize if no category was provided
            resolved_category_id = doc['category_id'] or ''
            if not resolved_category_id and app is not None:
                try:
                    from app.rag.categorizer import auto_categorize
                    sample = ' '.join(p['content'] for p in pages if p.get('content'))[:2000]
                    categories = call_fn('fn_list_categories', (True,), fetch_all=True, conn=conn)
                    if categories:
                        detected_id = auto_categorize(sample, doc['title'], categories, app)
                        if detected_id:
                            call_fn('fn_set_document_category', (document_id, detected_id), conn=conn)
                            resolved_category_id = detected_id
                except Exception as e:
                    print(f'[AutoCategorize skipped] {document_id}: {e}')

            # 3. Chunk text
            all_chunks = []
            chunk_index = 0
            for page_data in pages:
                chunks = chunk_text(page_data['content'])
                for chunk_content in chunks:
                    if len(chunk_content.strip()) < 50:
                        continue
                    all_chunks.append({
                        'content': chunk_content,
                        'document_id': doc['id'],
                        'title': doc['title'],
                        'category_id': resolved_category_id,
                        'page': page_data.get('page', 1),
                        'chunk_index': chunk_index,
                    })
                    chunk_index += 1

            if not all_chunks:
                raise ValueError('No se generaron chunks del documento.')

            # 4. Embed and store chunks with vectors in PostgreSQL
            try:
                add_chunks_to_postgres(all_chunks)
            except Exception as e:
                call_fn('fn_delete_chunks_by_document', (document_id,), conn=conn)
                raise

            # 5. Update document status
            call_fn('fn_update_document_status', (
                document_id, 'completed', None, len(all_chunks)
            ), conn=conn)

            if resolved_category_id:
                call_fn('fn_update_category_doc_count', (resolved_category_id,), conn=conn)

            # 6. Generate and store document summary
            if app is not None:
                try:
                    summary_text = _generate_summary(all_chunks, doc['title'], app)
                    if summary_text:
                        # Save summary text in documents.summary
                        call_fn('fn_update_document_summary', (document_id, summary_text), conn=conn)
                        # Save summary as an embedded chunk for semantic search (Stage 1)
                        from app.rag.embeddings import get_embeddings
                        embeddings_model = get_embeddings()
                        summary_vector = embeddings_model.embed_query(summary_text)
                        call_fn('fn_create_chunk', (
                            document_id, -1, summary_text, summary_vector,
                            Json({'page': 1, 'title': doc['title']}), 'summary'
                        ), fetch_one=True, conn=conn)
                except Exception as e:
                    print(f'[Summary skipped] {document_id}: {e}')

            print(f"Documento procesado: {doc['title']} ({len(all_chunks)} chunks)")

        except Exception as e:
            call_fn('fn_update_document_status', (document_id, 'failed', str(e)), conn=conn)
            raise

    finally:
        put_conn_raw(conn)


def _generate_summary(chunks, title, app):
    """Genera un resumen del documento usando el LLM."""
    from langchain_ollama import ChatOllama
    from langchain_core.messages import SystemMessage, HumanMessage

    # Tomar los primeros ~3000 chars del texto completo
    full_text = ' '.join(c['content'] for c in chunks[:20])[:3000]

    llm = ChatOllama(
        model=app.config.get('LLM_MODEL', 'gemma3:4b'),
        base_url=app.config.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
        temperature=0.1,
        num_ctx=2048,
    )
    system = SystemMessage(content='Eres un asistente que genera resúmenes académicos en español.')
    human = HumanMessage(content=(
        f'Genera un resumen conciso (3-5 oraciones) del siguiente fragmento del documento '
        f'titulado "{title}". El resumen debe capturar el tema principal, el tipo de contenido '
        f'y los puntos clave.\n\n{full_text}'
    ))
    response = llm.invoke([system, human])
    return response.content.strip()
