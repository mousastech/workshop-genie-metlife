#!/usr/bin/env bash
# Cria os dois Genie Spaces do workshop a partir dos JSONs serializados.
# Pre-requisitos: Databricks CLI autenticado e um SQL warehouse.
#
# Uso:
#   PROFILE=fevm-moi-ai WAREHOUSE_ID=xxxx PARENT=/Workspace/Users/voce@empresa.com/genie_spaces \
#     bash genie/create_genie_spaces.sh
set -euo pipefail

PROFILE="${PROFILE:?defina PROFILE}"
WAREHOUSE_ID="${WAREHOUSE_ID:?defina WAREHOUSE_ID}"
PARENT="${PARENT:?defina PARENT (ex: /Workspace/Users/voce@empresa.com/genie_spaces)}"
HERE="$(cd "$(dirname "$0")" && pwd)"

databricks workspace mkdirs "$PARENT" --profile "$PROFILE" || true

echo "== Genie Space 1: tabelas (exploracao) =="
databricks genie create-space --profile "$PROFILE" --json "{
  \"warehouse_id\": \"$WAREHOUSE_ID\",
  \"title\": \"MetLife - Seguros, Sinistros e Distribuicao\",
  \"description\": \"Genie sobre as tabelas cruas do dominio Seguros MetLife (exploracao e laboratorio).\",
  \"parent_path\": \"$PARENT\",
  \"serialized_space\": $(jq -c '.' "$HERE/genie_space_tabelas.json" | jq -Rs '.')
}"

echo "== Genie Space 2: camada semantica (Metric Views) =="
databricks genie create-space --profile "$PROFILE" --json "{
  \"warehouse_id\": \"$WAREHOUSE_ID\",
  \"title\": \"MetLife - Camada Semantica\",
  \"description\": \"Genie sobre a camada semantica governada (Metric Views). Base do Genie Ontology.\",
  \"parent_path\": \"$PARENT\",
  \"serialized_space\": $(jq -c '.' "$HERE/genie_space_camada_semantica.json" | jq -Rs '.')
}"

echo "OK - copie os space_id retornados acima."
