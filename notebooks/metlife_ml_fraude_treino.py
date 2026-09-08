# Databricks notebook source
# MAGIC %md
# MAGIC # MetLife · Treino do modelo de propensão a fraude (orquestrado pelo Job)
# MAGIC Gradient-Boosted Trees (Spark MLlib) + MLflow → Unity Catalog Model Registry. Executa após o pipeline.

# COMMAND ----------

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
stages += [VectorAssembler(inputCols=[c+"_o" for c in cats] + ["valor_reclamado","dias_liquidacao","dias_desde_emissao"], outputCol="features")]
stages += [GBTClassifier(featuresCol="features", labelCol="label", maxIter=30)]

train, test = df.randomSplit([0.8, 0.2], seed=42)
with mlflow.start_run(run_name="fraude_gbt"):
    model = Pipeline(stages=stages).fit(train)
    auc = BinaryClassificationEvaluator(labelCol="label", metricName="areaUnderROC").evaluate(model.transform(test))
    mlflow.log_metric("auc_roc", auc)
    feat = ["tipo_sinistro","linha_negocio","regiao","valor_reclamado","dias_liquidacao","dias_desde_emissao"]
    sample = test.select(*feat).limit(200).toPandas()
    sig = infer_signature(sample, model.transform(test.limit(200)).select("prediction").toPandas())
    mlflow.spark.log_model(model, "model", signature=sig, registered_model_name=MODELO,
                           dfs_tmpdir="/Volumes/moi_ai_catalog/metlife_pipeline/mlartifacts")
    print(f"AUC-ROC = {auc:.3f} | modelo registrado em {MODELO}")
