CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.premios AS
WITH meses AS (
  SELECT explode(sequence(0, 23)) AS m
),
comp AS (
  SELECT m, add_months(DATE'2024-09-01', m) AS competencia FROM meses
),
gen AS (
  SELECT
    a.apolice_id,
    a.cliente_id,
    a.linha_negocio,
    a.canal_distribuicao,
    a.regiao,
    c.competencia,
    c.m,
    a.premio_mensal,
    a.status_apolice
  FROM moi_ai_catalog.metlife_workshop.apolices a
  CROSS JOIN comp c
  WHERE c.competencia >= trunc(a.data_emissao, 'MM')
    AND NOT (a.status_apolice = 'Cancelada' AND c.m >= 18)
    AND a.premio_mensal > 0
)
SELECT
  concat('PRM', lpad(cast(g.apolice_id AS string), 8, '0'), '-', date_format(g.competencia, 'yyyyMM')) AS id_pagamento,
  g.apolice_id,
  g.cliente_id,
  g.linha_negocio,
  g.canal_distribuicao,
  g.regiao,
  g.competencia,
  g.premio_mensal AS valor_devido,
  date_add(g.competencia, 9) AS data_vencimento,
  CASE
    WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 85 THEN 'Pago'
    WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 95 THEN 'Pago em Atraso'
    ELSE 'Inadimplente' END AS status_pagamento,
  CASE
    WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 85
      THEN date_add(g.competencia, 9 - pmod(hash(g.apolice_id * 100 + g.m), 5))
    WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 95
      THEN date_add(g.competencia, 9 + 5 + pmod(hash(g.apolice_id * 100 + g.m), 25))
    ELSE NULL END AS data_pagamento,
  CASE
    WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 85 THEN g.premio_mensal
    WHEN pmod(hash(g.apolice_id * 100 + g.m), 100) < 95 THEN g.premio_mensal
    ELSE 0 END AS valor_pago
FROM gen g;
