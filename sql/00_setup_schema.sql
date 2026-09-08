-- 00_setup_schema.sql
-- Cria o catálogo/schema do workshop MetLife.
-- Ajuste o catálogo se necessário (padrão: moi_ai_catalog).

CREATE SCHEMA IF NOT EXISTS moi_ai_catalog.metlife_workshop
COMMENT 'Workshop AI/BI + Genie MetLife - dados sinteticos de seguros de vida, previdencia, sinistros e distribuicao';
