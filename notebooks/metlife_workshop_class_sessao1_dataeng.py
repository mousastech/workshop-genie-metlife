# Databricks notebook source
# MAGIC %md
# MAGIC # 🛠️ MetLife — Data Engineering na Databricks · Aula guiada (Sessão 1)
# MAGIC ### Sessão 1 · **Usuário Técnico / Data Engineering** · 09h00–11h00 (BRA)
# MAGIC
# MAGIC Nesta sessão construímos, do zero, o **pipeline medalhão** (Bronze → Silver → Gold) que **aterrissa os dados no catálogo** consumido pela Sessão 2 (negócio, AI/BI + Genie). Você verá ingestão, qualidade, modelagem dimensional, orquestração e governança — tudo no Unity Catalog.
# MAGIC
# MAGIC > 📅 **O dia em duas sessões:** **Sessão 1 (09h–11h) — Data Engineering (esta aula).** Sessão 2 (11h–13h) — Usuário de Negócio: AI/BI + Genie sobre o **Gold** que produzirmos aqui.
# MAGIC
# MAGIC ## 🗓️ Agenda (2h)
# MAGIC
# MAGIC | Horário | Bloco | Nesta aula |
# MAGIC |---|---|---|
# MAGIC | 09h00–09h15 | **1 · Arquitetura Lakehouse & medalhão** | Unity Catalog, Lakeflow, schema + Volume |
# MAGIC | 09h15–09h45 | **2 · Ingestão (Bronze)** | Auto Loader / `read_files` / COPY INTO → Bronze cru |
# MAGIC | 09h45–10h20 | **3 · Transformação (Silver)** | tipagem, dedup, qualidade (expectations) |
# MAGIC | 10h20–10h45 | **4 · Modelagem (Gold)** | dimensões e fatos prontos para consumo |
# MAGIC | 10h45–11h00 | **5 · Orquestração & Governança** | Lakeflow Pipeline/Job, lineage, tags · handoff p/ Sessão 2 |
# MAGIC
# MAGIC ## 🎯 Objetivos
# MAGIC Ao final você será capaz de: desenhar a arquitetura medalhão no Unity Catalog; ingerir dados brutos com **Auto Loader**; aplicar **qualidade de dados** e tipagem no Silver; modelar **dimensões e fatos** no Gold; e orquestrar/governar o pipeline com **Lakeflow** — entregando o Gold que a Sessão 2 consome.
# MAGIC
# MAGIC > **Ambiente:** origem (simulada) em `moi_ai_catalog.metlife_workshop` · medalhão construído em `moi_ai_catalog.metlife_medallion`. Não alteramos os objetos da Sessão 2.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 1 · Arquitetura Lakehouse & medalhão
# MAGIC **09h00–09h15**
# MAGIC
# MAGIC 🧑‍🏫 **Medalhão (Bronze → Silver → Gold)** é o padrão de refino progressivo:
# MAGIC - **Bronze** — dado cru, fiel à origem (schema flexível, histórico de ingestão).
# MAGIC - **Silver** — dado limpo, tipado, deduplicado e conformado (qualidade aplicada).
# MAGIC - **Gold** — modelo de negócio (dimensões e fatos) pronto para BI/IA.
# MAGIC
# MAGIC Tudo governado pelo **Unity Catalog** (catálogo → schema → tabela/volume, permissões, lineage) e orquestrado pelo **Lakeflow** (Declarative Pipelines + Jobs).
# MAGIC
# MAGIC ▶️ Criamos o schema do medalhão e um **Volume** (área de arquivos governada) para o landing bruto.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS moi_ai_catalog.metlife_medallion
# MAGIC   COMMENT 'Sessao 1 (Data Engineering) - medalhao que alimenta metlife_workshop';
# MAGIC CREATE VOLUME IF NOT EXISTS moi_ai_catalog.metlife_medallion.landing
# MAGIC   COMMENT 'Landing zone (arquivos brutos das origens)';

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 2 · Ingestão — camada Bronze
# MAGIC **09h15–09h45**
# MAGIC
# MAGIC 🧑‍🏫 Em produção, o Bronze é alimentado por **Auto Loader** (ingestão incremental de arquivos que chegam num Volume/cloud storage), por **COPY INTO** (batch idempotente) ou por conectores/streaming. Padrões:
# MAGIC
# MAGIC ```sql
# MAGIC -- Auto Loader (Lakeflow Declarative Pipeline)
# MAGIC CREATE OR REFRESH STREAMING TABLE bronze_apolices
# MAGIC AS SELECT *, _metadata.file_path AS _arquivo, current_timestamp() AS _ingestao
# MAGIC    FROM STREAM read_files('/Volumes/moi_ai_catalog/metlife_medallion/landing/apolices',
# MAGIC                           format => 'csv', header => true);
# MAGIC
# MAGIC -- COPY INTO (batch idempotente)
# MAGIC COPY INTO bronze_apolices FROM '/Volumes/.../landing/apolices'
# MAGIC   FILEFORMAT = CSV FORMAT_OPTIONS('header'='true') COPY_OPTIONS('mergeSchema'='true');
# MAGIC ```
# MAGIC
# MAGIC Para esta aula (100% executável em notebook), simulamos a **extração das origens** e materializamos o Bronze **fiel ao cru**: tudo como texto, categorias fora de padrão (ex.: linha em MAIÚSCULA), com colunas técnicas de ingestão. Silver cuida da limpeza.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- BRONZE · dimensões (cru, como chega da origem)
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.bronze_clientes AS
# MAGIC SELECT CAST(cliente_id AS STRING) cliente_id, codigo_cliente, nome_cliente, sexo,
# MAGIC        CAST(idade AS STRING) idade, cidade, uf, regiao,
# MAGIC        CAST(renda_mensal AS STRING) renda_mensal, upper(segmento_cliente) segmento_cliente,
# MAGIC        CAST(data_cadastro AS STRING) data_cadastro,
# MAGIC        current_timestamp() _ingestao, 'origem_crm' _fonte
# MAGIC FROM moi_ai_catalog.metlife_workshop.clientes;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.bronze_corretores AS
# MAGIC SELECT CAST(corretor_id AS STRING) corretor_id, codigo_corretor, nome_corretor,
# MAGIC        upper(canal_distribuicao) canal_distribuicao, uf, regiao,
# MAGIC        CAST(data_admissao AS STRING) data_admissao, CAST(meta_anual_producao AS STRING) meta_anual_producao,
# MAGIC        current_timestamp() _ingestao, 'origem_rh' _fonte
# MAGIC FROM moi_ai_catalog.metlife_workshop.corretores;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.bronze_produtos AS
# MAGIC SELECT CAST(produto_id AS STRING) produto_id, nome_produto, upper(linha_negocio) linha_negocio,
# MAGIC        tipo_produto, CAST(taxa_carregamento AS STRING) taxa_carregamento,
# MAGIC        current_timestamp() _ingestao, 'origem_catalogo' _fonte
# MAGIC FROM moi_ai_catalog.metlife_workshop.produtos;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- BRONZE · fatos (cru)
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.bronze_apolices AS
# MAGIC SELECT CAST(apolice_id AS STRING) apolice_id, numero_apolice, upper(linha_negocio) linha_negocio,
# MAGIC        nome_produto, tipo_produto, status_apolice, CAST(capital_segurado AS STRING) capital_segurado,
# MAGIC        CAST(premio_mensal AS STRING) premio_mensal, CAST(reserva_acumulada AS STRING) reserva_acumulada,
# MAGIC        forma_pagamento, canal_distribuicao, regiao, uf,
# MAGIC        CAST(data_emissao AS STRING) data_emissao, CAST(data_fim_vigencia AS STRING) data_fim_vigencia,
# MAGIC        CAST(cliente_id AS STRING) cliente_id, CAST(corretor_id AS STRING) corretor_id, CAST(produto_id AS STRING) produto_id,
# MAGIC        current_timestamp() _ingestao, 'origem_apolices' _fonte
# MAGIC FROM moi_ai_catalog.metlife_workshop.apolices;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.bronze_premios AS
# MAGIC SELECT id_pagamento, CAST(apolice_id AS STRING) apolice_id, CAST(cliente_id AS STRING) cliente_id,
# MAGIC        upper(linha_negocio) linha_negocio, canal_distribuicao, regiao,
# MAGIC        CAST(competencia AS STRING) competencia, CAST(valor_devido AS STRING) valor_devido,
# MAGIC        CAST(data_vencimento AS STRING) data_vencimento, status_pagamento,
# MAGIC        CAST(data_pagamento AS STRING) data_pagamento, CAST(valor_pago AS STRING) valor_pago,
# MAGIC        current_timestamp() _ingestao, 'origem_cobranca' _fonte
# MAGIC FROM moi_ai_catalog.metlife_workshop.premios;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.bronze_sinistros AS
# MAGIC SELECT numero_sinistro, CAST(sinistro_id AS STRING) sinistro_id, CAST(apolice_id AS STRING) apolice_id,
# MAGIC        CAST(cliente_id AS STRING) cliente_id, CAST(produto_id AS STRING) produto_id, nome_produto,
# MAGIC        upper(linha_negocio) linha_negocio, canal_distribuicao, regiao, uf, tipo_sinistro,
# MAGIC        CAST(data_ocorrencia AS STRING) data_ocorrencia, CAST(data_aviso AS STRING) data_aviso,
# MAGIC        CAST(data_liquidacao AS STRING) data_liquidacao, CAST(dias_liquidacao AS STRING) dias_liquidacao,
# MAGIC        status_sinistro, CAST(valor_reclamado AS STRING) valor_reclamado, CAST(valor_pago AS STRING) valor_pago,
# MAGIC        CAST(suspeita_fraude AS STRING) suspeita_fraude, CAST(dias_desde_emissao AS STRING) dias_desde_emissao,
# MAGIC        current_timestamp() _ingestao, 'origem_sinistros' _fonte
# MAGIC FROM moi_ai_catalog.metlife_workshop.sinistros;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.bronze_fraude_score AS
# MAGIC SELECT numero_sinistro, CAST(sinistro_id AS STRING) sinistro_id, CAST(apolice_id AS STRING) apolice_id,
# MAGIC        tipo_sinistro, CAST(valor_reclamado AS STRING) valor_reclamado,
# MAGIC        CAST(dias_desde_emissao AS STRING) dias_desde_emissao, CAST(suspeita_fraude AS STRING) suspeita_fraude,
# MAGIC        CAST(score_fraude AS STRING) score_fraude, nivel_risco, motivo_alerta_principal,
# MAGIC        current_timestamp() _ingestao, 'origem_antifraude' _fonte
# MAGIC FROM moi_ai_catalog.metlife_workshop.sinistros_fraude_score;

