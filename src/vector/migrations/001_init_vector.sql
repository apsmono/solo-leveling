-- Idempotent schema bootstrap for Signal vector database.
-- Run via src/vector/db.py on pool open.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS signal_embeddings (
    id            SERIAL PRIMARY KEY,
    owner_id      TEXT NOT NULL DEFAULT 'default-owner',
    entry_id      TEXT NOT NULL,
    section       TEXT NOT NULL DEFAULT '',
    content_hash  TEXT NOT NULL,
    embedding     vector(768),
    summary       TEXT NOT NULL DEFAULT '',
    source_url    TEXT,
    captured_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_signal_embeddings_owner_entry
    ON signal_embeddings (owner_id, entry_id);

CREATE INDEX IF NOT EXISTS idx_signal_embeddings_vec
    ON signal_embeddings USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE TABLE IF NOT EXISTS signal_token_cache (
    id            SERIAL PRIMARY KEY,
    owner_id      TEXT NOT NULL DEFAULT 'default-owner',
    content_hash  TEXT NOT NULL,
    embedding     vector(768),
    summary       TEXT NOT NULL,
    hit_count     INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at    TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_signal_token_cache_owner_hash
    ON signal_token_cache (owner_id, content_hash);

CREATE INDEX IF NOT EXISTS idx_signal_token_cache_vec
    ON signal_token_cache USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
