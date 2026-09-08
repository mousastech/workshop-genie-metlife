CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.sinistros AS
WITH base AS (
  SELECT explode(sequence(1, 2500)) AS sinistro_id
),
j AS (
  SELECT
    s.sinistro_id,
    pmod(hash(s.sinistro_id * 3), 8000) + 1 AS apolice_id
  FROM base s
),
enr AS (
  SELECT
    j.sinistro_id,
    j.apolice_id,
    a.cliente_id, a.produto_id, a.nome_produto, a.linha_negocio,
    a.canal_distribuicao, a.regiao, a.uf, a.capital_segurado, a.reserva_acumulada, a.data_emissao,
    date_add(a.data_emissao, 30 + pmod(hash(j.sinistro_id * 13),
             greatest(datediff(DATE'2026-08-31', a.data_emissao) - 30, 60))) AS data_ocorrencia
  FROM j
  JOIN moi_ai_catalog.metlife_workshop.apolices a ON j.apolice_id = a.apolice_id
),
sin AS (
  SELECT
    e.*,
    CASE WHEN e.linha_negocio = 'Vida'
         THEN element_at(array('Morte Natural','Morte Acidental','Invalidez Permanente','Doenca Grave'),
                         pmod(hash(e.sinistro_id * 7), 4) + 1)
         ELSE element_at(array('Resgate Total','Resgate Parcial','Portabilidade','Pensao por Morte'),
                         pmod(hash(e.sinistro_id * 7), 4) + 1) END AS tipo_sinistro,
    datediff(e.data_ocorrencia, e.data_emissao) AS dias_desde_emissao,
    CASE
      WHEN pmod(hash(e.sinistro_id * 23), 100) < 65 THEN 'Pago'
      WHEN pmod(hash(e.sinistro_id * 23), 100) < 80 THEN 'Em Analise'
      WHEN pmod(hash(e.sinistro_id * 23), 100) < 92 THEN 'Negado'
      ELSE 'Aprovado' END AS status_sinistro,
    (10 + pmod(hash(e.sinistro_id * 29), 110)) AS dias_liquidacao_base
  FROM enr e
)
SELECT
  concat('SIN', lpad(cast(sinistro_id AS string), 8, '0')) AS numero_sinistro,
  sinistro_id, apolice_id, cliente_id, produto_id, nome_produto, linha_negocio,
  canal_distribuicao, regiao, uf,
  tipo_sinistro,
  data_ocorrencia,
  date_add(data_ocorrencia, pmod(hash(sinistro_id * 17), 20)) AS data_aviso,
  CASE WHEN status_sinistro IN ('Pago','Negado','Aprovado')
       THEN date_add(date_add(data_ocorrencia, pmod(hash(sinistro_id * 17), 20)), dias_liquidacao_base)
       ELSE NULL END AS data_liquidacao,
  CASE WHEN status_sinistro IN ('Pago','Negado','Aprovado') THEN dias_liquidacao_base ELSE NULL END AS dias_liquidacao,
  status_sinistro,
  round(CASE WHEN linha_negocio = 'Vida'
             THEN greatest(capital_segurado * (0.3 + pmod(hash(sinistro_id * 19), 70) / 100.0), 5000)
             ELSE greatest(reserva_acumulada * (0.2 + pmod(hash(sinistro_id * 19), 80) / 100.0), 3000) END, 2) AS valor_reclamado,
  round(CASE WHEN status_sinistro IN ('Pago','Aprovado')
             THEN CASE WHEN linha_negocio = 'Vida'
                       THEN greatest(capital_segurado * (0.3 + pmod(hash(sinistro_id * 19), 70) / 100.0), 5000)
                       ELSE greatest(reserva_acumulada * (0.2 + pmod(hash(sinistro_id * 19), 80) / 100.0), 3000) END
             ELSE 0 END, 2) AS valor_pago,
  CASE WHEN (dias_desde_emissao < 180 AND pmod(hash(sinistro_id * 37), 100) < 45)
            OR pmod(hash(sinistro_id * 41), 100) < 5
       THEN true ELSE false END AS suspeita_fraude,
  dias_desde_emissao
FROM sin;