# COMMAND ----------

# MAGIC %md
# MAGIC ▶️ **Checkpoint Bronze** — tudo materializado como texto, fiel ao cru:

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'bronze_apolices' t, count(*) n, typeof(any_value(premio_mensal)) tipo_premio FROM moi_ai_catalog.metlife_medallion.bronze_apolices
# MAGIC UNION ALL SELECT 'bronze_premios', count(*), typeof(any_value(valor_pago)) FROM moi_ai_catalog.metlife_medallion.bronze_premios
# MAGIC UNION ALL SELECT 'bronze_sinistros', count(*), typeof(any_value(valor_reclamado)) FROM moi_ai_catalog.metlife_medallion.bronze_sinistros
# MAGIC ORDER BY t;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 3 · Transformação — camada Silver
# MAGIC **09h45–10h20**
# MAGIC
# MAGIC 🧑‍🏫 No Silver aplicamos **tipagem**, **padronização de categorias**, **deduplicação** e **qualidade de dados**. Numa Declarative Pipeline, a qualidade é declarativa com **expectations**:
# MAGIC
# MAGIC ```sql
# MAGIC CREATE OR REFRESH MATERIALIZED VIEW silver_apolices (
# MAGIC   CONSTRAINT apolice_valida   EXPECT (numero_apolice IS NOT NULL) ON VIOLATION DROP ROW,
# MAGIC   CONSTRAINT premio_nao_neg   EXPECT (premio_mensal >= 0),
# MAGIC   CONSTRAINT linha_conhecida  EXPECT (linha_negocio IN ('Vida','Previdencia'))
# MAGIC ) AS SELECT ... FROM bronze_apolices;
# MAGIC ```
# MAGIC
# MAGIC Neste notebook reproduzimos o mesmo efeito com tipagem + filtros de qualidade e uma tabela de **quarentena** para inspecionar o que foi barrado.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- SILVER · dimensões (tipadas e padronizadas; dedup por chave natural)
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.silver_clientes AS
# MAGIC WITH tip AS (
# MAGIC   SELECT CAST(cliente_id AS BIGINT) cliente_id, codigo_cliente, nome_cliente,
# MAGIC          upper(sexo) sexo, CAST(idade AS INT) idade, cidade, uf, regiao,
# MAGIC          CAST(renda_mensal AS DECIMAL(12,2)) renda_mensal, initcap(segmento_cliente) segmento_cliente,
# MAGIC          to_date(data_cadastro) data_cadastro,
# MAGIC          row_number() OVER (PARTITION BY codigo_cliente ORDER BY _ingestao DESC) rn
# MAGIC   FROM moi_ai_catalog.metlife_medallion.bronze_clientes)
# MAGIC SELECT * EXCEPT(rn) FROM tip WHERE rn = 1 AND cliente_id IS NOT NULL;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.silver_corretores AS
# MAGIC SELECT CAST(corretor_id AS BIGINT) corretor_id, codigo_corretor, nome_corretor,
# MAGIC        initcap(canal_distribuicao) canal_distribuicao, uf, regiao,
# MAGIC        to_date(data_admissao) data_admissao, CAST(meta_anual_producao AS DECIMAL(14,2)) meta_anual_producao
# MAGIC FROM moi_ai_catalog.metlife_medallion.bronze_corretores WHERE corretor_id IS NOT NULL;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.silver_produtos AS
# MAGIC SELECT CAST(produto_id AS BIGINT) produto_id, nome_produto, initcap(linha_negocio) linha_negocio,
# MAGIC        tipo_produto, CAST(taxa_carregamento AS DECIMAL(6,4)) taxa_carregamento
# MAGIC FROM moi_ai_catalog.metlife_medallion.bronze_produtos WHERE produto_id IS NOT NULL;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- SILVER · apólices (tipagem + qualidade). Linhas reprovadas vão para quarentena.
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.silver_apolices AS
# MAGIC SELECT CAST(apolice_id AS BIGINT) apolice_id, numero_apolice, initcap(linha_negocio) linha_negocio,
# MAGIC        nome_produto, tipo_produto, status_apolice,
# MAGIC        CAST(capital_segurado AS DECIMAL(14,2)) capital_segurado,
# MAGIC        CAST(premio_mensal AS DECIMAL(12,2)) premio_mensal,
# MAGIC        CAST(reserva_acumulada AS DECIMAL(14,2)) reserva_acumulada,
# MAGIC        forma_pagamento, canal_distribuicao, regiao, uf,
# MAGIC        to_date(data_emissao) data_emissao, to_date(data_fim_vigencia) data_fim_vigencia,
# MAGIC        CAST(cliente_id AS BIGINT) cliente_id, CAST(corretor_id AS BIGINT) corretor_id, CAST(produto_id AS BIGINT) produto_id
# MAGIC FROM moi_ai_catalog.metlife_medallion.bronze_apolices
# MAGIC WHERE numero_apolice IS NOT NULL
# MAGIC   AND CAST(premio_mensal AS DECIMAL(12,2)) >= 0
# MAGIC   AND initcap(linha_negocio) IN ('Vida','Previdencia');
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.silver_apolices_quarentena AS
# MAGIC SELECT *, CASE WHEN numero_apolice IS NULL THEN 'sem_numero'
# MAGIC                WHEN CAST(premio_mensal AS DECIMAL(12,2)) < 0 THEN 'premio_negativo'
# MAGIC                WHEN initcap(linha_negocio) NOT IN ('Vida','Previdencia') THEN 'linha_invalida'
# MAGIC                ELSE 'outro' END AS motivo_quarentena
# MAGIC FROM moi_ai_catalog.metlife_medallion.bronze_apolices
# MAGIC WHERE NOT (numero_apolice IS NOT NULL AND CAST(premio_mensal AS DECIMAL(12,2)) >= 0
# MAGIC            AND initcap(linha_negocio) IN ('Vida','Previdencia'));

