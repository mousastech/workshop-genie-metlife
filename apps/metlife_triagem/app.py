"""
MetLife · App de Triagem de Sinistros (Databricks Apps)
Lê o Gold (metlife_pipeline.gold_sinistros + score de fraude) e lista os sinistros
de maior risco para priorizar investigação. Autenticação e governança via Unity Catalog.
O consumo de IA (Model Serving do modelo de fraude) é governado pelo AI Gateway.
"""
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from databricks import sql
from databricks.sdk.core import Config

app = FastAPI(title="MetLife · Triagem de Sinistros")
cfg = Config()  # usa a identidade do app (OAuth) no ambiente Databricks
WAREHOUSE = os.environ["DATABRICKS_WAREHOUSE_ID"]

QUERY = """
SELECT s.numero_sinistro, s.tipo_sinistro, s.linha_negocio, s.regiao,
       s.valor_reclamado, f.score_fraude, f.nivel_risco
FROM moi_ai_catalog.metlife_pipeline.gold_sinistros s
JOIN moi_ai_catalog.metlife_pipeline.gold_fraude_score f USING (sinistro_id)
WHERE f.nivel_risco = 'Alto'
ORDER BY f.score_fraude DESC, s.valor_reclamado DESC
LIMIT 25
"""

def fetch():
    with sql.connect(server_hostname=cfg.host.replace("https://", ""),
                     http_path=f"/sql/1.0/warehouses/{WAREHOUSE}",
                     credentials_provider=lambda: cfg.authenticate) as c:
        with c.cursor() as cur:
            cur.execute(QUERY)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

@app.get("/api/triagem")
def triagem():
    return {"itens": fetch()}

@app.get("/", response_class=HTMLResponse)
def home():
    rows = "".join(
        f"<tr><td>{r['numero_sinistro']}</td><td>{r['tipo_sinistro']}</td>"
        f"<td>{r['linha_negocio']}</td><td>{r['regiao']}</td>"
        f"<td>R$ {r['valor_reclamado']:,.2f}</td><td><b>{r['score_fraude']}</b></td>"
        f"<td>{r['nivel_risco']}</td></tr>" for r in fetch())
    return f"""<h2>MetLife · Fila de triagem de fraude (alto risco)</h2>
    <table border=1 cellpadding=6 style='border-collapse:collapse;font-family:sans-serif'>
    <tr><th>Sinistro</th><th>Tipo</th><th>Linha</th><th>Região</th>
        <th>Valor reclamado</th><th>Score</th><th>Risco</th></tr>{rows}</table>"""
