-- Habilita la extensión pgvector en ambas bases (dify_plugin la necesita
-- también si algún plugin de embeddings la usa). Igual que
-- 01-create-plugin-db.sql, corre una sola vez, en la primera
-- inicialización de un volumen vacío.
CREATE EXTENSION IF NOT EXISTS vector;

\c dify_plugin
CREATE EXTENSION IF NOT EXISTS vector;
