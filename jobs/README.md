# Orquestração (Lakeflow Jobs) — Sessão 1

`metlife_orquestracao_medallion.job.json` orquestra o medalhão de ponta a ponta e mantém o **dashboard sincronizado** com os dados:

```
                              ┌→ [treinar_modelo_fraude]  (notebook_task · Spark MLlib + MLflow → UC Registry)
[pipeline_bronze_silver_gold] ┤
   (Lakeflow Declarative Pipe)└→ [refresh_dashboard_aibi] (dashboard_task — AI/BI)
```

- **Task 1 · `pipeline_task`** — dispara o Declarative Pipeline (`pipelines/metlife_medallion.sql`): Bronze → Silver → Gold.
- **Task 2 · `notebook_task`** (`treinar_modelo_fraude`, depende da 1) — re-treina o modelo de **propensão a fraude** (GBT, Spark MLlib), registrando em `moi_ai_catalog.metlife_pipeline.modelo_fraude` (Unity Catalog Model Registry). Notebook: `notebooks/metlife_ml_fraude_treino.py`.
- **Task 3 · `dashboard_task`** (depende da 1) — atualiza o **dashboard AI/BI** (Lakeview) com o Gold recém-processado.
- **Agenda** — cron diário 06h America/Sao_Paulo, criado **PAUSED** (troque para `UNPAUSED` para ativar). Também suporta gatilhos por *file arrival* no Volume de landing ou *table update*.

> `dashboard_task` é para dashboards **AI/BI (Lakeview)**. Para dashboards SQL legados use `sql_task.dashboard`.

## Deploy (CLI)
Substitua os placeholders (`<PIPELINE_ID>`, `<DASHBOARD_ID>`, `<WAREHOUSE_ID>`) e:
```bash
databricks jobs create --json @jobs/metlife_orquestracao_medallion.job.json --profile <perfil>
databricks jobs run-now <JOB_ID> --profile <perfil>       # executa on-demand
databricks jobs get-run --run-id <RUN_ID> --profile <perfil>
```

## Landing dos dados brutos (fonte do Auto Loader)
O pipeline lê CSVs de `/Volumes/moi_ai_catalog/metlife_medallion/landing/<origem>`. Para simular a extração das origens:
```sql
INSERT OVERWRITE DIRECTORY '/Volumes/moi_ai_catalog/metlife_medallion/landing/apolices'
USING CSV OPTIONS ('header'='true')
SELECT * FROM moi_ai_catalog.metlife_workshop.apolices;
-- repita para clientes, corretores, produtos, premios, sinistros, fraude_score
```

## Ambiente de referência (workshop 17/09, fevm-moi-ai)
- Pipeline `metlife_medallion`: `c8b22fb6-22a4-48b5-868e-c87dbcb45b8e` → publica em `moi_ai_catalog.metlife_pipeline`
- Job `metlife_orquestracao_medallion`: `93737767044104`
- Dashboard AI/BI: `01f1ab91baf51017b6a24adc9a23888e`
- Modelo UC: `moi_ai_catalog.metlife_pipeline.modelo_fraude` · Volume de artefatos ML: `metlife_pipeline.mlartifacts`

## Notas de ML (serverless)
Ao registrar modelos **SparkML** em serverless, o MLflow exige um `dfs_tmpdir` em UC Volume e uma **model signature** (`infer_signature`). Ver `notebooks/metlife_ml_fraude_treino.py`.
