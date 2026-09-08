# Databricks notebook source
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

mlflow.set_registry_uri("databricks-uc")
MODELO = "moi_ai_catalog.metlife_pipeline.modelo_fraude_serving"

pdf = (spark.table("moi_ai_catalog.metlife_pipeline.gold_sinistros")
       .select("tipo_sinistro","linha_negocio","regiao",
               "valor_reclamado","dias_liquidacao","dias_desde_emissao","suspeita_fraude")
       .toPandas().fillna(0))
for _c in ["valor_reclamado","dias_liquidacao","dias_desde_emissao"]:
    pdf[_c] = pdf[_c].astype(float)
y = pdf.pop("suspeita_fraude").astype(int)
X = pdf
cats = ["tipo_sinistro","linha_negocio","regiao"]
pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), cats)], remainder="passthrough")
clf = Pipeline([("pre", pre), ("lr", LogisticRegression(max_iter=1000, class_weight="balanced"))])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
with mlflow.start_run(run_name="fraude_sklearn"):
    clf.fit(Xtr, ytr)
    auc = roc_auc_score(yte, clf.predict_proba(Xte)[:, 1])
    mlflow.log_metric("auc_roc", auc)
    sig = infer_signature(Xte.head(50), clf.predict(Xte.head(50)))
    mlflow.sklearn.log_model(clf, "model", signature=sig, input_example=Xte.head(2),
                             registered_model_name=MODELO)
    print(f"AUC-ROC = {auc:.3f} | {MODELO}")
