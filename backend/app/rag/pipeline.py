from app.extensions import db
from app.models.document import Document
from app.models.category import Category
from app.models.chunk import DocumentChunk
from app.document_processing.processor import get_processor
from app.document_processing.chunker import chunk_text
from app.rag.vector_store import add_chunks_to_qdrant


def process_document(document_id):
    document = Document.query.get(document_id)
    if not document:
        raise ValueError(f'Documento no encontrado: {document_id}')

    document.processing_status = 'processing'
    db.session.commit()

    try:
        # 1. Extract text
        processor = get_processor(document.file_type)
        pages = processor.extract_text(document.file_path)

        # 2. Chunk text
        all_chunks = []
        chunk_index = 0
        for page_data in pages:
            chunks = chunk_text(page_data['content'])
            for chunk_content in chunks:
                all_chunks.append({
                    'content': chunk_content,
                    'document_id': document.id,
                    'title': document.title,
                    'category_id': document.category_id or '',
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
            db_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=chunk_data['chunk_index'],
                content=chunk_data['content'],
                qdrant_point_id=point_ids[i],
                metadata_json={
                    'page': chunk_data['page'],
                    'title': chunk_data['title'],
                }
            )
            db.session.add(db_chunk)

        # 5. Update document status
        document.processing_status = 'completed'
        document.chunk_count = len(all_chunks)

        # Update category document count
        if document.category_id:
            category = Category.query.get(document.category_id)
            if category:
                category.document_count = Document.query.filter_by(
                    category_id=category.id, processing_status='completed'
                ).count()

        db.session.commit()
        print(f"Documento procesado: {document.title} ({len(all_chunks)} chunks)")

    except Exception as e:
        document.processing_status = 'failed'
        document.processing_error = str(e)
        db.session.commit()
        raise
