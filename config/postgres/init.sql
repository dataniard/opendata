-- Inicialización de PostgreSQL para Hive Metastore y Auditoría

-- Crear extensión si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear base de datos de Airflow si no existe
DO
$do$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow') THEN
    CREATE DATABASE airflow;
  END IF;
END
$do$;

-- ==================== Tablas de Auditoría ====================

-- Tabla de operaciones en Iceberg
CREATE TABLE IF NOT EXISTS audit_operations (
  id BIGSERIAL PRIMARY KEY,
  table_namespace VARCHAR(255) NOT NULL,
  table_name VARCHAR(255) NOT NULL,
  operation_type VARCHAR(50) NOT NULL,
  snapshot_id BIGINT,
  committed_at TIMESTAMP NOT NULL,
  file_count INT DEFAULT 0,
  rows_affected BIGINT DEFAULT 0,
  metadata_changed BOOLEAN DEFAULT FALSE,
  user_id VARCHAR(255) DEFAULT 'system',
  operation_details JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de evolución de esquemas
CREATE TABLE IF NOT EXISTS schema_evolution (
  id BIGSERIAL PRIMARY KEY,
  table_namespace VARCHAR(255) NOT NULL,
  table_name VARCHAR(255) NOT NULL,
  schema_id INT,
  schema_json TEXT NOT NULL,
  change_type VARCHAR(50) NOT NULL,
  change_details TEXT,
  applied_at TIMESTAMP NOT NULL,
  applied_by VARCHAR(255) DEFAULT 'system',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de versionado de datos
CREATE TABLE IF NOT EXISTS data_snapshots (
  id BIGSERIAL PRIMARY KEY,
  table_namespace VARCHAR(255) NOT NULL,
  table_name VARCHAR(255) NOT NULL,
  snapshot_id BIGINT UNIQUE NOT NULL,
  parent_snapshot_id BIGINT,
  operation_type VARCHAR(50) NOT NULL,
  files_added INT DEFAULT 0,
  files_removed INT DEFAULT 0,
  files_modified INT DEFAULT 0,
  rows_added BIGINT DEFAULT 0,
  rows_deleted BIGINT DEFAULT 0,
  manifest_path VARCHAR(512),
  metadata_path VARCHAR(512),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ejecuciones de ETL
CREATE TABLE IF NOT EXISTS etl_executions (
  id BIGSERIAL PRIMARY KEY,
  job_name VARCHAR(255) NOT NULL,
  job_type VARCHAR(50) NOT NULL,
  source_namespace VARCHAR(255),
  source_table VARCHAR(255),
  target_namespace VARCHAR(255),
  target_table VARCHAR(255),
  status VARCHAR(50) NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  duration_seconds INT,
  rows_processed BIGINT DEFAULT 0,
  rows_failed BIGINT DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de calidad de datos
CREATE TABLE IF NOT EXISTS data_quality_checks (
  id BIGSERIAL PRIMARY KEY,
  table_namespace VARCHAR(255) NOT NULL,
  table_name VARCHAR(255) NOT NULL,
  check_name VARCHAR(255) NOT NULL,
  check_type VARCHAR(50) NOT NULL,
  check_query TEXT,
  expected_result VARCHAR(255),
  actual_result VARCHAR(255),
  passed BOOLEAN,
  run_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== Índices ====================

CREATE INDEX idx_audit_ops_table ON audit_operations(table_namespace, table_name, committed_at DESC);
CREATE INDEX idx_audit_ops_type ON audit_operations(operation_type, created_at DESC);
CREATE INDEX idx_schema_evo_table ON schema_evolution(table_namespace, table_name, applied_at DESC);
CREATE INDEX idx_snapshots_table ON data_snapshots(table_namespace, table_name, created_at DESC);
CREATE INDEX idx_etl_exec_status ON etl_executions(job_name, status, end_time DESC);
CREATE INDEX idx_etl_exec_target ON etl_executions(target_namespace, target_table, end_time DESC);
CREATE INDEX idx_quality_table ON data_quality_checks(table_namespace, table_name, run_at DESC);

-- ==================== Vistas ====================

-- Vista de operaciones recientes
CREATE OR REPLACE VIEW v_recent_operations AS
SELECT 
  ao.table_namespace,
  ao.table_name,
  ao.operation_type,
  ao.committed_at,
  ao.rows_affected,
  ao.file_count,
  ao.metadata_changed,
  ao.user_id
FROM audit_operations ao
ORDER BY ao.committed_at DESC
LIMIT 1000;

-- Vista de ejecuciones de ETL recientes
CREATE OR REPLACE VIEW v_recent_etl_executions AS
SELECT 
  ee.job_name,
  ee.job_type,
  ee.source_table,
  ee.target_table,
  ee.status,
  ee.start_time,
  ee.end_time,
  ee.duration_seconds,
  ee.rows_processed,
  ee.error_message
FROM etl_executions ee
ORDER BY ee.end_time DESC
LIMIT 500;

-- Vista de cambios de esquema recientes
CREATE OR REPLACE VIEW v_recent_schema_changes AS
SELECT 
  se.table_namespace,
  se.table_name,
  se.change_type,
  se.change_details,
  se.applied_at,
  se.applied_by
FROM schema_evolution se
ORDER BY se.applied_at DESC
LIMIT 1000;

-- ==================== Permisos ====================

-- Crear usuario para aplicaciones (opcional)
-- CREATE USER iceberg_user WITH PASSWORD 'iceberg_pass';
-- GRANT ALL PRIVILEGES ON TABLE audit_operations, schema_evolution, data_snapshots, etl_executions, data_quality_checks TO iceberg_user;
