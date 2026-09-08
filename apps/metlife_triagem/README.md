# Databricks App — Triagem de Sinistros (MetLife)

App FastAPI publicada **dentro do Databricks** (Databricks Apps). Lê o Gold do pipeline
(`metlife_pipeline.gold_sinistros` + score de fraude) e prioriza os sinistros de maior
risco para investigação. Identidade/permissões via Unity Catalog.

## Deploy
```bash
databricks apps create metlife-triagem --profile <perfil>
databricks sync ./apps/metlife_triagem "/Workspace/Users/<voce>/metlife_triagem" --profile <perfil>
databricks apps deploy metlife-triagem \
  --source-code-path "/Workspace/Users/<voce>/metlife_triagem" --profile <perfil>
```

## Governança de IA com AI Gateway
Quando o app (ou o Genie) consome LLMs/modelos via **Model Serving**, configure o **AI Gateway** no endpoint:
- **Rate limits** por usuário/endpoint e **usage tracking** (custo por consumo).
- **Inference tables** (payload logging) para auditoria.
- **Guardrails** (PII/tópicos) e **fallbacks** entre modelos.

Ex.: publicar o modelo de fraude (`moi_ai_catalog.metlife_pipeline.modelo_fraude`) como endpoint
`metlife-fraude` e aplicar AI Gateway — o app passa a consumir sob governança.

## Ambiente de referência (ao vivo, fevm-moi-ai)
- App: **metlife-triagem** — https://metlife-triagem-7474658545709121.aws.databricksapps.com (RUNNING)
- Endpoint de Model Serving (modelo sklearn servível): **metlife-fraude** com **AI Gateway** (rate limit 60/min + inference tables `metlife_pipeline.fraude_ep_*` + usage tracking)
- Modelo servível: `moi_ai_catalog.metlife_pipeline.modelo_fraude_serving` (Regressão Logística; GBT SparkML não é servível em Model Serving)
