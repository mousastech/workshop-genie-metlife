"""
MetLife OmniPulse AI — Databricks App (FastAPI + React).
3 módulos: Fast-Claims (Módulo 1), Churn Shield (Módulo 2), BrokerX Copilot (Módulo 3).
Dados: Gold (SQL warehouse) · Score de fraude: Model Serving (metlife-fraude) ·
Transacional/decisões: Lakebase (Postgres) — best-effort. WhatsApp: fase 2 (documentado).
"""
import os, json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from databricks import sql as dbsql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

app = FastAPI(title="MetLife OmniPulse AI")
cfg = Config()
WAREHOUSE = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
SCHEMA = os.environ.get("GOLD_SCHEMA", "moi_ai_catalog.metlife_pipeline")
ENDPOINT = os.environ.get("SERVING_ENDPOINT", "metlife-fraude")
GENIE_URL = os.environ.get("GENIE_URL", "")

def q(sql_text):
    with dbsql.connect(server_hostname=cfg.host.replace("https://", ""),
                       http_path=f"/sql/1.0/warehouses/{WAREHOUSE}",
                       credentials_provider=lambda: cfg.authenticate) as c:
        with c.cursor() as cur:
            cur.execute(sql_text)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

# ---------- KPIs (BrokerX / visão geral) ----------
@app.get("/api/kpis")
def kpis():
    try:
        r = q(f"""
          SELECT
            (SELECT COUNT(*) FROM {SCHEMA}.gold_apolices WHERE status_apolice='Ativa') AS apolices_ativas,
            (SELECT ROUND(SUM(premio_mensal),0) FROM {SCHEMA}.gold_apolices WHERE status_apolice='Ativa') AS premio_mensal,
            (SELECT ROUND(100.0*SUM(CASE WHEN status_pagamento='Inadimplente' THEN 1 ELSE 0 END)/COUNT(*),1) FROM {SCHEMA}.gold_premios) AS inadimplencia,
            (SELECT COUNT(*) FROM {SCHEMA}.gold_sinistros WHERE suspeita_fraude) AS sinistros_suspeitos,
            (SELECT ROUND(AVG(dias_liquidacao),0) FROM {SCHEMA}.gold_sinistros WHERE dias_liquidacao IS NOT NULL) AS dias_liquidacao
        """)[0]
        return r
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- Módulo 1: Fast-Claims (fila de triagem de fraude) ----------
@app.get("/api/claims")
def claims():
    try:
        return q(f"""
          SELECT s.numero_sinistro, s.tipo_sinistro, s.linha_negocio, s.regiao,
                 s.valor_reclamado, s.dias_liquidacao, s.dias_desde_emissao,
                 f.score_fraude, f.nivel_risco, f.motivo_alerta_principal
          FROM {SCHEMA}.gold_sinistros s
          JOIN {SCHEMA}.gold_fraude_score f USING (sinistro_id)
          WHERE f.nivel_risco='Alto'
          ORDER BY f.score_fraude DESC, s.valor_reclamado DESC LIMIT 40
        """)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- Score ao vivo via Model Serving (AI Gateway) ----------
@app.post("/api/score")
def score(payload: dict):
    try:
        w = WorkspaceClient()
        resp = w.serving_endpoints.query(name=ENDPOINT, dataframe_records=[payload])
        return {"prediction": resp.predictions[0] if getattr(resp, "predictions", None) else resp.as_dict()}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- Módulo 2: Churn Shield (propensão a cancelamento) ----------
@app.get("/api/churn")
def churn():
    try:
        # score de churn = combinação de inadimplência + suspensão + baixo ticket (transparente)
        return q(f"""
          WITH pg AS (
            SELECT apolice_id,
                   SUM(CASE WHEN status_pagamento='Inadimplente' THEN 1 ELSE 0 END) AS inadimplentes,
                   COUNT(*) AS competencias
            FROM {SCHEMA}.gold_premios GROUP BY apolice_id)
          SELECT a.numero_apolice, a.linha_negocio, a.nome_produto, a.regiao, a.canal_distribuicao,
                 a.premio_mensal, a.status_apolice,
                 COALESCE(pg.inadimplentes,0) AS meses_inadimplente,
                 LEAST(100, ROUND(
                    100.0*COALESCE(pg.inadimplentes,0)/GREATEST(COALESCE(pg.competencias,1),1)*0.7
                    + (CASE WHEN a.status_apolice='Suspensa' THEN 30 ELSE 0 END)
                    + (CASE WHEN a.premio_mensal < 300 THEN 10 ELSE 0 END), 0)) AS score_churn
          FROM {SCHEMA}.gold_apolices a
          LEFT JOIN pg ON a.apolice_id=pg.apolice_id
          WHERE a.status_apolice IN ('Ativa','Suspensa')
          ORDER BY score_churn DESC LIMIT 40
        """)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- Módulo 3: BrokerX (mix carteira p/ gráficos) ----------
@app.get("/api/portfolio")
def portfolio():
    try:
        regiao = q(f"SELECT regiao, ROUND(SUM(premio_mensal),0) AS premio FROM {SCHEMA}.gold_apolices WHERE status_apolice='Ativa' GROUP BY regiao ORDER BY premio DESC")
        linha = q(f"SELECT linha_negocio, COUNT(*) AS apolices FROM {SCHEMA}.gold_apolices WHERE status_apolice='Ativa' GROUP BY linha_negocio")
        return {"regiao": regiao, "linha": linha, "genie_url": GENIE_URL}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- Ação/decisão (grava no Lakebase se disponível; senão eco) ----------
@app.post("/api/action")
def action(payload: dict):
    try:
        import psycopg
        conn = psycopg.connect()  # usa PGHOST/PGUSER/PGPASSWORD/PGDATABASE do recurso Lakebase
        with conn, conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS decisions(
                id serial PRIMARY KEY, modulo text, referencia text, acao text,
                detalhe jsonb, criado_em timestamptz DEFAULT now())""")
            cur.execute("INSERT INTO decisions(modulo, referencia, acao, detalhe) VALUES(%s,%s,%s,%s)",
                        (payload.get("modulo"), payload.get("referencia"), payload.get("acao"),
                         json.dumps(payload.get("detalhe", {}))))
        return {"status": "gravado_no_lakebase"}
    except Exception as e:
        return {"status": "registrado_local", "nota": "Lakebase indisponível no runtime", "erro": str(e)[:120]}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
