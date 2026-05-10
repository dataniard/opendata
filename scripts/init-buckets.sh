#!/bin/bash

# Script de inicialización de buckets MinIO

set -e

MINIO_ENDPOINT=${MINIO_ENDPOINT:-http://localhost:9000}
MINIO_USER=${MINIO_USER:-minioadmin}
MINIO_PASS=${MINIO_PASS:-changeme123!}

echo "Configurando MinIO en: $MINIO_ENDPOINT"

# Configurar cliente MC
mc config host add minio $MINIO_ENDPOINT $MINIO_USER $MINIO_PASS --api S3v4

# Crear buckets si no existen
echo "Creando buckets..."
mc mb --ignore-existing minio/iceberg-data
mc mb --ignore-existing minio/warehouse
mc mb --ignore-existing minio/logs

# Crear prefijos para capas medallion
echo "Creando estructura de prefijos..."
mc put --recursive /dev/null minio/iceberg-data/bronze/
mc put --recursive /dev/null minio/iceberg-data/silver/
mc put --recursive /dev/null minio/iceberg-data/gold/

# Habilitar versionado
echo "Habilitando versionado..."
mc version enable minio/iceberg-data
mc version enable minio/warehouse

# Listar buckets
echo "Buckets creados:"
mc ls minio/

echo "✅ Inicialización de buckets completada"
