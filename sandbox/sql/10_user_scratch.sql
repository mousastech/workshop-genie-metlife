-- ============================================================================
-- 10_user_scratch.sql  ·  MetLife · Track Técnico (sandbox COMPARTILHADO)
-- ============================================================================
-- O sandbox é compartilhado por todos os técnicos. Para ninguém pisar no
-- trabalho do outro, cada participante cria o SEU schema de rascunho e escreve
-- apenas nele. O GOLD (metlife_sandbox.workshop_gold) é somente LEITURA.
--
-- Padrão de isolamento:  metlife_sandbox.scratch_<usuario>
-- ============================================================================

-- OPÇÃO A (recomendada) — schema derivado automaticamente do seu login.
-- Deriva um sufixo seguro do current_user() (troca '.', '@', '-' por '_').
DECLARE OR REPLACE VARIABLE meu_schema STRING;
SET VARIABLE meu_schema =
  'metlife_sandbox.scratch_' ||
  regexp_replace(split(current_user(), '@')[0], '[^a-zA-Z0-9]', '_');

-- Cria o schema pessoal (identifier() permite usar a variável como identificador)
CREATE SCHEMA IF NOT EXISTS IDENTIFIER(meu_schema)
  COMMENT 'Rascunho pessoal do participante — isolado no sandbox compartilhado';

SELECT meu_schema AS seu_schema_de_rascunho;

-- OPÇÃO B — manual: descomente e troque <usuario> pelo seu identificador.
-- CREATE SCHEMA IF NOT EXISTS metlife_sandbox.scratch_<usuario>
--   COMMENT 'Rascunho pessoal do participante';

-- ----------------------------------------------------------------------------
-- LAB · Bloco 2 (Trabalhando na camada Gold)
-- Crie uma VIEW derivada no SEU schema, lendo do GOLD compartilhado.
-- Troque <usuario> pelo mesmo sufixo do seu schema (veja a saída acima).
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW metlife_sandbox.scratch_<usuario>.vw_carteira_por_regiao AS
SELECT
  regiao,
  linha_negocio,
  count(*)                              AS apolices,
  count_if(status_apolice = 'Ativa')    AS apolices_ativas,
  round(sum(premio_mensal), 2)          AS premio_mensal_total,
  round(avg(premio_mensal), 2)          AS premio_mensal_medio
FROM metlife_sandbox.workshop_gold.apolices
GROUP BY regiao, linha_negocio
ORDER BY premio_mensal_total DESC;

-- Confira o resultado do seu artefato pessoal:
-- SELECT * FROM metlife_sandbox.scratch_<usuario>.vw_carteira_por_regiao;
