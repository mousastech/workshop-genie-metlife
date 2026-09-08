# Databricks notebook source
# MAGIC %md
# MAGIC # MetLife · Re-treino do modelo de fraude com FEEDBACK humano (fecha o ciclo MLOps)
# MAGIC Lê os rótulos confirmados na investigação (Lakebase `feedback`), corrige os labels do Gold,
# MAGIC re-treina (sklearn) e registra nova versão no UC; opcionalmente aponta o endpoint para a nova versão.

# COMMAND ----------
import os, uuid, requests, mlflow
from mlflow.models.signature import infer_signature
from databricks.sdk.core import Config
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

cfg = Config()
INSTANCE = "metlife-omnipulse-db"; HOST = "ep-floral-meadow-d85rz2wi.database.us-east-2.cloud.databricks.com"
MODELO = "moi_ai_catalog.metlife_pipeline.modelo_fraude_serving"
ENDPOINT = "metlife-fraude"
mlflow.set_registry_uri("databricks-uc")

# 1) feedback humano do Lakebase (via token OAuth)
import psycopg
tok = requests.post(f"{cfg.host}/api/2.0/database/credentials", headers=cfg.authenticate(),
                    json={"request_id": str(uuid.uuid4()), "instance_names":[INSTANCE]}, timeout=30).json()["token"]
email = requests.get(f"{cfg.host}/api/2.0/preview/scim/v2/Me", headers=cfg.authenticate()).json().get("userName")
with psycopg.connect(host=HOST, port=5432, dbname="omnipulse", user=email, password=tok, sslmode="require") as c, c.cursor() as cur:
    cur.execute("SELECT referencia, label FROM feedback")
    fb = {r[0]: int(r[1]) for r in cur.fetchall()}
print(f"Rótulos de feedback recebidos: {len(fb)}")

# 2) Gold + correção de rótulos (feedback humano tem prioridade sobre a heurística)
pdf = (spark.table("moi_ai_catalog.metlife_pipeline.gold_sinistros")
       .select("numero_sinistro","tipo_sinistro","linha_negocio","regiao",
               "valor_reclamado","dias_liquidacao","dias_desde_emissao","suspeita_fraude")
       .toPandas())
for c in ["valor_reclamado","dias_liquidacao","dias_desde_emissao"]:
    pdf[c] = pdf[c].astype(float).fillna(0.0)
for c in ["tipo_sinistro","linha_negocio","regiao"]:
    pdf[c] = pdf[c].fillna("NA")
pdf["label"] = pdf.apply(lambda r: fb.get(r["numero_sinistro"], int(bool(r["suspeita_fraude"]))), axis=1)
corrigidos = sum(1 for _,r in pdf.iterrows() if r["numero_sinistro"] in fb)
print(f"Linhas com rótulo corrigido pelo feedback: {corrigidos}")

feat = ["tipo_sinistro","linha_negocio","regiao","valor_reclamado","dias_liquidacao","dias_desde_emissao"]
X, y = pdf[feat], pdf["label"]
pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), ["tipo_sinistro","linha_negocio","regiao"])], remainder="passthrough")
clf = Pipeline([("pre", pre), ("lr", LogisticRegression(max_iter=1000, class_weight="balanced"))])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 3) re-treina + registra nova versão
with mlflow.start_run(run_name="fraude_retreino_feedback"):
    clf.fit(Xtr, ytr)
    auc = roc_auc_score(yte, clf.predict_proba(Xte)[:,1])
    mlflow.log_metric("auc_roc", auc); mlflow.log_metric("n_feedback", len(fb))
    sig = infer_signature(Xte.head(50), clf.predict(Xte.head(50)))
    info = mlflow.sklearn.log_model(clf, "model", signature=sig, input_example=Xte.head(2), registered_model_name=MODELO)
    print(f"AUC-ROC={auc:.3f} | nova versão registrada")

# 4) alias champion na nova versão (deploy/swap do endpoint é opcional, zero-downtime)
from mlflow.tracking import MlflowClient
mc = MlflowClient(registry_uri="databricks-uc")
v = max(int(m.version) for m in mc.search_model_versions(f"name='{MODELO}'"))
mc.set_registered_model_alias(MODELO, "champion", v)
print(f"Modelo {MODELO} v{v} marcado como @champion. Endpoint {ENDPOINT} pode ser atualizado p/ esta versão (zero-downtime).")
