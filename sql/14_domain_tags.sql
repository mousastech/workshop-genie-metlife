-- 14_domain_tags.sql
-- Aplica o "Domain" do Genie Ontology via tags de Unity Catalog.
-- Observacao: neste ambiente ha tag policies governadas — a chave `camada`
-- so aceita bronze/silver/gold. Ajuste as chaves/valores conforme as
-- politicas de tags do seu metastore.

-- Schema (dominio de negocio)
ALTER SCHEMA moi_ai_catalog.metlife_workshop
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'certificado' = 'workshop');

-- Metric Views (camada semantica gold, certificada)
ALTER VIEW moi_ai_catalog.metlife_workshop.mv_carteira
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'camada' = 'gold', 'certificado' = 'sim');
ALTER VIEW moi_ai_catalog.metlife_workshop.mv_arrecadacao
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'camada' = 'gold', 'certificado' = 'sim');
ALTER VIEW moi_ai_catalog.metlife_workshop.mv_sinistralidade
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'camada' = 'gold', 'certificado' = 'sim');

-- Tabelas-fato (subdominios / areas de negocio)
ALTER TABLE moi_ai_catalog.metlife_workshop.apolices
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'area_negocio' = 'Carteira e Distribuicao');
ALTER TABLE moi_ai_catalog.metlife_workshop.premios
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'area_negocio' = 'Arrecadacao');
ALTER TABLE moi_ai_catalog.metlife_workshop.sinistros
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'area_negocio' = 'Sinistros e Fraude');

-- Glossario certificado
ALTER TABLE moi_ai_catalog.metlife_workshop.glossario_negocio
  SET TAGS ('dominio_negocio' = 'Seguros MetLife', 'certificado' = 'sim', 'tipo' = 'glossario');
