# PePDF-FASTAPI 🔐

API REST para gestión de herramientas PDF con autenticación JWT.

## Quick Start

```bash
# 1. Instalar dependencias
uv sync

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración de BD

# 3. Ejecutar migraciones
uv run alembic upgrade head

# 4. Iniciar servidor
uv run fastapi dev
```

---

## Gestión de Dependencias

> **Importante:** Este proyecto usa [`uv`](https://github.com/astral-sh/uv) como gestor de paquetes.

```bash
# Agregar dependencia
uv add <paquete>

# Agregar dependencia de desarrollo
uv add -D <paquete>

# Instalar todas las dependencias
uv sync
```

### ❌ No uses:
- `pip install`
- `pip freeze`
- `python -m pip install`

---

## Scripts de Utilidad

Ubicación: `scripts/utils/`

### 🔑 test_jwt.py
Verifica que el módulo de autenticación JWT funciona correctamente.

```bash
uv run python -m scripts.utils.test_jwt
```

### 👤 check_user.py
Busca un usuario en la base de datos y muestra sus datos.

```bash
# Con email específico
uv run python -m scripts.utils.check_user admin@example.com

# Sin argumentos (usa default: admin@example.com)
uv run python -m scripts.utils.check_user
```

### 🔐 verify_hash.py
Verifica si la contraseña de un usuario coincide con su hash bcrypt.

```bash
uv run python -m scripts.utils.verify_hash <email> <password>

# Ejemplo
uv run python -m scripts.utils.verify_hash admin@example.com admin123
```

---

## Estructura del Proyecto

```
PePDF-FASTAPI/
├── app/
│   ├── main.py              # Entry point de FastAPI
│   ├── config.py            # Configuración (.env)
│   ├── database.py          # Conexión SQLAlchemy
│   ├── models/              # Modelos ORM
│   ├── schemas/             # Pydantic models
│   ├── core/                # Configuración centralizada
│   │   ├── security.py      # JWT y hashing
│   │   └── deps.py          # Dependencias globales
│   └── modules/             # Lógica por feature
│       ├── auth/            # Login, registro
│       └── pdf-tools/       # Herramientas PDF
├── scripts/utils/           # Scripts de debugging
├── alembic/                 # Migraciones
└── pyproject.toml           # Dependencias
```

---

## Arquitectura Modular

Cada módulo (`app/modules/<nombre>/`) sigue esta estructura:

| Archivo | Responsabilidad |
|---------|-----------------|
| `routes.py` | Endpoints HTTP |
| `schemas.py` | Validación request/response |
| `services.py` | Lógica de negocio |
| `repositories.py` | Acceso a base de datos |

### Reglas de Separación

```
routes.py     → Recibe requests → Devuelve responses
services.py   → Lógica de negocio
repositories.py → Solo SQLAlchemy
schemas.py    → Solo validación
```

---

## Tecnologías

| Categoría | Herramienta |
|-----------|-------------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Base de Datos | PostgreSQL + asyncpg |
| Migraciones | Alembic |
| Auth | JWT (python-jose) + bcrypt |
| Validadores | Pydantic v2 |

---

## Comandos de Desarrollo

```bash
# Iniciar servidor de desarrollo
uv run fastapi dev

# Verificar código (linting)
uv run ruff check app/

# Formatear código
uv run ruff format app/

# Crear migración
uv run alembic revision --autogenerate -m "descripción"
```

---

## Agregar un Nuevo Módulo

1. Crear carpeta `app/modules/<nombre>/`
2. Agregar archivos: `__init__.py`, `routes.py`, `schemas.py`, `services.py`, `repositories.py`
3. Importar en `app/main.py`

---

## Notas

- ⚠️ **Nunca** hacer commit de `.env`
- ✅ Usar `uv` para todas las operaciones de paquetes
- ✅ Mantener simetría con el frontend (PePDF-ASTRO)
- ✅ Usar type hints en todas las funciones