# COMMAND ----------

# MAGIC %sql
# MAGIC -- SILVER · prêmios e sinistros
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.silver_premios AS
# MAGIC SELECT id_pagamento, CAST(apolice_id AS BIGINT) apolice_id, CAST(cliente_id AS BIGINT) cliente_id,
# MAGIC        initcap(linha_negocio) linha_negocio, canal_distribuicao, regiao,
# MAGIC        CAST(competencia AS DATE) competencia, CAST(valor_devido AS DECIMAL(12,2)) valor_devido,
# MAGIC        to_date(data_vencimento) data_vencimento, status_pagamento,
# MAGIC        to_date(data_pagamento) data_pagamento, CAST(valor_pago AS DECIMAL(12,2)) valor_pago
# MAGIC FROM moi_ai_catalog.metlife_medallion.bronze_premios WHERE id_pagamento IS NOT NULL;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.silver_sinistros AS
# MAGIC SELECT numero_sinistro, CAST(sinistro_id AS BIGINT) sinistro_id, CAST(apolice_id AS BIGINT) apolice_id,
# MAGIC        CAST(cliente_id AS BIGINT) cliente_id, CAST(produto_id AS BIGINT) produto_id, nome_produto,
# MAGIC        initcap(linha_negocio) linha_negocio, canal_distribuicao, regiao, uf, tipo_sinistro,
# MAGIC        to_date(data_ocorrencia) data_ocorrencia, to_date(data_aviso) data_aviso, to_date(data_liquidacao) data_liquidacao,
# MAGIC        CAST(dias_liquidacao AS INT) dias_liquidacao, status_sinistro,
# MAGIC        CAST(valor_reclamado AS DECIMAL(14,2)) valor_reclamado, CAST(valor_pago AS DECIMAL(14,2)) valor_pago,
# MAGIC        CAST(suspeita_fraude AS BOOLEAN) suspeita_fraude, CAST(dias_desde_emissao AS INT) dias_desde_emissao
# MAGIC FROM moi_ai_catalog.metlife_medallion.bronze_sinistros WHERE numero_sinistro IS NOT NULL;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.silver_fraude_score AS
# MAGIC SELECT numero_sinistro, CAST(sinistro_id AS BIGINT) sinistro_id, CAST(apolice_id AS BIGINT) apolice_id,
# MAGIC        tipo_sinistro, CAST(valor_reclamado AS DECIMAL(14,2)) valor_reclamado,
# MAGIC        CAST(dias_desde_emissao AS INT) dias_desde_emissao, CAST(suspeita_fraude AS BOOLEAN) suspeita_fraude,
# MAGIC        CAST(score_fraude AS INT) score_fraude, nivel_risco, motivo_alerta_principal
# MAGIC FROM moi_ai_catalog.metlife_medallion.bronze_fraude_score WHERE sinistro_id IS NOT NULL;

