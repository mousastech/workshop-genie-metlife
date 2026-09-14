-- ============================================================================
-- 30_delta_sharing.sql  ·  MetLife · Track Técnico
-- Bloco 5 — Delta Sharing / Open Sharing (NOVO)
-- ============================================================================
-- Modela o fluxo do diagrama CAF Brasil: o hub central (papel da ARGENTINA)
-- publica o GOLD via Open Sharing; a self-service zone (BRASIL) consome.
--
--   PROVEDOR (AR / hub central)  --SHARE-->  RECIPIENTE (BR / self-service)
--
-- Open Sharing = protocolo aberto (não precisa Databricks do outro lado): gera
-- um arquivo de credencial/link de ativação para o recipiente.
-- Pré-requisito: Delta Sharing habilitado no metastore do sandbox.
-- ============================================================================

-- ==== LADO PROVEDOR (executado no hub / instrutor) ==========================

-- 1) Cria o SHARE
CREATE SHARE IF NOT EXISTS metlife_gold_share
  COMMENT 'Publicação do GOLD de seguros para a self-service zone (AR -> BR)';

-- 2) Adiciona as tabelas Gold ao share
ALTER SHARE metlife_gold_share ADD TABLE metlife_sandbox.workshop_gold.apolices;
ALTER SHARE metlife_gold_share ADD TABLE metlife_sandbox.workshop_gold.premios;
ALTER SHARE metlife_gold_share ADD TABLE metlife_sandbox.workshop_gold.sinistros;
ALTER SHARE metlife_gold_share ADD TABLE metlife_sandbox.workshop_gold.clientes;
-- Dica: dá para compartilhar com particionamento/histórico e aplicar
-- partition filters por recipiente. Veja `ALTER SHARE ... ADD TABLE ... PARTITION (...)`.

SHOW ALL IN SHARE metlife_gold_share;

-- 3) Cria o RECIPIENTE em modo OPEN SHARING (sem sharing_identifier).
--    Isso gera um link de ativação (arquivo .share com o token) para entregar
--    ao consumidor da self-service zone (Brasil).
CREATE RECIPIENT IF NOT EXISTS brasil_selfservice
  COMMENT 'Self-service zone Brasil — consumidor Open Sharing do GOLD';

-- 4) Concede o share ao recipiente
GRANT SELECT ON SHARE metlife_gold_share TO RECIPIENT brasil_selfservice;

-- 5) Recupera o link de ativação (entregue ao recipiente por canal seguro)
DESCRIBE RECIPIENT brasil_selfservice;   -- veja o campo activation_link


-- ==== LADO RECIPIENTE (executado na self-service zone / Brasil) =============
-- Cenário A — recipiente TAMBÉM é Databricks (UC): monta um catálogo a partir
-- do provider e consulta como se fosse local (governado por UC).
--
--   CREATE PROVIDER metlife_hub USING '<caminho_do_arquivo_.share>';
--   CREATE CATALOG metlife_gold_recebido USING SHARE metlife_hub.metlife_gold_share;
--   SELECT regiao, count(*) FROM metlife_gold_recebido.workshop_gold.apolices GROUP BY regiao;
--
-- Cenário B — recipiente NÃO-Databricks (ex.: quem estiver em Free Edition ou
-- ferramenta externa): usa o delta-sharing client com o arquivo de credencial
-- (perfil .share) — protocolo aberto, sem dependência do provider.
--   (pandas/spark connector: `delta_sharing.load_as_pandas("<profile>#share.schema.table")`)
--
-- LAB · Bloco 5: (provedor) criar share + recipiente e pegar o activation_link;
--                (recipiente) ativar, montar o catálogo e consultar o Gold.
