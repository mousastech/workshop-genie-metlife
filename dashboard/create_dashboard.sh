#!/usr/bin/env bash
# Cria e publica o dashboard AI/BI de referencia sobre os Metric Views.
# Pre-requisitos: Databricks CLI autenticado, warehouse e os Metric Views ja criados.
#
# Uso:
#   PROFILE=fevm-moi-ai WAREHOUSE_ID=xxxx PARENT=/Workspace/Users/voce@empresa.com/dashboards \
#     bash dashboard/create_dashboard.sh
set -euo pipefail

PROFILE="${PROFILE:?defina PROFILE}"
WAREHOUSE_ID="${WAREHOUSE_ID:?defina WAREHOUSE_ID}"
PARENT="${PARENT:?defina PARENT (ex: /Workspace/Users/voce@empresa.com/dashboards)}"
CATALOG="${CATALOG:-moi_ai_catalog}"
SCHEMA="${SCHEMA:-metlife_workshop}"
HERE="$(cd "$(dirname "$0")" && pwd)"

databricks workspace mkdirs "$PARENT" --profile "$PROFILE" || true

# IMPORTANTE: sempre passe --profile, senao a CLI cai no profile DEFAULT.
DASHBOARD_ID=$(databricks lakeview create \
  --display-name "MetLife - Painel de Seguros (Workshop)" \
  --warehouse-id "$WAREHOUSE_ID" \
  --dataset-catalog "$CATALOG" \
  --dataset-schema "$SCHEMA" \
  --serialized-dashboard "$(cat "$HERE/dashboard.json")" \
  --json "{\"parent_path\": \"$PARENT\"}" \
  --profile "$PROFILE" \
  -o json | jq -r '.dashboard_id')

echo "DASHBOARD_ID=$DASHBOARD_ID"
databricks lakeview publish "$DASHBOARD_ID" --warehouse-id "$WAREHOUSE_ID" --profile "$PROFILE"
echo "Publicado. Link: <host>/sql/dashboardsv3/$DASHBOARD_ID/published"