# COMMAND ----------

# MAGIC %md
# MAGIC ▶️ **Checkpoint Silver** — qualidade: aprovadas vs quarentena, e amostra de indicadores de qualidade.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   (SELECT count(*) FROM moi_ai_catalog.metlife_medallion.silver_apolices) AS apolices_aprovadas,
# MAGIC   (SELECT count(*) FROM moi_ai_catalog.metlife_medallion.silver_apolices_quarentena) AS apolices_quarentena,
# MAGIC   (SELECT count(*) FROM moi_ai_catalog.metlife_medallion.silver_clientes) AS clientes_dedup,
# MAGIC   (SELECT count(DISTINCT status_pagamento) FROM moi_ai_catalog.metlife_medallion.silver_premios) AS status_pagto_distintos;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 4 · Modelagem — camada Gold
# MAGIC **10h20–10h45**
# MAGIC
# MAGIC 🧑‍🏫 O **Gold** é o modelo de negócio: **dimensões** conformadas e **fatos** prontos para BI/IA, preservando as dimensões que os analistas vão filtrar (linha de negócio, canal, região, produto, tempo). É exatamente o conjunto que a **Sessão 2** consome via Metric Views, Genie e dashboards.
# MAGIC
# MAGIC Aqui promovemos o Silver a Gold, adicionando algumas colunas de negócio derivadas (ex.: faixa de capital, mês de competência).

