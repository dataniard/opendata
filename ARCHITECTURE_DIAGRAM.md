# 🏗️ Arquitectura OpenData - Diagrama Completo

Visualización de la arquitectura del proyecto OpenData con Docker Compose, MinIO, Iceberg y arquitectura medallion.

---

## 📐 Diagrama General del Sistema

```mermaid
flowchart TD
    subgraph DOCKER["🐳 DOCKER COMPOSE ENVIRONMENT"]
        subgraph STORAGE["🗄️ STORAGE LAYER"]
            MinIO["MinIO S3<br/>(9000, 9001)<br/>• iceberg-data/<br/>  ├── bronze/<br/>  ├── silver/<br/>  └── gold/<br/>• warehouse/<br/>• logs/"]
            PostgreSQL["PostgreSQL DB<br/>(5432)<br/>• Hive Metastore<br/>• Audit Tables<br/>• Schema History<br/>• Quality Checks"]
        end

        subgraph METADATA["🎯 METADATA & ORCHESTRATION LAYER"]
            HiveMS["Hive Metastore Service<br/>(9083)<br/>• Namespace Management<br/>• Table Registry<br/>• Partition Management<br/>• Schema Evolution"]
        end

        subgraph PROCESSING["⚙️ PROCESSING LAYER"]
            subgraph Spark["Apache Spark Cluster"]
                Master["Spark Master<br/>(7077, 8080)<br/>• Catalogs<br/>• SQL Engine<br/>• DAG Scheduler"]
                Workers["Spark Workers x2<br/>(8081, 8082)<br/>• 2 CPU / 2GB each<br/>• Partition Processing<br/>• Shuffle Operations"]
            end
            Trino["Trino Query Engine<br/>(8888)<br/>• Interactive SQL<br/>• Iceberg Catalog<br/>• Query Federation<br/>• Cost-based Optimizer"]
        end

        subgraph VISUALIZATION["📊 VISUALIZATION LAYER"]
            Superset["Apache Superset<br/>(8088)<br/>• Dashboards<br/>• Charts & Visualizations<br/>• Data Exploration<br/>• BI Reports"]
        end
    end

    MinIO --> HiveMS
    PostgreSQL --> HiveMS
    HiveMS --> Master
    Master --> Workers
    Master --> Trino
    Trino --> Superset
```

---

## 🔄 Flujo de Datos - Arquitectura Medallion

```mermaid
flowchart TD
    A["📥 DATA SOURCES"]
    API["External APIs<br/>(REST/gRPC)"]
    DB["Databases<br/>(SQL)"]
    MQ["Message Queues<br/>(Kafka/etc)"]
    
    API --> INGEST["Spark Ingestor Job<br/>(ingest_bronze.py)"]
    DB --> INGEST
    MQ --> INGEST
    A --> INGEST
    
    INGEST --> BRONZE["🥉 BRONZE LAYER - Raw<br/>━━━━━━━━━━<br/>raw_events/<br/>  ├── data/<br/>  ├── metadata/<br/>  └── snapshots/<br/>raw_logs/<br/>  ├── data/<br/>  ├── metadata/<br/>  └── snapshots/<br/>━━━━━━━━━━<br/>Retention: 90-180 days<br/>Compression: Snappy<br/>No transformations<br/>Full audit trail"]
    
    BRONZE --> TRANS["Transform<br/>(dbt/Spark)"]
    BRONZE --> QUERY["Query<br/>(SQL)"]
    BRONZE --> QUALITY["Monitor Data Quality<br/>Checks"]
    
    TRANS --> SILVER["🥈 SILVER LAYER - Curated<br/>━━━━━━━━━━<br/>events/<br/>  ├── data/<br/>  ├── metadata/<br/>  └── snapshots/<br/>users/<br/>  ├── data/<br/>  ├── metadata/<br/>  └── snapshots/<br/>━━━━━━━━━━<br/>Retention: 1-2 years<br/>Compression: Snappy<br/>Cleaned & Validated<br/>Deduplication Applied<br/>Schema Evolution"]
    QUERY --> SILVER
    QUALITY --> SILVER
    
    SILVER --> AGG["Aggregate<br/>(Spark)"]
    SILVER --> ANALYTICS["Analytics<br/>Queries"]
    SILVER --> ML["Machine Learning<br/>Features"]
    
    AGG --> GOLD["🥇 GOLD LAYER - Serving<br/>━━━━━━━━━━<br/>daily_user_metrics/<br/>  ├── data/<br/>  ├── metadata/<br/>  └── snapshots/<br/>event_types_daily/<br/>  ├── data/<br/>  ├── metadata/<br/>  └── snapshots/<br/>━━━━━━━━━━<br/>Retention: 2-5 years<br/>Pre-aggregated<br/>Optimized for queries<br/>Ready for BI"]
    ANALYTICS --> GOLD
    ML --> GOLD
    
    GOLD --> DASH["Dashboards<br/>(Superset)"]
    GOLD --> REPORTS["Business Reports<br/>(SQL/Spark)"]
    GOLD --> APIS["APIs<br/>(REST/gRPC)"]
    
    DASH --> USERS["👥 END USERS<br/>(Analysts, Decision Makers)"]
    REPORTS --> USERS
    APIS --> USERS
```

---

## 🗂️ Estructura de Buckets MinIO

