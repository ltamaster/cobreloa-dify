-- postgres solo crea la base declarada en POSTGRES_DB (dify) al inicializar
-- el volumen. plugin-daemon necesita su propia base separada (dify_plugin);
-- este script corre una sola vez, cuando postgres inicializa un volumen
-- vacío por primera vez — no se re-ejecuta en un volumen ya existente.
CREATE DATABASE dify_plugin;
