-- =====================================================
-- UPAO RAG - Database Tables
-- =====================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- Function: auto-update updated_at
-- =====================================================
CREATE OR REPLACE FUNCTION fn_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Table: users
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id          VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name   VARCHAR(255) NOT NULL,
    role        VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

-- =====================================================
-- Table: categories
-- =====================================================
CREATE TABLE IF NOT EXISTS categories (
    id              VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    name            VARCHAR(100) UNIQUE NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    icon            VARCHAR(50) DEFAULT 'folder',
    color           VARCHAR(7) DEFAULT '#1E3A5F',
    is_active       BOOLEAN DEFAULT TRUE,
    document_count  INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);

-- =====================================================
-- Table: documents
-- =====================================================
CREATE TABLE IF NOT EXISTS documents (
    id                  VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    title               VARCHAR(500) NOT NULL,
    original_filename   VARCHAR(500) NOT NULL,
    file_path           VARCHAR(1000) NOT NULL,
    file_type           VARCHAR(20) NOT NULL,
    file_size           INTEGER,
    category_id         VARCHAR(36) REFERENCES categories(id) ON DELETE SET NULL,
    uploaded_by         VARCHAR(36) NOT NULL REFERENCES users(id),
    processing_status   VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    processing_error    TEXT,
    chunk_count         INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by);

DROP TRIGGER IF EXISTS trg_documents_updated_at ON documents;
CREATE TRIGGER trg_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

-- =====================================================
-- Table: document_chunks
-- =====================================================
CREATE TABLE IF NOT EXISTS document_chunks (
    id              VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    document_id     VARCHAR(36) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    qdrant_point_id VARCHAR(36),
    metadata_json   JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);

-- =====================================================
-- Table: chat_history
-- =====================================================
CREATE TABLE IF NOT EXISTS chat_history (
    id                VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    conversation_id   VARCHAR(36) NOT NULL,
    user_id           VARCHAR(36) NOT NULL REFERENCES users(id),
    role              VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content           TEXT NOT NULL,
    source_documents  JSONB,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_conversation ON chat_history(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id);

-- =====================================================
-- Table: feedbacks
-- =====================================================
CREATE TABLE IF NOT EXISTS feedbacks (
    id              VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    chat_history_id VARCHAR(36) NOT NULL REFERENCES chat_history(id) ON DELETE CASCADE,
    user_id         VARCHAR(36) NOT NULL REFERENCES users(id),
    rating          INTEGER NOT NULL CHECK (rating IN (1, -1)),
    comment         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedbacks_chat ON feedbacks(chat_history_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_user ON feedbacks(user_id);
