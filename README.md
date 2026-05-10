# 📊 OpenData - Entorno de Analítica de Datos Abierto

## Descripción

Repositorio dedicado a almacenar información, configuraciones y documentación para construir un **entorno integrado de analítica de datos** utilizando exclusivamente herramientas y tecnologías de código abierto.

Este proyecto proporciona una alternativa completa y accesible a plataformas comerciales de analítica, permitiendo el máximo control, personalización y escalabilidad sin costos de licencia.

---

## 🎯 Objetivos

- **Documentar** tecnologías open-source para analítica de datos
- **Proporcionar** guías de instalación y configuración
- **Facilitar** la integración de múltiples herramientas especializadas
- **Democratizar** el acceso a infraestructura de datos de clase empresarial
- **Crear** una referencia reutilizable para proyectos similares

---

## 🛠️ Stack Tecnológico (Alternativas Abiertas)

Este repositorio cubre:

### Almacenamiento y Bases de Datos
- PostgreSQL / TimescaleDB
- ClickHouse
- Apache Spark

### Orquestación y ETL
- Apache Airflow
- dbt (data build tool)
- Meltano

### Visualización y BI
- Apache Superset
- Metabase
- Grafana

### Análisis y Datos
- Jupyter Notebook
- RStudio
- Apache Zeppelin

### Infraestructura
- Docker & Docker Compose
- Kubernetes (opcional)
- MinIO (almacenamiento de objetos)

---

## 📂 Estructura del Repositorio

```
opendata/
├── doc/                    # Documentación del proyecto
│   ├── 01_SPECS.md        # Especificaciones técnicas
│   └── 02_PLAN.md         # Plan de ejecución
├── 00_PROMPTS/            # Configuración de prompts
├── docker/                # Configuraciones Docker
│   ├── docker-compose.yml # Orquestación completa
│   └── .env               # Variables de entorno
├── config/                # Archivos de configuración
│   ├── spark/             # Configuración Spark + Iceberg
│   ├── trino/             # Configuración Trino
│   └── postgres/          # Scripts de inicialización
├── scripts/               # Scripts de utilidad
│   ├── init-buckets.sh    # Inicializar buckets MinIO
│   ├── create_iceberg_tables.py      # Crear tablas
│   └── ingest_bronze_data.py         # Ingestar datos
├── QUICKSTART.md          # Guía de inicio rápido
└── README.md              # Este archivo
```

---

## 🚀 Inicio Rápido

Para comenzar inmediatamente, consulta la guía [QUICKSTART.md](QUICKSTART.md) que incluye:

- ✅ Despliegue con Docker Compose
- ✅ Creación de tablas Iceberg
- ✅ Ingestión de datos de prueba
- ✅ Consultas y visualización

### Comandos principales

```bash
# 1. Iniciar servicios
cd docker
docker compose up -d

# 2. Crear tablas Iceberg
docker compose exec spark-master spark-submit /scripts/create_iceberg_tables.py

# 3. Ingestar datos
docker compose exec spark-master spark-submit /scripts/ingest_bronze_data.py

# 4. Acceder a MinIO UI
# http://localhost:9001

# 5. Acceder a Spark Master
# http://localhost:8080
```

---

## � Documentación Completa

### 🚀 Para Comenzar
- **[QUICKSTART.md](QUICKSTART.md)** - Guía paso a paso para desplegar todo en 30 minutos

### 📋 Especificaciones y Arquitectura
- **[01_SPECS.md](doc/01_SPECS.md)** - Especificaciones técnicas del stack
- **[02_PLAN.md](doc/02_PLAN.md)** - Plan de implementación en 7 fases
- **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** - Diagramas visuales completos
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Resumen de todo lo implementado

### ⚙️ Archivos de Configuración
- **[docker-compose.yml](docker/docker-compose.yml)** - Orquestación de 10 servicios
- **[spark-defaults.conf](config/spark/spark-defaults.conf)** - Spark + Iceberg
- **[iceberg.properties](config/trino/catalog/iceberg.properties)** - Trino
- **[init.sql](config/postgres/init.sql)** - PostgreSQL + auditoría

### 🔧 Scripts de Utilidad
- **[init-buckets.sh](scripts/init-buckets.sh)** - Crear buckets MinIO
- **[create_iceberg_tables.py](scripts/create_iceberg_tables.py)** - Crear tablas
- **[ingest_bronze_data.py](scripts/ingest_bronze_data.py)** - Ingestar datos
- **[transform_silver_data.py](scripts/transform_silver_data.py)** - Transformar datos
- **[aggregate_gold_data.py](scripts/aggregate_gold_data.py)** - Agregar datos

---

## 📄 Licencia

Este repositorio almacena información y configuraciones de tecnologías open-source. 
Cada herramienta mantiene su propia licencia.

---

**Última actualización:** Abril 2026