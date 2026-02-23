-- =====================================================
-- UPAO RAG - pgai Vectorizer
-- =====================================================
-- NOTA: pgai 0.11.2 (timescale/timescaledb-ha:pg16) no incluye
-- el componente vectorizer (ai.create_vectorizer no existe en esta versión).
-- Los embeddings son generados por el backend Python via OllamaEmbeddings
-- y almacenados directamente en document_chunks.embedding.
-- Este archivo se mantiene como placeholder para una futura actualización.

DO $$
BEGIN
    RAISE NOTICE 'vectorizer.sql: pgai vectorizer no disponible en esta imagen (pgai 0.11.2). Embeddings generados por Python.';
END;
$$;
