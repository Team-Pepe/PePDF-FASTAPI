# PePDF-FASTAPI - Documentación del Proyecto

## ⚠️ IMPORTANTE: Uso Obligatorio de `uv`

**SIEMPRE** usa `uv` en lugar de `pip` para todas las operaciones.

### Comandos permitidos:

```bash
# Instalar dependencias
uv add <paquete>
uv add -D <paquete>  # dev dependencies

# Instalar desde pyproject.toml
uv sync

# Ejecutar scripts
uv run <comando>

# Desarrollo
uv run fastapi dev

# Crear entorno virtual (si no existe)
uv venv
```

### NUNCA uses:
- ❌ `pip install`
- ❌ `pip freeze > requirements.txt`
- ❌ `python -m pip install`

---

## Estructura del Proyecto

```
PePDF-FASTAPI/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point de FastAPI
│   ├── database.py             # Conexión a la base de datos (SQLAlchemy)
│   ├── config.py                # Configuración y variables de entorno
│   ├── models/                 # Modelos de la base de datos (ORM)
│   │   └── __init__.py
│   ├── schemas/                # Modelos Pydantic (request/response)
│   │   └── __init__.py
│   ├── core/                   # Configuración centralizada
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, hashing de contraseñas
│   │   └── deps.py             # Dependencias globales (get_db, get_current_user)
│   └── modules/                # Lógica por feature (simétrico con frontend Astro)
│       ├── __init__.py
│       ├── auth/               # Autenticación
│       │   ├── __init__.py
│       │   ├── routes.py       # Endpoints: /api/auth/login, /api/auth/register
│       │   ├── schemas.py      # Pydantic: LoginRequest, RegisterRequest, Token
│       │   ├── services.py    # Lógica de negocio (crear usuario, verificar password)
│       │   └── repositories.py # CRUD con SQLAlchemy
│       └── tools-suites/             # Herramientas PDF
│           ├── __init__.py
│           ├── convert/
│           ├── protect/
│           └── pdf-tools/
├── .env                        # Variables de entorno (NUNCA commitear)
├── pyproject.toml              # Dependencias del proyecto
├── uv.lock                     # Lock de dependencias
└── README.md
```

---

## Simetría con Frontend (PePDF-ASTRO)

La estructura del backend debe ser **simétrica** con el frontend para mantener coherencia:

| Frontend (Astro) | Backend (FastAPI) |
|------------------|-------------------|
| `src/components/auth/` | `app/modules/auth/` |
| `src/components/tools/` | `app/modules/tools/` |
| `src/components/home/` | `app/modules/home/` |
| `src/pages/login/` | `/api/auth/login` |
| `src/pages/register/` | `/api/auth/register` |
| `src/pages/pdf-tools/` | `/api/tools/pdf-tools` |

---

## Reglas de Arquitectura

### 1. Arquitectura Modular por Feature

Cada módulo en `app/modules/` debe contener:
- `routes.py` - Endpoints HTTP
- `schemas.py` - Pydantic models (request/response)
- `services.py` - Lógica de negocio
- `repositories.py` - Acceso a la base de datos

### 2. Separación de Responsabilidades

```
routes.py     → Solo recibe requests y devuelve responses
services.py   → Lógica de negocio (no accede a DB directamente)
repositories.py → Solo acceso a la base de datos
schemas.py    → Solo validación y serialización de datos
```

El versionado se agregará cuando:
- Se lance el producto públicamente
- Existan clientes externos
- Se necesiten cambios breaking

---

## Dependencias Requeridas

Agregar al `pyproject.toml` usando `uv add`:

```bash
uv add sqlalchemy[asyncio] asyncpg alembic
uv add python-jose[cryptography] passlib[bcrypt] python-multipart
uv add pydantic-settings
```

---

## Patrón de Importación

```python
# ✅ Correcto
from app.modules.auth.schemas import UserCreate
from app.modules.auth.services import AuthService
from app.core.deps import get_db

# ❌ Evitar
from app.services import algo  # services plano
from app.models import User     # modelos sueltos
```

---

## Cómo Crear un Nuevo Módulo

1. Crear carpeta en `app/modules/<nombre>/`
2. Crear `__init__.py`
3. Crear `routes.py` con APIRouter
4. Crear `schemas.py` con Pydantic models
5. Crear `services.py` con lógica de negocio
6. Crear `repositories.py` con CRUD
7. Importar en `app/main.py`

### Ejemplo de estructura:

```
├── modules/
│   └── users/
│       ├── __init__.py
│       ├── routers/
│       │   └── users.py
│       ├── services/
│       │   └── users.py
│       └── repositories/
│           └── users.py

```

---

## Comandos de Desarrollo

```bash
# Iniciar servidor de desarrollo
uv run fastapi dev

# Verificar tipos
uv run ruff check app/

# Formatear código
uv run ruff format app/
```

---

## Base de Datos

- **ORM**: SQLAlchemy 2.0 (async)
- **Migraciones**: Alembic
- **DRIVER**: asyncpg (PostgreSQL)

---

## Autenticación

- **JWT**: python-jose
- **Password Hashing**: passlib + bcrypt
- **Tipo**: Bearer token en headers

---

## Notas Adicionales

1. **NUNCA** hacer commit de `.env` o archivos con secretos
2. **SIEMPRE** usar `uv` para gestión de dependencias
3. **MANTENER** la simetría con el frontend
4. **NO** mezclar lógica de negocio en las rutas
5. **USAR** type hints en todas las funciones
