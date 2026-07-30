# Dev Container para OpenData

Esta configuración permite abrir el proyecto en VS Code con un entorno Python listo para trabajar y con acceso a Docker desde dentro del contenedor.

## Requisitos

- Docker instalado en el host
- Extensión Dev Containers en VS Code

## Uso

1. Abre la carpeta del proyecto en VS Code.
2. Instala la extensión Dev Containers.
3. Ejecuta "Dev Containers: Rebuild and Reopen in Container".
4. Una vez dentro del contenedor, puedes probar el proyecto con:

```bash
docker ps
docker compose -f docker/docker-compose.lite.yml up -d
```

## Servicios recomendados para probar

Para recursos limitados, usa la configuración ligera:

```bash
cd /workspaces/opendata/docker
docker compose -f docker-compose.lite.yml up -d
```

## Próximos pasos

- Crear tablas Iceberg
- Ingestar datos de prueba
- Revisar resultados en Spark o MinIO
