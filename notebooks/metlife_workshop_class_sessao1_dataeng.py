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
# MAGIC | 09h00–09h10 | **1 · Arquitetura Lakehouse & medalhão** | Unity Catalog, Lakeflow, schema + Volume |
# MAGIC | 09h10–09h35 | **2 · Ingestão (Bronze)** | Auto Loader / `read_files` / COPY INTO → Bronze cru |
# MAGIC | 09h35–10h05 | **3 · Transformação (Silver → Gold)** | tipagem, dedup, qualidade + dimensões e fatos |
# MAGIC | 10h05–10h30 | **4 · Preparação de Dados & Machine Learning** | features + treinar modelo, orquestrado após o pipeline |
# MAGIC | 10h30–10h50 | **5 · Databricks Apps & AI Gateway** | criar um app e governar o consumo de IA |
# MAGIC | 10h50–11h00 | **6 · Orquestração & Governança** | Job (pipeline→treino→dashboard), lineage, tags · handoff |
# MAGIC
# MAGIC ## 🎯 Objetivos
# MAGIC Ao final você será capaz de: desenhar a arquitetura medalhão no Unity Catalog; ingerir dados brutos com **Auto Loader**; aplicar **qualidade de dados** e tipagem no Silver; modelar **dimensões e fatos** no Gold; e orquestrar/governar o pipeline com **Lakeflow** — entregando o Gold que a Sessão 2 consome.
# MAGIC
# MAGIC > **Ambiente:** origem (simulada) em `moi_ai_catalog.metlife_workshop` · medalhão construído em `moi_ai_catalog.metlife_medallion`. Não alteramos os objetos da Sessão 2.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 1 · Arquitetura Lakehouse & medalhão
# MAGIC **09h00–09h10**
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
# MAGIC **09h10–09h35**
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
# MAGIC # 🕘 Bloco 3 · Transformação — Silver → Gold
# MAGIC **09h35–10h05**
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
# MAGIC ### 3.2 · Promoção a Gold — dimensões e fatos
# MAGIC O **Gold** é o modelo de negócio: **dimensões** conformadas e **fatos** prontos para BI/IA, preservando as dimensões que os analistas filtram (linha, canal, região, produto, tempo) — exatamente o conjunto que a **Sessão 2** consome via Metric Views, Genie e dashboards. Promovemos o Silver a Gold adicionando colunas derivadas (faixa de capital, mês de competência).

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
# MAGIC # 🕘 Bloco 4 · Preparação de Dados & Machine Learning
# MAGIC **10h05–10h30**
# MAGIC
# MAGIC 🧑‍🏫 Com o **Gold** pronto, preparamos *features* e treinamos um modelo de **propensão a fraude em sinistros** — classificação binária que gera um **score de risco** para **priorizar a fila de investigação**. Temos o rótulo `suspeita_fraude` no Gold.
# MAGIC
# MAGIC - **Preparação de dados:** seleção de features (tipo de sinistro, linha, região, valor reclamado, dias de liquidação, dias desde a emissão), tratamento de nulos e *encoding* de categorias.
# MAGIC - **Modelo:** **Gradient-Boosted Trees** (Spark MLlib) — forte em dados tabulares; baseline de **Regressão Logística** para explicabilidade; **Databricks AutoML** como acelerador.
# MAGIC - **MLOps:** rastreamento com **MLflow** e versionamento no **Unity Catalog Model Registry** (`moi_ai_catalog.metlife_pipeline.modelo_fraude`).
# MAGIC - **Orquestração:** o treino roda como uma **task do Job, dependente do pipeline** — sempre que o Gold é atualizado, o modelo é re-treinado.
# MAGIC
# MAGIC ▶️ Treino (Spark MLlib + MLflow → Unity Catalog):

# COMMAND ----------

# Treino do modelo de propensao a FRAUDE (Spark MLlib + MLflow, registrado no Unity Catalog)
# Requer runtime com ML (MLlib e MLflow ja inclusos).
from pyspark.sql.functions import col
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.classification import GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
import mlflow
from mlflow.models.signature import infer_signature

mlflow.set_registry_uri("databricks-uc")
MODELO = "moi_ai_catalog.metlife_pipeline.modelo_fraude"

df = (spark.table("moi_ai_catalog.metlife_pipeline.gold_sinistros")
        .select("tipo_sinistro", "linha_negocio", "regiao",
                col("valor_reclamado").cast("double"),
                col("dias_liquidacao").cast("double"),
                col("dias_desde_emissao").cast("double"),
                col("suspeita_fraude").cast("int").alias("label"))
        .na.fill(0))

