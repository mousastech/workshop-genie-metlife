CREATE OR REPLACE TABLE moi_ai_catalog.metlife_workshop.sinistros_fraude_score AS
SELECT
  s.numero_sinistro,
  s.sinistro_id,
  s.apolice_id,
  s.tipo_sinistro,
  s.valor_reclamado,
  s.dias_desde_emissao,
  s.suspeita_fraude,
  CASE WHEN s.suspeita_fraude
       THEN 60 + pmod(hash(s.sinistro_id * 53), 40)
       ELSE pmod(hash(s.sinistro_id * 59), 56) END AS score_fraude,
  CASE
    WHEN (CASE WHEN s.suspeita_fraude THEN 60 + pmod(hash(s.sinistro_id * 53), 40)
               ELSE pmod(hash(s.sinistro_id * 59), 56) END) >= 70 THEN 'Alto'
    WHEN (CASE WHEN s.suspeita_fraude THEN 60 + pmod(hash(s.sinistro_id * 53), 40)
               ELSE pmod(hash(s.sinistro_id * 59), 56) END) >= 40 THEN 'Medio'
    ELSE 'Baixo' END AS nivel_risco,
  CASE
    WHEN s.dias_desde_emissao < 180 THEN 'Sinistro logo apos emissao da apolice'
    WHEN s.valor_reclamado > 500000 THEN 'Valor reclamado acima do padrao'
    WHEN s.suspeita_fraude THEN 'Padrao atipico de sinistralidade'
    ELSE 'Sem alerta relevante' END AS motivo_alerta_principal
FROM moi_ai_catalog.metlife_workshop.sinistros s;