# COMMAND ----------

# MAGIC %sql
# MAGIC -- GOLD · dimensões
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.gold_clientes AS SELECT * FROM moi_ai_catalog.metlife_medallion.silver_clientes;
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.gold_corretores AS SELECT * FROM moi_ai_catalog.metlife_medallion.silver_corretores;
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.gold_produtos AS SELECT * FROM moi_ai_catalog.metlife_medallion.silver_produtos;
# MAGIC
# MAGIC -- GOLD · fato apólices (+ coluna de negócio derivada)
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.gold_apolices AS
# MAGIC SELECT a.*,
# MAGIC        CASE WHEN a.linha_negocio='Vida' AND a.capital_segurado >= 1000000 THEN 'Alto'
# MAGIC             WHEN a.linha_negocio='Vida' AND a.capital_segurado >= 300000 THEN 'Medio'
# MAGIC             WHEN a.linha_negocio='Vida' THEN 'Baixo' ELSE 'N/A' END AS faixa_capital
# MAGIC FROM moi_ai_catalog.metlife_medallion.silver_apolices a;
# MAGIC
# MAGIC -- GOLD · fatos prêmios e sinistros
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.gold_premios AS
# MAGIC SELECT p.*, date_format(p.competencia,'yyyy-MM') AS competencia_mes FROM moi_ai_catalog.metlife_medallion.silver_premios p;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.gold_sinistros AS SELECT * FROM moi_ai_catalog.metlife_medallion.silver_sinistros;
# MAGIC CREATE OR REPLACE TABLE moi_ai_catalog.metlife_medallion.gold_fraude_score AS SELECT * FROM moi_ai_catalog.metlife_medallion.silver_fraude_score;

