# Pipeline medalhão (Lakeflow Declarative Pipeline) — Sessão 1

`metlife_medallion.sql` é a versão **produtiva** do medalhão da Sessão 1: Bronze (Auto Loader) → Silver (com *expectations* de qualidade) → Gold (dimensões e fatos), publicando em `moi_ai_catalog.metlife_medallion`. O Gold é o formato que a **Sessão 2** consome.

> Para a aula guiada e executável célula a célula, use o notebook `notebooks/metlife_workshop_class_sessao1_dataeng.py` (constrói o mesmo medalhão em SQL batch). Este pipeline é a forma orquestrada/produtiva.

## Pré-requisitos
- Volume de landing com os CSVs das origens:
  `/Volumes/moi_ai_catalog/metlife_medallion/landing/<origem>/` — origens: `clientes`, `corretores`, `produtos`, `apolices`, `premios`, `sinistros`, `fraude_score`.
- SQL warehouse / serverless e permissões de `CREATE` no schema alvo.

## Deploy — opção A: CLI (iteração rápida)
```bash
PROFILE=meu-profile
# 1) suba o arquivo SQL para o workspace
databricks workspace import-dir ./pipelines /Workspace/Users/voce@empresa.com/metlife_pipeline --overwrite --profile $PROFILE
# 2) crie o pipeline apontando para o arquivo (default catalog/schema = moi_ai_catalog/metlife_medallion)
databricks pipelines create --json '{
  "name": "metlife_medallion",
  "serverless": true,
  "catalog": "moi_ai_catalog",
  "schema": "metlife_medallion",
  "libraries": [{"file": {"path": "/Workspace/Users/voce@empresa.com/metlife_pipeline/metlife_medallion.sql"}}]
}' --profile $PROFILE
# 3) rode e acompanhe
databricks pipelines start-update <PIPELINE_ID> --profile $PROFILE
```

## Deploy — opção B: Asset Bundle (DAB)
Inclua um `resources/metlife_medallion.pipeline.yml` apontando para `pipelines/` e faça `databricks bundle deploy` + `databricks bundle run metlife_medallion`.

## Notas
- **Bronze** usa `STREAM read_files(...)` (Auto Loader) — ingestão incremental idempotente.
- **Silver** aplica `CONSTRAINT ... EXPECT (...)`; violações críticas usam `ON VIOLATION DROP ROW` (métricas de qualidade ficam no event log do pipeline).
- **Gold** preserva as dimensões que o negócio filtra (linha, canal, região, produto, tempo).
- Aplique as *tags* de Domain no Gold (veja `sql/14_domain_tags.sql`, adaptando o schema) para alinhar com a taxonomia da Sessão 2.
