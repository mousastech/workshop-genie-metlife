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