# COMMAND ----------

# MAGIC %md
# MAGIC ▶️ **Checkpoint Gold** — o Gold reconcilia com a origem (mesma volumetria de negócio):

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'gold_apolices' t, (SELECT count(*) FROM moi_ai_catalog.metlife_medallion.gold_apolices) medalhao,
# MAGIC         (SELECT count(*) FROM moi_ai_catalog.metlife_workshop.apolices) referencia
# MAGIC UNION ALL SELECT 'gold_premios', (SELECT count(*) FROM moi_ai_catalog.metlife_medallion.gold_premios), (SELECT count(*) FROM moi_ai_catalog.metlife_workshop.premios)
# MAGIC UNION ALL SELECT 'gold_sinistros', (SELECT count(*) FROM moi_ai_catalog.metlife_medallion.gold_sinistros), (SELECT count(*) FROM moi_ai_catalog.metlife_workshop.sinistros)
# MAGIC ORDER BY t;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 5 · Orquestração & Governança · handoff para a Sessão 2
# MAGIC **10h45–11h00**
# MAGIC
# MAGIC 🧑‍🏫 **Orquestração.** Em produção, este medalhão é um **Lakeflow Declarative Pipeline** (Bronze/Silver/Gold como *streaming tables* e *materialized views*, com *expectations*), agendado por um **Lakeflow Job**. O repositório traz a versão pronta em `pipelines/metlife_medallion.sql` + `pipelines/README.md`.
# MAGIC
# MAGIC **Governança (Unity Catalog).** Aplicamos tags de domínio no Gold (mesma taxonomia da Sessão 2) e contamos com **lineage** automático (bronze → silver → gold → Metric Views → dashboards/Genie).

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Governança: tags de domínio no Gold (alinhado à Sessão 2)
# MAGIC ALTER SCHEMA moi_ai_catalog.metlife_medallion SET TAGS ('dominio_negocio'='Seguros MetLife', 'camada'='gold');
# MAGIC ALTER TABLE moi_ai_catalog.metlife_medallion.gold_apolices  SET TAGS ('dominio_negocio'='Seguros MetLife','camada'='gold','area_negocio'='Carteira e Distribuicao');
# MAGIC ALTER TABLE moi_ai_catalog.metlife_medallion.gold_premios   SET TAGS ('dominio_negocio'='Seguros MetLife','camada'='gold','area_negocio'='Arrecadacao');
# MAGIC ALTER TABLE moi_ai_catalog.metlife_medallion.gold_sinistros SET TAGS ('dominio_negocio'='Seguros MetLife','camada'='gold','area_negocio'='Sinistros e Fraude');

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🔗 Handoff para a Sessão 2
# MAGIC O **Gold** aqui construído (dimensões + fatos) é exatamente o formato que a **Sessão 2** consome. No ambiente do workshop, a camada curada de negócio vive em **`moi_ai_catalog.metlife_workshop`**, sobre a qual já existem os **Metric Views**, o **Domain**, o **glossário**, os **2 Genie Spaces** e o **Dashboard AI/BI**.
# MAGIC
# MAGIC **Fluxo do dia inteiro:**
# MAGIC `origens → Bronze → Silver → Gold  →  Metric Views (semântica)  →  Genie + Dashboards (negócio)`
# MAGIC
# MAGIC ✅ **Encerramento.** Você construiu um pipeline medalhão governado, com ingestão, qualidade, modelagem e orquestração — pronto para a Sessão 2 transformar em autoatendimento analítico.
# MAGIC
# MAGIC > **Apêndice — Declarative Pipeline:** veja `pipelines/metlife_medallion.sql` no repositório para a versão produtiva (Auto Loader + `EXPECT`), e `pipelines/README.md` para deploy via Lakeflow.
