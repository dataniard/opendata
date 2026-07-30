#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILE="docker/docker-compose.yml"
SPARK_MASTER_SERVICE="spark-master"
SCRIPTS_PATH="/scripts"

function run_step() {
  local step_name="$1"
  local script_name="$2"

  echo
  echo "=========="
  echo "Ejecutando: $step_name"
  echo "=========="

  docker compose -f "$COMPOSE_FILE" exec -T "$SPARK_MASTER_SERVICE" spark-submit "$SCRIPTS_PATH/$script_name"
}

echo
echo "Iniciando pipeline ETL OpenData"

run_step "Crear tablas Iceberg" "create_iceberg_tables.py"
run_step "Ingestar datos a Bronze" "ingest_bronze_data.py"
run_step "Transformar Bronze a Silver" "transform_silver_data.py"
run_step "Agregar datos a Gold" "aggregate_gold_data.py"

echo
echo "✅ Pipeline ETL completado"
