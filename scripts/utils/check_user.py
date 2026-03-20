"""
scripts/utils/check_user.py

Script para verificar datos de un usuario en la base de datos.
Útil para debugging y validación.
Uso: uv run python -m scripts.utils.check_user [email]
"""

import asyncio
import sys
from typing import Optional

from sqlalchemy import select

from app.core.database import engine, async_session
from app.models import User


async def check_user(email: str) -> Optional[dict]:
    """
    Verifica datos de un usuario en la BD.

    Args:
        email: Email del usuario a buscar

    Returns:
        dict con datos del usuario o None si no existe
    """
    print("=" * 60)
    print("VERIFICACIÓN DE USUARIO EN BD")
    print("=" * 60)

    async with async_session() as session:
        try:
            # Query el usuario
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user:
                print(f"\n✅ Usuario encontrado:")
                print(f"   ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   Username: {user.username}")
                print(f"   Password Hash (primeros 50 chars): {user.password_hash[:50]}...")
                print(f"   Hash Length: {len(user.password_hash)}")
                print(f"   Is Active: {user.is_active}")
                print(f"   Created At: {user.created_at}")
                print(f"   Updated At: {user.updated_at}")

                # Verificar si es un bcrypt válido
                if user.password_hash.startswith("$2"):
                    print(f"\n   ✅ Hash comienza correctamente con $2 (bcrypt)")
                else:
                    print(f"\n   ❌ Hash NO comienza con $2 - NO es bcrypt válido")

                return {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "is_active": user.is_active,
                    "hash_valid": user.password_hash.startswith("$2"),
                }
            else:
                print(f"\n❌ Usuario '{email}' NO encontrado en BD")

                # Listar todos los usuarios
                stmt_all = select(User)
                result_all = await session.execute(stmt_all)
                users = result_all.scalars().all()

                if users:
                    print(f"\n   Usuarios existentes ({len(users)}):")
                    for u in users:
                        print(f"     - {u.email} ({u.username})")
                else:
                    print(f"\n   No hay usuarios en la BD")

                return None

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()
            return None
        finally:
            await engine.dispose()


async def main() -> int:
    """Punto de entrada principal."""
    email = sys.argv[1] if len(sys.argv) > 1 else "admin@example.com"

    result = await check_user(email)

    print("\n" + "=" * 60)
    return 0 if result else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
