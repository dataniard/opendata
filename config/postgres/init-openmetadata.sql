-- Gobierno del dato: rol y bases de datos para OpenMetadata.
--
-- Crea (de forma idempotente) el rol `openmetadata` y las BBDD que usan
-- el servidor de OpenMetadata y su servicio de ingestión (Airflow
-- standalone). Se ejecuta automáticamente SOLO en el primer arranque
-- (cuando se inicializa el volumen postgres_data).
--
-- IMPORTANTE: la contraseña está duplicada en `docker/.env`
-- (OPENMETADATA_DB_PASSWORD). Si la cambias allí, actualízala también
-- aquí antes del primer `docker compose up` (o ejecuta ALTER ROLE
-- manualmente en un despliegue existente):
--   ALTER ROLE openmetadata WITH LOGIN PASSWORD 'nueva-clave';
--
-- OpenMetadata necesita PostgreSQL 12+ (este stack usa PostgreSQL 15).

-- Rol de aplicación para OpenMetadata (server + ingestion)
SELECT 'CREATE ROLE openmetadata WITH LOGIN PASSWORD ''changeme-om123!'''
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'openmetadata')\gexec

-- Base de datos del servidor OpenMetadata (catálogo, glosario, linaje)
SELECT 'CREATE DATABASE openmetadata_db OWNER openmetadata'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'openmetadata_db')\gexec

-- Base de datos del Airflow interno de OpenMetadata Ingestion
SELECT 'CREATE DATABASE openmetadata_ingestion_db OWNER openmetadata'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'openmetadata_ingestion_db')\gexec

-- Privilegios sobre ambas BBDD
GRANT ALL PRIVILEGES ON DATABASE openmetadata_db TO openmetadata;
GRANT ALL PRIVILEGES ON DATABASE openmetadata_ingestion_db TO openmetadata;
