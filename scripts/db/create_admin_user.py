"""
scripts/db/create_admin_user.py

Script para crear o actualizar un usuario admin con bcrypt hash válido.
Uso: uv run python -m scripts.db.create_admin_user
"""

import asyncio
import sys
from typing import Optional

import bcrypt
from sqlalchemy import select

from app.core.database import async_session, engine
from app.models import User, Base


async def create_admin_user(
    email: str = "admin@example.com",
    password: str = "admin123",
    username: str = "admin",
    interactive: bool = True,
) -> bool:
    """
    Crea o actualiza un usuario admin con password hasheado correctamente.

    Args:
        email: Email del usuario admin
        password: Contraseña en texto plano
        username: Nombre de usuario
        interactive: Si True, solicita confirmación

    Returns:
        bool: True si se creó/actualizó exitosamente, False si se canceló
    """
    print("=" * 60)
    print("CREAR/ACTUALIZAR USUARIO ADMIN CON BCRYPT VÁLIDO")
    print("=" * 60)

    if interactive:
        response = (
            input(
                f"\n¿Crear usuario admin con email '{email}'? (s/n): "
            )
            .strip()
            .lower()
        )
        if response != "s":
            print("Cancelado")
            return False

    try:
        # 1. Crear tabla si no existe
        print("\n⏳ Creando/verificando tabla users...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tabla users lista")

        # 2. Generar hash bcrypt seguro
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        print(f"\n🔐 Password info:")
        print(f"   Plain: {password}")
        print(f"   Hash: {password_hash}")
        print(f"   Hash Length: {len(password_hash)}")

        # 3. Crear/actualizar usuario en BD
        async with async_session() as session:
            # Verificar si existe
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                print(f"\n🔄 Actualizando usuario existente ({existing_user.id})...")
                existing_user.password_hash = password_hash
                existing_user.is_active = True
                await session.merge(existing_user)
            else:
                print(f"\n➕ Creando usuario nuevo...")
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    is_active=True,
                )
                session.add(new_user)

            await session.commit()
            print("✅ Usuario guardado en BD")

            # 4. Verificar
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalars().first()

            if user:
                print(f"\n✅ Verificación exitosa:")
                print(f"   ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   Username: {user.username}")
                print(f"   Is Active: {user.is_active}")

                # Verificar que bcrypt puede validar
                try:
                    is_valid = bcrypt.checkpw(
                        password.encode(), user.password_hash.encode()
                    )
                    if is_valid:
                        print(f"\n✅ Password verification CORRECTA")
                    else:
                        print(f"\n❌ Password verification FALLÓ")
                        return False
                except Exception as e:
                    print(f"\n❌ Error verificando password: {e}")
                    return False

                return True
            else:
                print(f"\n❌ Error: Usuario no encontrado después de guardar")
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
    success = await create_admin_user(interactive=True)

    if success:
        print("\n" + "=" * 60)
        print("✅ LISTO - Ahora puedes hacer login con:")
        print("   Email: admin@example.com")
        print("   Password: admin123")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ FALLÓ crear usuario admin")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
