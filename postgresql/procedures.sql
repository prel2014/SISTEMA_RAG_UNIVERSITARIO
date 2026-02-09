-- =====================================================
-- UPAO RAG - Stored Functions
-- =====================================================

-- =====================================================
-- AUTH FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_create_user(
    p_email VARCHAR,
    p_password_hash VARCHAR,
    p_full_name VARCHAR,
    p_role VARCHAR DEFAULT 'user'
)
RETURNS TABLE(
    id VARCHAR, email VARCHAR, password_hash VARCHAR, full_name VARCHAR,
    role VARCHAR, is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO users (email, password_hash, full_name, role)
    VALUES (p_email, p_password_hash, p_full_name, p_role)
    RETURNING users.id, users.email, users.password_hash, users.full_name,
              users.role, users.is_active, users.created_at, users.updated_at;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_user_by_email(p_email VARCHAR)
RETURNS TABLE(
    id VARCHAR, email VARCHAR, password_hash VARCHAR, full_name VARCHAR,
    role VARCHAR, is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.email, u.password_hash, u.full_name,
           u.role, u.is_active, u.created_at, u.updated_at
    FROM users u WHERE u.email = p_email;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_user_by_id(p_id VARCHAR)
RETURNS TABLE(
    id VARCHAR, email VARCHAR, password_hash VARCHAR, full_name VARCHAR,
    role VARCHAR, is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.email, u.password_hash, u.full_name,
           u.role, u.is_active, u.created_at, u.updated_at
    FROM users u WHERE u.id = p_id;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- USERS FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_list_users(
    p_search VARCHAR DEFAULT '',
    p_page INTEGER DEFAULT 1,
    p_per_page INTEGER DEFAULT 20
)
RETURNS TABLE(
    id VARCHAR, email VARCHAR, full_name VARCHAR, role VARCHAR,
    is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ,
    total_count BIGINT
) AS $$
DECLARE
    v_offset INTEGER := (p_page - 1) * p_per_page;
BEGIN
    RETURN QUERY
    SELECT u.id, u.email, u.full_name, u.role,
           u.is_active, u.created_at, u.updated_at,
           COUNT(*) OVER() AS total_count
    FROM users u
    WHERE (p_search = '' OR u.email ILIKE '%' || p_search || '%'
           OR u.full_name ILIKE '%' || p_search || '%')
    ORDER BY u.created_at DESC
    LIMIT p_per_page OFFSET v_offset;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_toggle_user_active(p_user_id VARCHAR)
RETURNS TABLE(
    id VARCHAR, email VARCHAR, full_name VARCHAR, role VARCHAR,
    is_active BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    UPDATE users SET is_active = NOT users.is_active
    WHERE users.id = p_user_id AND users.role != 'admin'
    RETURNING users.id, users.email, users.full_name, users.role,
              users.is_active, users.created_at, users.updated_at;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_delete_user(p_user_id VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_role VARCHAR;
BEGIN
    SELECT u.role INTO v_role FROM users u WHERE u.id = p_user_id;
    IF v_role IS NULL THEN RETURN FALSE; END IF;
    IF v_role = 'admin' THEN RETURN FALSE; END IF;
    DELETE FROM users WHERE users.id = p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- DOCUMENTS FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_create_document(
    p_title VARCHAR,
    p_filename VARCHAR,
    p_path VARCHAR,
    p_type VARCHAR,
    p_size INTEGER,
    p_cat_id VARCHAR,
    p_uploaded_by VARCHAR
)
RETURNS TABLE(
    id VARCHAR, title VARCHAR, original_filename VARCHAR, file_path VARCHAR,
    file_type VARCHAR, file_size INTEGER, category_id VARCHAR,
    uploaded_by VARCHAR, processing_status VARCHAR, processing_error TEXT,
    chunk_count INTEGER, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ,
    category_name VARCHAR, category_slug VARCHAR, category_color VARCHAR, category_icon VARCHAR
) AS $$
DECLARE
    v_id VARCHAR;
BEGIN
    INSERT INTO documents (title, original_filename, file_path, file_type, file_size, category_id, uploaded_by)
    VALUES (p_title, p_filename, p_path, p_type, p_size, NULLIF(p_cat_id, ''), p_uploaded_by)
    RETURNING documents.id INTO v_id;

    RETURN QUERY
    SELECT d.id, d.title, d.original_filename, d.file_path,
           d.file_type, d.file_size, d.category_id,
           d.uploaded_by, d.processing_status, d.processing_error,
           d.chunk_count, d.created_at, d.updated_at,
           c.name AS category_name, c.slug AS category_slug,
           c.color AS category_color, c.icon AS category_icon
    FROM documents d
    LEFT JOIN categories c ON d.category_id = c.id
    WHERE d.id = v_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_list_documents(
    p_search VARCHAR DEFAULT '',
    p_cat_id VARCHAR DEFAULT '',
    p_status VARCHAR DEFAULT '',
    p_page INTEGER DEFAULT 1,
    p_per_page INTEGER DEFAULT 20
)
RETURNS TABLE(
    id VARCHAR, title VARCHAR, original_filename VARCHAR, file_path VARCHAR,
    file_type VARCHAR, file_size INTEGER, category_id VARCHAR,
    uploaded_by VARCHAR, processing_status VARCHAR, processing_error TEXT,
    chunk_count INTEGER, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ,
    category_name VARCHAR, category_slug VARCHAR, category_color VARCHAR, category_icon VARCHAR,
    total_count BIGINT
) AS $$
DECLARE
    v_offset INTEGER := (p_page - 1) * p_per_page;
BEGIN
    RETURN QUERY
    SELECT d.id, d.title, d.original_filename, d.file_path,
           d.file_type, d.file_size, d.category_id,
           d.uploaded_by, d.processing_status, d.processing_error,
           d.chunk_count, d.created_at, d.updated_at,
           c.name AS category_name, c.slug AS category_slug,
           c.color AS category_color, c.icon AS category_icon,
           COUNT(*) OVER() AS total_count
    FROM documents d
    LEFT JOIN categories c ON d.category_id = c.id
    WHERE (p_search = '' OR d.title ILIKE '%' || p_search || '%'
           OR d.original_filename ILIKE '%' || p_search || '%')
      AND (p_cat_id = '' OR d.category_id = p_cat_id)
      AND (p_status = '' OR d.processing_status = p_status)
    ORDER BY d.created_at DESC
    LIMIT p_per_page OFFSET v_offset;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_document(p_id VARCHAR)
RETURNS TABLE(
    id VARCHAR, title VARCHAR, original_filename VARCHAR, file_path VARCHAR,
    file_type VARCHAR, file_size INTEGER, category_id VARCHAR,
    uploaded_by VARCHAR, processing_status VARCHAR, processing_error TEXT,
    chunk_count INTEGER, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ,
    category_name VARCHAR, category_slug VARCHAR, category_color VARCHAR, category_icon VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT d.id, d.title, d.original_filename, d.file_path,
           d.file_type, d.file_size, d.category_id,
           d.uploaded_by, d.processing_status, d.processing_error,
           d.chunk_count, d.created_at, d.updated_at,
           c.name AS category_name, c.slug AS category_slug,
           c.color AS category_color, c.icon AS category_icon
    FROM documents d
    LEFT JOIN categories c ON d.category_id = c.id
    WHERE d.id = p_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_update_document(
    p_id VARCHAR,
    p_title VARCHAR DEFAULT NULL,
    p_cat_id VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    id VARCHAR, title VARCHAR, original_filename VARCHAR, file_path VARCHAR,
    file_type VARCHAR, file_size INTEGER, category_id VARCHAR,
    uploaded_by VARCHAR, processing_status VARCHAR, processing_error TEXT,
    chunk_count INTEGER, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ,
    category_name VARCHAR, category_slug VARCHAR, category_color VARCHAR, category_icon VARCHAR
) AS $$
BEGIN
    UPDATE documents SET
        title = COALESCE(p_title, documents.title),
        category_id = CASE WHEN p_cat_id IS NOT NULL THEN NULLIF(p_cat_id, '') ELSE documents.category_id END
    WHERE documents.id = p_id;

    RETURN QUERY
    SELECT d.id, d.title, d.original_filename, d.file_path,
           d.file_type, d.file_size, d.category_id,
           d.uploaded_by, d.processing_status, d.processing_error,
           d.chunk_count, d.created_at, d.updated_at,
           c.name AS category_name, c.slug AS category_slug,
           c.color AS category_color, c.icon AS category_icon
    FROM documents d
    LEFT JOIN categories c ON d.category_id = c.id
    WHERE d.id = p_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_delete_document(p_id VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    v_file_path VARCHAR;
    v_cat_id VARCHAR;
BEGIN
    SELECT d.file_path, d.category_id INTO v_file_path, v_cat_id
    FROM documents d WHERE d.id = p_id;

    IF v_file_path IS NULL THEN RETURN NULL; END IF;

    DELETE FROM documents WHERE documents.id = p_id;

    IF v_cat_id IS NOT NULL THEN
        PERFORM fn_update_category_doc_count(v_cat_id);
    END IF;

    RETURN v_file_path;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_update_document_status(
    p_id VARCHAR,
    p_status VARCHAR,
    p_error TEXT DEFAULT NULL,
    p_chunk_count INTEGER DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE documents SET
        processing_status = p_status,
        processing_error = p_error,
        chunk_count = COALESCE(p_chunk_count, documents.chunk_count)
    WHERE documents.id = p_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_reset_document_for_reprocess(p_id VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM documents WHERE documents.id = p_id) THEN
        RETURN FALSE;
    END IF;

    DELETE FROM document_chunks WHERE document_chunks.document_id = p_id;

    UPDATE documents SET
        processing_status = 'pending',
        processing_error = NULL,
        chunk_count = 0
    WHERE documents.id = p_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_update_category_doc_count(p_cat_id VARCHAR)
RETURNS VOID AS $$
BEGIN
    UPDATE categories SET document_count = (
        SELECT COUNT(*) FROM documents
        WHERE documents.category_id = p_cat_id AND documents.processing_status = 'completed'
    ) WHERE categories.id = p_cat_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_document_for_processing(p_id VARCHAR)
RETURNS TABLE(
    id VARCHAR, title VARCHAR, file_path VARCHAR, file_type VARCHAR,
    category_id VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT d.id, d.title, d.file_path, d.file_type, d.category_id
    FROM documents d WHERE d.id = p_id;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- CATEGORIES FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_list_categories(p_active_only BOOLEAN DEFAULT TRUE)
RETURNS TABLE(
    id VARCHAR, name VARCHAR, slug VARCHAR, description TEXT,
    icon VARCHAR, color VARCHAR, is_active BOOLEAN, document_count INTEGER,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.slug, c.description,
           c.icon, c.color, c.is_active, c.document_count,
           c.created_at
    FROM categories c
    WHERE (NOT p_active_only OR c.is_active = TRUE)
    ORDER BY c.name;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_create_category(
    p_name VARCHAR,
    p_slug VARCHAR,
    p_desc TEXT DEFAULT NULL,
    p_icon VARCHAR DEFAULT 'folder',
    p_color VARCHAR DEFAULT '#1E3A5F'
)
RETURNS TABLE(
    id VARCHAR, name VARCHAR, slug VARCHAR, description TEXT,
    icon VARCHAR, color VARCHAR, is_active BOOLEAN, document_count INTEGER,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO categories (name, slug, description, icon, color)
    VALUES (p_name, p_slug, p_desc, p_icon, p_color)
    RETURNING categories.id, categories.name, categories.slug, categories.description,
              categories.icon, categories.color, categories.is_active, categories.document_count,
              categories.created_at;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_category(p_id VARCHAR)
RETURNS TABLE(
    id VARCHAR, name VARCHAR, slug VARCHAR, description TEXT,
    icon VARCHAR, color VARCHAR, is_active BOOLEAN, document_count INTEGER,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.slug, c.description,
           c.icon, c.color, c.is_active, c.document_count,
           c.created_at
    FROM categories c WHERE c.id = p_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_category_slug_exists(
    p_slug VARCHAR,
    p_exclude_id VARCHAR DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM categories
        WHERE slug = p_slug AND (p_exclude_id IS NULL OR id != p_exclude_id)
    );
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_update_category(
    p_id VARCHAR,
    p_name VARCHAR DEFAULT NULL,
    p_slug VARCHAR DEFAULT NULL,
    p_desc TEXT DEFAULT NULL,
    p_icon VARCHAR DEFAULT NULL,
    p_color VARCHAR DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT NULL
)
RETURNS TABLE(
    id VARCHAR, name VARCHAR, slug VARCHAR, description TEXT,
    icon VARCHAR, color VARCHAR, is_active BOOLEAN, document_count INTEGER,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    UPDATE categories SET
        name = COALESCE(p_name, categories.name),
        slug = COALESCE(p_slug, categories.slug),
        description = COALESCE(p_desc, categories.description),
        icon = COALESCE(p_icon, categories.icon),
        color = COALESCE(p_color, categories.color),
        is_active = COALESCE(p_is_active, categories.is_active)
    WHERE categories.id = p_id;

    RETURN QUERY
    SELECT c.id, c.name, c.slug, c.description,
           c.icon, c.color, c.is_active, c.document_count,
           c.created_at
    FROM categories c WHERE c.id = p_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_delete_category(p_id VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM documents WHERE documents.category_id = p_id) THEN
        RETURN FALSE;
    END IF;
    DELETE FROM categories WHERE categories.id = p_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- CHUNKS FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_create_chunk(
    p_doc_id VARCHAR,
    p_index INTEGER,
    p_content TEXT,
    p_qdrant_id VARCHAR DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
)
RETURNS TABLE(
    id VARCHAR, document_id VARCHAR, chunk_index INTEGER, content TEXT,
    qdrant_point_id VARCHAR, metadata_json JSONB, created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO document_chunks (document_id, chunk_index, content, qdrant_point_id, metadata_json)
    VALUES (p_doc_id, p_index, p_content, p_qdrant_id, p_metadata)
    RETURNING document_chunks.id, document_chunks.document_id, document_chunks.chunk_index,
              document_chunks.content, document_chunks.qdrant_point_id,
              document_chunks.metadata_json, document_chunks.created_at;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_delete_chunks_by_document(p_doc_id VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    DELETE FROM document_chunks WHERE document_chunks.document_id = p_doc_id;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- CHAT FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_create_chat_message(
    p_conv_id VARCHAR,
    p_user_id VARCHAR,
    p_role VARCHAR,
    p_content TEXT,
    p_sources JSONB DEFAULT NULL
)
RETURNS TABLE(
    id VARCHAR, conversation_id VARCHAR, user_id VARCHAR, role VARCHAR,
    content TEXT, source_documents JSONB, created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO chat_history (conversation_id, user_id, role, content, source_documents)
    VALUES (p_conv_id, p_user_id, p_role, p_content, p_sources)
    RETURNING chat_history.id, chat_history.conversation_id, chat_history.user_id,
              chat_history.role, chat_history.content, chat_history.source_documents,
              chat_history.created_at;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_list_conversations(
    p_user_id VARCHAR,
    p_page INTEGER DEFAULT 1,
    p_per_page INTEGER DEFAULT 20
)
RETURNS TABLE(
    conversation_id VARCHAR,
    preview TEXT,
    last_message_at TIMESTAMPTZ,
    message_count BIGINT,
    total_count BIGINT
) AS $$
DECLARE
    v_offset INTEGER := (p_page - 1) * p_per_page;
BEGIN
    RETURN QUERY
    SELECT
        ch.conversation_id,
        LEFT(MIN(CASE WHEN ch.role = 'user' THEN ch.content END), 100) AS preview,
        MAX(ch.created_at) AS last_message_at,
        COUNT(*) AS message_count,
        COUNT(*) OVER() AS total_count
    FROM chat_history ch
    WHERE ch.user_id = p_user_id
    GROUP BY ch.conversation_id
    ORDER BY last_message_at DESC
    LIMIT p_per_page OFFSET v_offset;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_conversation_messages(
    p_conv_id VARCHAR,
    p_user_id VARCHAR
)
RETURNS TABLE(
    id VARCHAR, conversation_id VARCHAR, user_id VARCHAR, role VARCHAR,
    content TEXT, source_documents JSONB, created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT ch.id, ch.conversation_id, ch.user_id, ch.role,
           ch.content, ch.source_documents, ch.created_at
    FROM chat_history ch
    WHERE ch.conversation_id = p_conv_id AND ch.user_id = p_user_id
    ORDER BY ch.created_at;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_delete_conversation(
    p_conv_id VARCHAR,
    p_user_id VARCHAR
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    DELETE FROM chat_history
    WHERE chat_history.conversation_id = p_conv_id AND chat_history.user_id = p_user_id;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- FEEDBACK FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_upsert_feedback(
    p_chat_id VARCHAR,
    p_user_id VARCHAR,
    p_rating INTEGER,
    p_comment TEXT DEFAULT NULL
)
RETURNS TABLE(
    id VARCHAR, chat_history_id VARCHAR, user_id VARCHAR,
    rating INTEGER, comment TEXT, created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO feedbacks (chat_history_id, user_id, rating, comment)
    VALUES (p_chat_id, p_user_id, p_rating, p_comment)
    ON CONFLICT (chat_history_id, user_id) DO UPDATE
    SET rating = EXCLUDED.rating, comment = EXCLUDED.comment
    RETURNING feedbacks.id, feedbacks.chat_history_id, feedbacks.user_id,
              feedbacks.rating, feedbacks.comment, feedbacks.created_at;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- ANALYTICS FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_get_dashboard_stats()
RETURNS TABLE(
    total_users BIGINT,
    total_documents BIGINT,
    total_conversations BIGINT,
    total_messages BIGINT,
    feedback_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM users WHERE role = 'user') AS total_users,
        (SELECT COUNT(*) FROM documents) AS total_documents,
        (SELECT COUNT(DISTINCT ch.conversation_id) FROM chat_history ch) AS total_conversations,
        (SELECT COUNT(*) FROM chat_history) AS total_messages,
        CASE
            WHEN (SELECT COUNT(*) FROM feedbacks) > 0
            THEN ROUND((SELECT COUNT(*) FROM feedbacks WHERE rating = 1)::NUMERIC /
                        (SELECT COUNT(*) FROM feedbacks)::NUMERIC * 100, 1)
            ELSE 0
        END AS feedback_rate;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_daily_usage(p_days INTEGER DEFAULT 30)
RETURNS TABLE(
    date DATE,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT ch.created_at::DATE AS date, COUNT(*) AS count
    FROM chat_history ch
    WHERE ch.created_at >= NOW() - (p_days || ' days')::INTERVAL
    GROUP BY ch.created_at::DATE
    ORDER BY date;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_popular_queries(
    p_days INTEGER DEFAULT 30,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE(
    content TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT LEFT(ch.content, 200) AS content, ch.created_at
    FROM chat_history ch
    WHERE ch.role = 'user' AND ch.created_at >= NOW() - (p_days || ' days')::INTERVAL
    ORDER BY ch.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_feedback_summary()
RETURNS TABLE(
    total BIGINT,
    positive BIGINT,
    negative BIGINT,
    rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE f.rating = 1) AS positive,
        COUNT(*) FILTER (WHERE f.rating = -1) AS negative,
        CASE
            WHEN COUNT(*) > 0
            THEN ROUND(COUNT(*) FILTER (WHERE f.rating = 1)::NUMERIC / COUNT(*)::NUMERIC * 100, 1)
            ELSE 0
        END AS rate
    FROM feedbacks f;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_get_recent_negative_feedback(p_limit INTEGER DEFAULT 10)
RETURNS TABLE(
    id VARCHAR, chat_history_id VARCHAR, user_id VARCHAR,
    rating INTEGER, comment TEXT, created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT f.id, f.chat_history_id, f.user_id,
           f.rating, f.comment, f.created_at
    FROM feedbacks f
    WHERE f.rating = -1
    ORDER BY f.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- SEED FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION fn_seed_admin(
    p_email VARCHAR,
    p_password_hash VARCHAR,
    p_full_name VARCHAR
)
RETURNS BOOLEAN AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM users WHERE email = p_email) THEN
        RETURN FALSE;
    END IF;
    INSERT INTO users (email, password_hash, full_name, role, is_active)
    VALUES (p_email, p_password_hash, p_full_name, 'admin', TRUE);
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fn_seed_category(
    p_name VARCHAR,
    p_slug VARCHAR,
    p_desc TEXT DEFAULT NULL,
    p_icon VARCHAR DEFAULT 'folder',
    p_color VARCHAR DEFAULT '#1E3A5F'
)
RETURNS BOOLEAN AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM categories WHERE slug = p_slug) THEN
        RETURN FALSE;
    END IF;
    INSERT INTO categories (name, slug, description, icon, color)
    VALUES (p_name, p_slug, p_desc, p_icon, p_color);
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- Unique constraint for feedback upsert
-- =====================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_feedback_chat_user'
    ) THEN
        ALTER TABLE feedbacks ADD CONSTRAINT uq_feedback_chat_user
            UNIQUE (chat_history_id, user_id);
    END IF;
END;
$$;
