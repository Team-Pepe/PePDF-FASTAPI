"""
scripts/db/reset_db.py

Script para resetear la base de datos completamente.
Elimina todos los datos y reinicializa las tablas.
Uso: uv run python -m scripts.db.reset_db
"""

import asyncio
import sys
from typing import Optional

from sqlalchemy import text

from app.core.database import engine
from app.models import Base


async def reset_database(interactive: bool = True) -> bool:
    """
    Resetea la base de datos completamente.
    Elimina todas las tablas y las recrea.

    Args:
        interactive: Si True, solicita confirmación

    Returns:
        bool: True si se reseteó exitosamente
    """
    print("=" * 60)
    print("⚠️  RESETEAR BASE DE DATOS COMPLETAMENTE")
    print("=" * 60)

    if interactive:
        print("\n🔴 ADVERTENCIA: Esto eliminará TODOS los datos")
        response = input("¿Estás seguro? (escribe 'si confirmó' para continuar): ")
        if response != "si confirmó":
            print("❌ Cancelado")
            return False

    try:
        print("\n⏳ Eliminando todas las tablas...")
        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
        print("✅ Tablas eliminadas")

        print("\n⏳ Recreando todas las tablas...")
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tablas recreadas")

        print("\n✅ Base de datos reseteada exitosamente")
        return True

    except Exception as e:
        print(f"\n❌ Error al resetear BD: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


async def main() -> int:
    """Punto de entrada principal."""
    success = await reset_database(interactive=True)
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
