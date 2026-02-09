from psycopg2.extras import Json
from app.db import call_fn, get_conn_raw, put_conn_raw
from app.document_processing.processor import get_processor
from app.document_processing.chunker import chunk_text
from app.rag.vector_store import add_chunks_to_qdrant


def process_document(document_id):
    conn = get_conn_raw()
    try:
        doc = call_fn('fn_get_document_for_processing', (document_id,), fetch_one=True, conn=conn)
        if not doc:
            raise ValueError(f'Documento no encontrado: {document_id}')

        call_fn('fn_update_document_status', (document_id, 'processing'), conn=conn)

        try:
            # 1. Extract text
            processor = get_processor(doc['file_type'])
            pages = processor.extract_text(doc['file_path'])

            # 2. Chunk text
            all_chunks = []
            chunk_index = 0
            for page_data in pages:
                chunks = chunk_text(page_data['content'])
                for chunk_content in chunks:
                    all_chunks.append({
                        'content': chunk_content,
                        'document_id': doc['id'],
                        'title': doc['title'],
                        'category_id': doc['category_id'] or '',
                        'page': page_data.get('page', 1),
                        'chunk_index': chunk_index,
                    })
                    chunk_index += 1

            if not all_chunks:
                raise ValueError('No se generaron chunks del documento.')

            # 3. Embed and store in Qdrant
            point_ids = add_chunks_to_qdrant(all_chunks)

            # 4. Save chunks in PostgreSQL
            for i, chunk_data in enumerate(all_chunks):
                metadata = Json({'page': chunk_data['page'], 'title': chunk_data['title']})
                call_fn('fn_create_chunk', (
                    doc['id'], chunk_data['chunk_index'], chunk_data['content'],
                    point_ids[i], metadata
                ), fetch_one=True, conn=conn)

            # 5. Update document status
            call_fn('fn_update_document_status', (
                document_id, 'completed', None, len(all_chunks)
            ), conn=conn)

            # Update category document count
            if doc['category_id']:
                call_fn('fn_update_category_doc_count', (doc['category_id'],), conn=conn)

            print(f"Documento procesado: {doc['title']} ({len(all_chunks)} chunks)")

        except Exception as e:
            call_fn('fn_update_document_status', (document_id, 'failed', str(e)), conn=conn)
            raise

    finally:
        put_conn_raw(conn)