```
minio/
│
├── iceberg-data/  ◄─────────── Principal bucket para Iceberg
│   │
│   ├── bronze/    ◄─────────── Raw data layer
│   │   ├── raw_events/
│   │   │   ├── data/
│   │   │   │   ├── year=2026/
│   │   │   │   │   ├── month=5/
│   │   │   │   │   │   ├── day=1/
│   │   │   │   │   │   │   ├── 00000-0-*.parquet
│   │   │   │   │   │   │   └── ...
│   │   │   │   │   │   └── day=2/
│   │   │   │   │   └── month=6/
│   │   │   │   └── year=2027/
│   │   │   ├── metadata/
│   │   │   │   ├── 00000-*.avro
│   │   │   │   ├── 00001-*.avro
│   │   │   │   └── version-hint.txt
│   │   │   └── snapshots/
│   │   │       ├── snap-*.avro
│   │   │       └── ...
│   │   │
│   │   └── raw_logs/
│   │       ├── data/
│   │       ├── metadata/
│   │       └── snapshots/
│   │
│   ├── silver/    ◄─────────── Curated data layer
│   │   ├── events/
│   │   │   ├── data/
│   │   │   ├── metadata/
│   │   │   └── snapshots/
│   │   │
│   │   └── users/
│   │       ├── data/
│   │       ├── metadata/
│   │       └── snapshots/
│   │
│   └── gold/      ◄─────────── Serving/Analytics layer
│       ├── daily_user_metrics/
│       │   ├── data/
│       │   ├── metadata/
│       │   └── snapshots/
│       │
│       └── event_types_daily/
│           ├── data/
│           ├── metadata/
│           └── snapshots/
│
├── warehouse/     ◄─────────── Iceberg warehouse metadata
│   ├── 00000-*.avro
│   └── version-hint.txt
│
└── logs/          ◄─────────── Operation logs
    ├── etl/
    │   ├── 2026-05-10.log
    │   └── ...
    ├── queries/
    │   ├── 2026-05-10.log
    │   └── ...
    └── errors/
        ├── 2026-05-10.log
        └── ...
```

---

## 🔌 Puertos y Conexiones

```
┌────────────────────────────────────────────────────────────────┐
│              SERVICE PORTS & CONNECTIONS                       │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SERVICE           │ PORT(s) │ ACCESS              │ PURPOSE │
├─────────────────────────────────────────────────────────────┤
│ PostgreSQL        │ 5432   │ Internal only       │ DB      │
│ MinIO API         │ 9000   │ http://localhost    │ S3 API  │
│ MinIO UI          │ 9001   │ http://localhost    │ Web UI  │
│ Hive Metastore    │ 9083   │ Internal (Thrift)   │ Catalog │
│ Spark Master      │ 7077   │ Internal (Spark RPC)│ Cluster │
│ Spark Master UI   │ 8080   │ http://localhost    │ Web UI  │
│ Spark Worker 1    │ 8081   │ http://localhost    │ Web UI  │
│ Spark Worker 2    │ 8082   │ http://localhost    │ Web UI  │
│ Spark Driver      │ 4040   │ http://localhost    │ Job UI  │
│ Trino             │ 8888   │ http://localhost    │ Web UI  │
│ Superset          │ 8088   │ http://localhost    │ Web UI  │
└─────────────────────────────────────────────────────────────┘

Network Connectivity:
┌─────────────────────────────────────────┐
│        opendata-network (bridge)        │
├─────────────────────────────────────────┤
│                                         │
│  All containers can communicate via:   │
│  • hostname (service name)              │
│  • Internal DNS resolution              │
│  • No external network required         │
│  • Persistent volumes for data          │
│                                         │
└─────────────────────────────────────────┘
```

---

## 📋 Tabla de Componentes

```
┌────────────────────────────────────────────────────────────────────────┐
│ COMPONENT        │ IMAGE                    │ PURPOSE                  │
├────────────────────────────────────────────────────────────────────────┤
│ PostgreSQL       │ postgres:15-alpine       │ Hive Metastore DB       │
│ MinIO            │ minio/minio:latest       │ S3-compatible storage   │
│ Hive Metastore   │ bde2020/hive:2.3.9-*     │ Metadata catalog        │
│ Spark Master     │ bde2020/spark-master:*   │ Cluster orchestration   │
│ Spark Workers    │ bde2020/spark-worker:*   │ Data processing         │
│ Trino            │ trinodb/trino:latest     │ SQL query engine        │
│ Superset         │ apache/superset:latest   │ BI & visualization      │
│ MinIO Init       │ minio/mc:latest          │ Bucket provisioning     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Data Flow Security

```
┌─────────────────────────────────────────┐
│      Data & Access Control              │
├─────────────────────────────────────────┤
│                                         │
│  Storage:                               │
│  ├── MinIO: S3 credentials              │
│  ├── PostgreSQL: User/password          │
│  └── Iceberg: Schema enforcement        │
│                                         │
│  Audit:                                 │
│  ├── audit_operations table             │
│  ├── schema_evolution table             │
│  ├── data_snapshots table               │
│  └── etl_executions table               │
│                                         │
│  Compliance:                            │
│  ├── Full change tracking               │
│  ├── Snapshot history                   │
│  ├── Access logs                        │
│  └── Data lineage                       │
│                                         │
└─────────────────────────────────────────┘
```

---

**Documento**: Arquitectura OpenData  
**Versión**: 1.0  
**Actualización**: Mayo 2026
