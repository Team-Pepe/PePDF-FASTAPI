# PePDF FastAPI

Servicio backend de PePDF construido con FastAPI y gestionado con `uv`.

## Docker en Produccion

El proyecto incluye un `Dockerfile` optimizado para produccion con estrategia multi-etapa:
- instala dependencias bloqueadas desde `uv.lock` usando `uv`
- reutiliza cache de capas copiando primero manifiestos
- ejecuta FastAPI con `uvicorn` en el puerto interno `8000`

### 1. Construir la imagen

Desde la raiz del proyecto:

```bash
docker build -t pepdf-fastapi:latest .
```

### 2. Ejecutar el contenedor

```bash
docker run -d --name pepdf-fastapi -p 8000:8000 pepdf-fastapi:latest
```

### 3. Validar funcionamiento

Verificar endpoint principal:

```bash
curl http://localhost:8000/
```

Respuesta esperada:

```json
{"Hello":"World"}
```

Verificar documentacion de API:

```bash
curl -I http://localhost:8000/docs
```

### 4. Revisar logs y detener

```bash
docker logs pepdf-fastapi
docker stop pepdf-fastapi
docker rm pepdf-fastapi
```

## Criterios de aceptacion cubiertos

- Dockerfile apto para produccion con imagen base ligera y comando de arranque estable.
- Dependencias instaladas desde `pyproject.toml` + `uv.lock` con `uv sync --frozen`.
- Flujo simple de build y run con comandos directos de Docker.
