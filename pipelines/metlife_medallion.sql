-- =====================================================================
-- MetLife · Lakeflow Declarative Pipeline (SQL) — medalhão Bronze/Silver/Gold
-- Sessão 1 (Data Engineering). Produz o Gold consumido pela Sessão 2.
--
-- Publicar em: catálogo `moi_ai_catalog`, schema `metlife_medallion`
-- (defina nas Settings do pipeline: default catalog/schema).
-- Ingestão: arquivos CSV no Volume de landing (Auto Loader via `read_files`).
--   /Volumes/moi_ai_catalog/metlife_medallion/landing/<origem>/
-- =====================================================================

-- ============================ BRONZE ============================
-- Streaming Tables com Auto Loader (ingestão incremental, exactly-once).

CREATE OR REFRESH STREAMING TABLE bronze_clientes
  COMMENT 'Clientes crus (CRM) via Auto Loader'
AS SELECT *, _metadata.file_path AS _arquivo, current_timestamp() AS _ingestao
   FROM STREAM read_files('/Volumes/moi_ai_catalog/metlife_medallion/landing/clientes',
                          format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE bronze_corretores
  COMMENT 'Corretores crus (RH/parceiros)'
AS SELECT *, _metadata.file_path AS _arquivo, current_timestamp() AS _ingestao
   FROM STREAM read_files('/Volumes/moi_ai_catalog/metlife_medallion/landing/corretores',
                          format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE bronze_produtos
  COMMENT 'Catálogo de produtos cru'
AS SELECT *, _metadata.file_path AS _arquivo, current_timestamp() AS _ingestao
   FROM STREAM read_files('/Volumes/moi_ai_catalog/metlife_medallion/landing/produtos',
                          format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE bronze_apolices
  COMMENT 'Apólices cruas (sistema de apólices)'
AS SELECT *, _metadata.file_path AS _arquivo, current_timestamp() AS _ingestao
   FROM STREAM read_files('/Volumes/moi_ai_catalog/metlife_medallion/landing/apolices',
                          format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE bronze_premios
  COMMENT 'Pagamentos de prêmio crus (cobrança)'
AS SELECT *, _metadata.file_path AS _arquivo, current_timestamp() AS _ingestao
   FROM STREAM read_files('/Volumes/moi_ai_catalog/metlife_medallion/landing/premios',
                          format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE bronze_sinistros
  COMMENT 'Sinistros crus'
AS SELECT *, _metadata.file_path AS _arquivo, current_timestamp() AS _ingestao
   FROM STREAM read_files('/Volumes/moi_ai_catalog/metlife_medallion/landing/sinistros',
                          format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE bronze_fraude_score
  COMMENT 'Scores antifraude crus'
AS SELECT *, _metadata.file_path AS _arquivo, current_timestamp() AS _ingestao
   FROM STREAM read_files('/Volumes/moi_ai_catalog/metlife_medallion/landing/fraude_score',
                          format => 'csv', header => true);

-- ============================ SILVER ============================
-- Materialized Views com tipagem, padronização e QUALIDADE (expectations).

CREATE OR REFRESH MATERIALIZED VIEW silver_clientes (
  CONSTRAINT cliente_id_valido EXPECT (cliente_id IS NOT NULL) ON VIOLATION DROP ROW
)
  COMMENT 'Clientes tipados, padronizados e deduplicados por chave natural'
AS WITH tip AS (
  SELECT CAST(cliente_id AS BIGINT) cliente_id, codigo_cliente, nome_cliente, upper(sexo) sexo,
         CAST(idade AS INT) idade, cidade, uf, regiao,
         CAST(renda_mensal AS DECIMAL(12,2)) renda_mensal, initcap(segmento_cliente) segmento_cliente,
         to_date(data_cadastro) data_cadastro,
         row_number() OVER (PARTITION BY codigo_cliente ORDER BY _ingestao DESC) rn
  FROM bronze_clientes)
SELECT * EXCEPT(rn) FROM tip WHERE rn = 1;

CREATE OR REFRESH MATERIALIZED VIEW silver_corretores (
  CONSTRAINT corretor_id_valido EXPECT (corretor_id IS NOT NULL) ON VIOLATION DROP ROW
)
AS SELECT CAST(corretor_id AS BIGINT) corretor_id, codigo_corretor, nome_corretor,
          initcap(canal_distribuicao) canal_distribuicao, uf, regiao,
          to_date(data_admissao) data_admissao, CAST(meta_anual_producao AS DECIMAL(14,2)) meta_anual_producao
   FROM bronze_corretores;

CREATE OR REFRESH MATERIALIZED VIEW silver_produtos (
  CONSTRAINT produto_id_valido EXPECT (produto_id IS NOT NULL) ON VIOLATION DROP ROW
)
AS SELECT CAST(produto_id AS BIGINT) produto_id, nome_produto, initcap(linha_negocio) linha_negocio,
          tipo_produto, CAST(taxa_carregamento AS DECIMAL(6,4)) taxa_carregamento
   FROM bronze_produtos;

CREATE OR REFRESH MATERIALIZED VIEW silver_apolices (
  CONSTRAINT apolice_valida  EXPECT (numero_apolice IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT premio_nao_neg  EXPECT (CAST(premio_mensal AS DECIMAL(12,2)) >= 0) ON VIOLATION DROP ROW,
  CONSTRAINT linha_conhecida EXPECT (initcap(linha_negocio) IN ('Vida','Previdencia'))
)
  COMMENT 'Apólices tipadas e validadas'
AS SELECT CAST(apolice_id AS BIGINT) apolice_id, numero_apolice, initcap(linha_negocio) linha_negocio,
          nome_produto, tipo_produto, status_apolice,
          CAST(capital_segurado AS DECIMAL(14,2)) capital_segurado,
          CAST(premio_mensal AS DECIMAL(12,2)) premio_mensal,
          CAST(reserva_acumulada AS DECIMAL(14,2)) reserva_acumulada,
          forma_pagamento, canal_distribuicao, regiao, uf,
          to_date(data_emissao) data_emissao, to_date(data_fim_vigencia) data_fim_vigencia,
          CAST(cliente_id AS BIGINT) cliente_id, CAST(corretor_id AS BIGINT) corretor_id, CAST(produto_id AS BIGINT) produto_id
   FROM bronze_apolices;

CREATE OR REFRESH MATERIALIZED VIEW silver_premios (
  CONSTRAINT pagamento_valido EXPECT (id_pagamento IS NOT NULL) ON VIOLATION DROP ROW
)
AS SELECT id_pagamento, CAST(apolice_id AS BIGINT) apolice_id, CAST(cliente_id AS BIGINT) cliente_id,
          initcap(linha_negocio) linha_negocio, canal_distribuicao, regiao,
          CAST(competencia AS DATE) competencia, CAST(valor_devido AS DECIMAL(12,2)) valor_devido,
          to_date(data_vencimento) data_vencimento, status_pagamento,
          to_date(data_pagamento) data_pagamento, CAST(valor_pago AS DECIMAL(12,2)) valor_pago
   FROM bronze_premios;

CREATE OR REFRESH MATERIALIZED VIEW silver_sinistros (
  CONSTRAINT sinistro_valido EXPECT (numero_sinistro IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valor_nao_neg   EXPECT (CAST(valor_reclamado AS DECIMAL(14,2)) >= 0)
)
AS SELECT numero_sinistro, CAST(sinistro_id AS BIGINT) sinistro_id, CAST(apolice_id AS BIGINT) apolice_id,
          CAST(cliente_id AS BIGINT) cliente_id, CAST(produto_id AS BIGINT) produto_id, nome_produto,
          initcap(linha_negocio) linha_negocio, canal_distribuicao, regiao, uf, tipo_sinistro,
          to_date(data_ocorrencia) data_ocorrencia, to_date(data_aviso) data_aviso, to_date(data_liquidacao) data_liquidacao,
          CAST(dias_liquidacao AS INT) dias_liquidacao, status_sinistro,
          CAST(valor_reclamado AS DECIMAL(14,2)) valor_reclamado, CAST(valor_pago AS DECIMAL(14,2)) valor_pago,
          CAST(suspeita_fraude AS BOOLEAN) suspeita_fraude, CAST(dias_desde_emissao AS INT) dias_desde_emissao
   FROM bronze_sinistros;

CREATE OR REFRESH MATERIALIZED VIEW silver_fraude_score (
  CONSTRAINT score_valido EXPECT (sinistro_id IS NOT NULL) ON VIOLATION DROP ROW
)
AS SELECT numero_sinistro, CAST(sinistro_id AS BIGINT) sinistro_id, CAST(apolice_id AS BIGINT) apolice_id,
          tipo_sinistro, CAST(valor_reclamado AS DECIMAL(14,2)) valor_reclamado,
          CAST(dias_desde_emissao AS INT) dias_desde_emissao, CAST(suspeita_fraude AS BOOLEAN) suspeita_fraude,
          CAST(score_fraude AS INT) score_fraude, nivel_risco, motivo_alerta_principal
   FROM bronze_fraude_score;

-- ============================ GOLD ============================
-- Modelo de negócio (dimensões + fatos) consumido pela Sessão 2.

CREATE OR REFRESH MATERIALIZED VIEW gold_clientes   AS SELECT * FROM silver_clientes;
CREATE OR REFRESH MATERIALIZED VIEW gold_corretores AS SELECT * FROM silver_corretores;
CREATE OR REFRESH MATERIALIZED VIEW gold_produtos   AS SELECT * FROM silver_produtos;

CREATE OR REFRESH MATERIALIZED VIEW gold_apolices
  COMMENT 'Fato apólices pronto para BI/IA'
AS SELECT a.*,
     CASE WHEN a.linha_negocio='Vida' AND a.capital_segurado >= 1000000 THEN 'Alto'
          WHEN a.linha_negocio='Vida' AND a.capital_segurado >= 300000  THEN 'Medio'
          WHEN a.linha_negocio='Vida' THEN 'Baixo' ELSE 'N/A' END AS faixa_capital
   FROM silver_apolices a;

CREATE OR REFRESH MATERIALIZED VIEW gold_premios
AS SELECT p.*, date_format(p.competencia,'yyyy-MM') AS competencia_mes FROM silver_premios p;

CREATE OR REFRESH MATERIALIZED VIEW gold_sinistros    AS SELECT * FROM silver_sinistros;
CREATE OR REFRESH MATERIALIZED VIEW gold_fraude_score AS SELECT * FROM silver_fraude_score;
