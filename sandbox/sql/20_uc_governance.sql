-- ============================================================================
-- 20_uc_governance.sql  ·  MetLife · Track Técnico
-- Bloco 3 — Governança com Unity Catalog (AMPLIADO)
-- ============================================================================
-- Governança da self-service zone sobre o GOLD: grants, tags/Domain, lineage,
-- row filter, column masking, audit e custo. Namespace: metlife_sandbox.workshop_gold
-- Colunas sensíveis do domínio de seguros usadas nos exemplos:
--   clientes.nome_cliente (PII) · clientes.renda_mensal (financeiro)
--   sinistros.valor_reclamado (financeiro) · apolices.regiao (segmentação)
-- ============================================================================

-- 1) GRANTS -------------------------------------------------------------------
-- Princípio do menor privilégio: participantes leem o Gold; admins têm visão plena.
GRANT USE CATALOG, USE SCHEMA ON SCHEMA metlife_sandbox.workshop_gold TO `workshop_metlife_tecnico`;
GRANT SELECT ON TABLE metlife_sandbox.workshop_gold.apolices          TO `workshop_metlife_tecnico`;
GRANT SELECT ON TABLE metlife_sandbox.workshop_gold.sinistros         TO `workshop_metlife_tecnico`;
-- Inspecione quem tem o quê:
SHOW GRANTS ON SCHEMA metlife_sandbox.workshop_gold;

-- 2) TAGS / DOMAIN (Genie Ontology) -------------------------------------------
-- Marca o domínio de negócio e a camada. Obs.: em metastores com tag policies
-- governadas, a chave `camada` pode aceitar só bronze/silver/gold.
ALTER SCHEMA metlife_sandbox.workshop_gold
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'camada' = 'gold', 'certificado' = 'workshop');
ALTER TABLE metlife_sandbox.workshop_gold.apolices
  SET TAGS ('area_negocio' = 'Carteira e Distribuicao');
ALTER TABLE metlife_sandbox.workshop_gold.premios
  SET TAGS ('area_negocio' = 'Arrecadacao');
ALTER TABLE metlife_sandbox.workshop_gold.sinistros
  SET TAGS ('area_negocio' = 'Sinistros e Fraude');
-- Marca colunas sensíveis (útil p/ descoberta e políticas):
ALTER TABLE metlife_sandbox.workshop_gold.clientes
  ALTER COLUMN nome_cliente SET TAGS ('classificacao' = 'PII');
ALTER TABLE metlife_sandbox.workshop_gold.clientes
  ALTER COLUMN renda_mensal SET TAGS ('classificacao' = 'financeiro_sensivel');

-- 3) LINEAGE ------------------------------------------------------------------
-- O lineage (upstream/downstream, coluna a coluna) é capturado automaticamente
-- pelo UC quando você cria views/tabelas a partir do Gold e quando o Genie /
-- dashboards consultam. Veja no Catalog Explorer -> aba "Lineage".
-- Consulta programática (system tables):
SELECT source_table_full_name, target_table_full_name, event_time
FROM system.access.table_lineage
WHERE target_table_full_name LIKE 'metlife_sandbox.workshop_gold.%'
ORDER BY event_time DESC
LIMIT 20;

-- 4) ROW FILTER (segurança em nível de linha) ---------------------------------
-- Cada steward regional enxerga só a sua região; o grupo admin vê tudo.
CREATE OR REPLACE FUNCTION metlife_sandbox.workshop_gold.rf_regiao(regiao STRING)
  RETURN is_account_group_member('workshop_metlife_admin')
      OR regiao = 'Sudeste';   -- exemplo: perfil regional = Sudeste
COMMENT ON FUNCTION metlife_sandbox.workshop_gold.rf_regiao IS
  'Row filter: admin vê tudo; demais veem apenas a região Sudeste (exemplo de RLS).';

ALTER TABLE metlife_sandbox.workshop_gold.apolices
  SET ROW FILTER metlife_sandbox.workshop_gold.rf_regiao ON (regiao);

-- Teste: como participante (não-admin) só devem aparecer linhas do Sudeste.
-- SELECT DISTINCT regiao FROM metlife_sandbox.workshop_gold.apolices;
-- Para remover: ALTER TABLE ... DROP ROW FILTER;

-- 5) COLUMN MASK (mascaramento de coluna) -------------------------------------
-- 5a) Máscara de texto (PII): nome do cliente.
CREATE OR REPLACE FUNCTION metlife_sandbox.workshop_gold.mask_nome(v STRING)
  RETURN CASE WHEN is_account_group_member('workshop_metlife_admin') THEN v
              ELSE '*** MASCARADO ***' END;
ALTER TABLE metlife_sandbox.workshop_gold.clientes
  ALTER COLUMN nome_cliente SET MASK metlife_sandbox.workshop_gold.mask_nome;

-- 5b) Máscara numérica (financeiro): renda do cliente.
CREATE OR REPLACE FUNCTION metlife_sandbox.workshop_gold.mask_valor(v DOUBLE)
  RETURN CASE WHEN is_account_group_member('workshop_metlife_admin') THEN v
              ELSE NULL END;
ALTER TABLE metlife_sandbox.workshop_gold.clientes
  ALTER COLUMN renda_mensal SET MASK metlife_sandbox.workshop_gold.mask_valor;

-- 5c) Máscara no valor reclamado de sinistros (reutiliza mask_valor).
ALTER TABLE metlife_sandbox.workshop_gold.sinistros
  ALTER COLUMN valor_reclamado SET MASK metlife_sandbox.workshop_gold.mask_valor;

-- Teste: como participante, nome vem mascarado e valores vêm NULL.
-- SELECT nome_cliente, renda_mensal FROM metlife_sandbox.workshop_gold.clientes LIMIT 5;
-- Para remover: ALTER TABLE ... ALTER COLUMN <col> DROP MASK;

-- 6) AUDIT & CUSTO (system tables) --------------------------------------------
-- Auditoria de acessos (quem consultou o quê):
SELECT event_time, user_identity.email, action_name, request_params.full_name_arg AS objeto
FROM system.access.audit
WHERE action_name IN ('getTable','generateTemporaryTableCredential')
  AND event_date >= current_date() - INTERVAL 1 DAY
ORDER BY event_time DESC
LIMIT 20;

-- Custo por SKU (amarra na trilha de Governança/Custos do diagrama CAF Brasil):
SELECT usage_date, sku_name, round(sum(usage_quantity), 2) AS dbus
FROM system.billing.usage
WHERE usage_date >= current_date() - INTERVAL 7 DAYS
GROUP BY usage_date, sku_name
ORDER BY usage_date DESC, dbus DESC
LIMIT 20;
