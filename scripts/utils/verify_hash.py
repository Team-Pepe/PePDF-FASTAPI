"""
scripts/utils/verify_hash.py

Script para verificar si un hash bcrypt es válido y puede ser validado.
Útil para debugging de problemas de password.
Uso: uv run python -m scripts.utils.verify_hash [email] [password]
"""

import asyncio
import sys
from typing import Optional

import bcrypt
from sqlalchemy import select

from app.core.database import engine, async_session
from app.models import User
from app.core.security import verify_password


async def verify_hash(email: str, password: str) -> bool:
    """
    Verifica si el hash de un usuario puede ser validado con una contraseña.

    Args:
        email: Email del usuario
        password: Contraseña en texto plano

    Returns:
        bool: True si la validación es exitosa
    """
    print("=" * 60)
    print("VERIFICAR HASH BCRYPT")
    print("=" * 60)

    async with async_session() as session:
        try:
            # Obtener usuario
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if not user:
                print(f"\n❌ Usuario '{email}' NO encontrado")
                return False

            print(f"\n📋 Usuario encontrado: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Hash (primeros 50): {user.password_hash[:50]}...")

            # Validar formato bcrypt
            print(f"\n🔐 Validando formato bcrypt...")
            if not user.password_hash.startswith("$2"):
                print(f"   ❌ Hash no comienza con $2 - formato inválido")
                return False
            print(f"   ✅ Formato bcrypt válido")

            if len(user.password_hash) != 60:
                print(
                    f"   ⚠️  Hash tiene {len(user.password_hash)} chars (esperado 60)"
                )
            else:
                print(f"   ✅ Longitud correcta (60 chars)")

            # Intentar verificar la contraseña
            print(f"\n🔑 Verificando contraseña '{password}'...")
            try:
                is_valid = verify_password(password, user.password_hash)
                if is_valid:
                    print(f"   ✅ Contraseña VÁLIDA")
                    return True
                else:
                    print(f"   ❌ Contraseña INCORRECTA")
                    return False
            except ValueError as e:
                print(f"   ❌ Error en verificación bcrypt: {e}")
                # Intentar directamente con bcrypt
                print(f"\n   Intentando verificación directa con bcrypt...")
                try:
                    result = bcrypt.checkpw(
                        password.encode(), user.password_hash.encode()
                    )
                    print(f"   {'✅ VÁLIDA' if result else '❌ INCORRECTA'}")
                    return result
                except Exception as e2:
                    print(f"   ❌ Error: {e2}")
                    return False

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            await engine.dispose()


async def main() -> int:
    """Punto de entrada principal."""
    if len(sys.argv) < 3:
        print("Uso: uv run python -m scripts.utils.verify_hash <email> <password>")
        print("Ej:  uv run python -m scripts.utils.verify_hash admin@example.com admin123")
        return 1

    email = sys.argv[1]
    password = sys.argv[2]

    result = await verify_hash(email, password)

    print("\n" + "=" * 60)
    return 0 if result else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
