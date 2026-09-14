-- ============================================================================
-- 00_setup_gold.sql  ·  MetLife · Track Técnico (sandbox compartilhado)
-- ============================================================================
-- Cria o catálogo + schema GOLD do workshop no sandbox do cliente e concede
-- acesso ao grupo de participantes.
--
-- PREMISSA DE ARQUITETURA (CAF Brasil DataHub & Self-Service Zone):
--   A ingestão e o tratamento (Bronze -> Silver) ficam a cargo da Argentina,
--   UPSTREAM. Este track trabalha SOMENTE na camada GOLD, dentro da
--   self-service zone do Brasil. Por isso NÃO construímos Bronze/Silver aqui:
--   apenas materializamos o GOLD consumível e governado.
--
-- NAMESPACE (ajuste se o sandbox usar outro catálogo/schema):
--   catálogo : metlife_sandbox
--   schema   : workshop_gold
-- ============================================================================

-- 1) Catálogo + schema Gold ---------------------------------------------------
CREATE CATALOG IF NOT EXISTS metlife_sandbox
  COMMENT 'MetLife - sandbox do workshop técnico (self-service zone)';

CREATE SCHEMA IF NOT EXISTS metlife_sandbox.workshop_gold
  COMMENT 'Camada GOLD consumível de seguros (Vida & Previdência, Sinistros & Fraude, Distribuição). Ingestão upstream = Argentina.';

-- 2) GERAÇÃO DAS TABELAS GOLD -------------------------------------------------
-- As 7 tabelas Gold são geradas pelos scripts de dados do repositório
-- (100% SQL — PyPI é bloqueado neste ambiente):
--
--     sql/01_produtos.sql      -> produtos            (12 linhas)
--     sql/02_corretores.sql    -> corretores          (150 linhas)
--     sql/03_clientes.sql      -> clientes            (5.000 linhas)
--     sql/04_apolices.sql      -> apolices            (8.000 linhas)
--     sql/05_premios.sql       -> premios             (~177.523 linhas)
--     sql/06_sinistros.sql     -> sinistros           (2.500 linhas)
--     sql/07_fraude.sql        -> sinistros_fraude_score (2.500 linhas)
--
-- COMO GERAR NO SANDBOX (Gold-only): rode os 7 scripts trocando o namespace
-- de origem `moi_ai_catalog.metlife_workshop` para `metlife_sandbox.workshop_gold`.
-- Um jeito rápido, a partir da raiz do repositório (ver também sandbox/README.md):
--
--     for f in sql/0[1-7]_*.sql; do
--       sed 's/moi_ai_catalog\.metlife_workshop/metlife_sandbox.workshop_gold/g' "$f" \
--         | databricks sql query --warehouse-id <WAREHOUSE_ID> --query - ;
--     done
--
-- (ou cole cada script no SQL Editor após o find/replace do namespace.)
--
-- CHECKPOINT de reconciliação (após gerar):
--     SELECT
--       (SELECT count(*) FROM metlife_sandbox.workshop_gold.apolices)  AS apolices,   -- 8000
--       (SELECT count(*) FROM metlife_sandbox.workshop_gold.premios)   AS premios,    -- 177523
--       (SELECT count(*) FROM metlife_sandbox.workshop_gold.sinistros) AS sinistros;  -- 2500

-- 3) GRANTS ao grupo de participantes -----------------------------------------
-- Participantes LEEM o Gold compartilhado e podem CRIAR o próprio schema de
-- rascunho (scratch_<user>) — ver 10_user_scratch.sql.
GRANT USE CATALOG            ON CATALOG metlife_sandbox                     TO `workshop_metlife_tecnico`;
GRANT USE SCHEMA             ON SCHEMA  metlife_sandbox.workshop_gold       TO `workshop_metlife_tecnico`;
GRANT SELECT                 ON SCHEMA  metlife_sandbox.workshop_gold       TO `workshop_metlife_tecnico`;
GRANT CREATE SCHEMA          ON CATALOG metlife_sandbox                     TO `workshop_metlife_tecnico`;

-- (Opcional) grupo com acesso pleno para os labs de governança (row filter /
-- column mask enxergam dados sem máscara). Ajuste ao seu metastore.
-- GRANT SELECT ON SCHEMA metlife_sandbox.workshop_gold TO `workshop_metlife_admin`;