cats = ["tipo_sinistro", "linha_negocio", "regiao"]
stages  = [StringIndexer(inputCol=c, outputCol=c+"_i", handleInvalid="keep") for c in cats]
stages += [OneHotEncoder(inputCols=[c+"_i" for c in cats], outputCols=[c+"_o" for c in cats])]
stages += [VectorAssembler(
    inputCols=[c+"_o" for c in cats] + ["valor_reclamado", "dias_liquidacao", "dias_desde_emissao"],
    outputCol="features")]
stages += [GBTClassifier(featuresCol="features", labelCol="label", maxIter=30)]

train, test = df.randomSplit([0.8, 0.2], seed=42)
with mlflow.start_run(run_name="fraude_gbt"):
    model = Pipeline(stages=stages).fit(train)
    auc = BinaryClassificationEvaluator(labelCol="label", metricName="areaUnderROC").evaluate(model.transform(test))
    mlflow.log_metric("auc_roc", auc)
    feat = ["tipo_sinistro", "linha_negocio", "regiao", "valor_reclamado", "dias_liquidacao", "dias_desde_emissao"]
    sig = infer_signature(test.select(*feat).limit(200).toPandas(),
                          model.transform(test.limit(200)).select("prediction").toPandas())
    mlflow.spark.log_model(model, "model", signature=sig, registered_model_name=MODELO,
                           dfs_tmpdir="/Volumes/moi_ai_catalog/metlife_pipeline/mlartifacts")
    print(f"AUC-ROC = {auc:.3f} | modelo registrado em {MODELO}")

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ **Checkpoint ML.** O modelo é registrado no Unity Catalog e versionado. No Job, esta etapa é a task **`treinar_modelo`**, que depende do pipeline — treino e dados ficam sincronizados. O modelo pode então ser publicado como **Model Serving endpoint** e consumido pelo app (próximo bloco), sob governança do **AI Gateway**.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 5 · Databricks Apps & AI Gateway
# MAGIC **10h30–10h50**
# MAGIC
# MAGIC 🧑‍🏫 **Databricks Apps** permite publicar aplicações web (FastAPI, Streamlit, Dash…) **dentro do Databricks**, com identidade e governança do Unity Catalog — sem infra externa. Vamos criar um app de **triagem de sinistros** que lê o Gold e chama o **modelo de fraude** para ranquear casos.
# MAGIC
# MAGIC **Estrutura mínima de um app** (no repositório: `apps/metlife_triagem/`):
# MAGIC ```yaml
# MAGIC # app.yaml
# MAGIC command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
# MAGIC env:
# MAGIC   - name: DATABRICKS_WAREHOUSE_ID
# MAGIC     value: "<warehouse_id>"
# MAGIC ```
# MAGIC ```bash
# MAGIC databricks apps create metlife-triagem
# MAGIC databricks sync ./apps/metlife_triagem "/Workspace/Users/<voce>/metlife_triagem"
# MAGIC databricks apps deploy metlife-triagem --source-code-path "/Workspace/Users/<voce>/metlife_triagem"
# MAGIC ```
# MAGIC
# MAGIC 🛡️ **Governança com AI Gateway.** Quando o app (ou o Genie) consome LLMs/modelos via **Model Serving**, o **AI Gateway** aplica controles no endpoint:
# MAGIC - **Rate limiting** por usuário/endpoint e **usage tracking** (custo/consumo).
# MAGIC - **Payload logging** (inference tables) para auditoria.
# MAGIC - **Guardrails** (PII, tópicos) e **fallbacks** entre modelos.
# MAGIC
# MAGIC Assim, o consumo de IA do app fica **rastreável, seguro e com custo controlado** — o mesmo padrão que governa o Genie na Sessão 2.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🕘 Bloco 6 · Orquestração & Governança · handoff para a Sessão 2
# MAGIC **10h50–11h00**
# MAGIC
# MAGIC 🧑‍🏫 **Orquestração (Lakeflow Job).** Um único **Job** encadeia o dia: **Task 1** roda o Declarative Pipeline (Bronze→Silver→Gold); ao concluir, **Task 2** re-treina o modelo de fraude e **Task 3** atualiza o **dashboard AI/BI** — dados, modelo e painel sempre **sincronizados**. Artefatos no repositório: `pipelines/` e `jobs/`.
# MAGIC
# MAGIC **Governança (Unity Catalog).** Tags de domínio no Gold (mesma taxonomia da Sessão 2), **lineage** automático (bronze → silver → gold → modelo/Metric Views → Genie/dashboards) e **AI Gateway** no consumo de IA.

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
