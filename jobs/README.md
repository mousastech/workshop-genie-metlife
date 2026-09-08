# Orquestração (Lakeflow Jobs) — Sessão 1

`metlife_orquestracao_medallion.job.json` orquestra o medalhão de ponta a ponta e mantém o **dashboard sincronizado** com os dados:

```
[pipeline_bronze_silver_gold]  →  [refresh_dashboard_aibi]
   (Lakeflow Declarative Pipeline)     (dashboard_task — AI/BI)
```

- **Task 1 · `pipeline_task`** — dispara o Declarative Pipeline (`pipelines/metlife_medallion.sql`), que atualiza Bronze → Silver → Gold.
- **Task 2 · `dashboard_task`** — atualiza o **dashboard AI/BI** (Lakeview) assim que a task 1 conclui (`depends_on`), garantindo que o painel reflita o Gold recém-processado.
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
