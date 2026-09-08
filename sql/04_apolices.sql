CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.apolices AS
WITH base AS (
  SELECT explode(sequence(1, 8000)) AS apolice_id
),
j AS (
  SELECT
    b.apolice_id,
    pmod(hash(b.apolice_id * 3), 5000) + 1 AS cliente_id,
    pmod(hash(b.apolice_id * 7), 150) + 1  AS corretor_id,
    pmod(hash(b.apolice_id * 11), 12) + 1  AS produto_id,
    date_add(DATE'2018-01-01', pmod(hash(b.apolice_id * 13), 2800)) AS data_emissao
  FROM base b
),
enr AS (
  SELECT
    j.apolice_id,
    concat('APL', lpad(cast(j.apolice_id AS string), 8, '0')) AS numero_apolice,
    j.cliente_id, j.corretor_id, j.produto_id,
    p.nome_produto, p.linha_negocio, p.tipo_produto,
    c.canal_distribuicao, c.regiao, c.uf,
    j.data_emissao,
    date_add(j.data_emissao, (5 + pmod(hash(j.apolice_id * 29), 25)) * 365) AS data_fim_vigencia,
    CASE
      WHEN pmod(hash(j.apolice_id * 23), 100) < 70 THEN 'Ativa'
      WHEN pmod(hash(j.apolice_id * 23), 100) < 88 THEN 'Cancelada'
      WHEN pmod(hash(j.apolice_id * 23), 100) < 95 THEN 'Suspensa'
      ELSE 'Quitada' END AS status_apolice,
    CASE WHEN p.linha_negocio = 'Vida'
         THEN p.capital_min + pmod(hash(j.apolice_id * 17), greatest(p.capital_max - p.capital_min, 1))
         ELSE 0 END AS capital_segurado,
    p.taxa_carregamento,
    element_at(array('Debito Automatico','Boleto','Cartao de Credito','Consignado'),
               pmod(hash(j.apolice_id * 31), 4) + 1) AS forma_pagamento
  FROM j
  JOIN moi_ai_catalog.metlife_workshop.produtos p   ON j.produto_id = p.produto_id
  JOIN moi_ai_catalog.metlife_workshop.corretores c ON j.corretor_id = c.corretor_id
)
SELECT
  e.*,
  CASE WHEN e.linha_negocio = 'Vida'
       THEN round(e.capital_segurado * e.taxa_carregamento / 12 + pmod(hash(e.apolice_id * 43), 150), 2)
       ELSE round(100 + pmod(hash(e.apolice_id * 47), 2900), 2) END AS premio_mensal,
  CASE WHEN e.linha_negocio = 'Previdencia'
       THEN round((100 + pmod(hash(e.apolice_id * 47), 2900))
                  * greatest(months_between(least(DATE'2026-09-01', e.data_fim_vigencia), e.data_emissao), 1)
                  * 1.06, 2)
       ELSE 0 END AS reserva_acumulada
FROM enr e;
