"""
scripts/setup.py

Script orquestador para el setup inicial de PePDF-FASTAPI.
Realiza:
  1. Resetea la BD (opcional)
  2. Crea el usuario admin
  3. Verifica la configuración

Uso: uv run python -m scripts.setup
"""

import asyncio
import sys
from typing import Optional

from scripts.db.create_admin_user import create_admin_user
from scripts.db.reset_db import reset_database
from scripts.utils.check_user import check_user


async def setup_pepdf() -> bool:
    """
    Ejecuta el setup completo de PePDF-FASTAPI.

    Returns:
        bool: True si el setup fue exitoso
    """
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  SETUP INICIAL DE PePDF-FASTAPI                           ║")
    print("╚" + "=" * 58 + "╝")

    # Opción 1: Resetear BD (opcional)
    print("\n📋 Paso 1/3: ¿Resetear base de datos?")
    print("   Esto eliminará todos los datos existentes")
    response = input("   ¿Resetear BD? (s/n): ").strip().lower()

    if response == "s":
        print("\n⏳ Reseteando base de datos...")
        success = await reset_database(interactive=False)
        if not success:
            print("❌ Falló resetear la BD")
            return False
        print("✅ BD reseteada")
    else:
        print("⏭️  Saltando reseteo de BD")

    # Paso 2: Crear usuario admin
    print("\n📋 Paso 2/3: Crear usuario admin")
    print("⏳ Creando usuario admin...")
    success = await create_admin_user(interactive=False)
    if not success:
        print("❌ Falló crear usuario admin")
        return False
    print("✅ Usuario admin creado")

    # Paso 3: Verificar
    print("\n📋 Paso 3/3: Verificar configuración")
    print("⏳ Verificando usuario admin...")
    result = await check_user("admin@example.com")

    if not result:
        print("❌ No se encontró el usuario admin")
        return False

    if not result.get("hash_valid"):
        print("❌ El hash del usuario no es válido")
        return False

    print("✅ Configuración verificada")

    # Resumen final
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  ✅ SETUP COMPLETADO EXITOSAMENTE                         ║")
    print("╚" + "=" * 58 + "╝")
    print("\n📌 Próximos pasos:")
    print("   1. Iniciar el servidor: uv run fastapi dev app/main.py")
    print("   2. Probar login: curl -X POST http://localhost:8000/auth/login \\")
    print('        -H "Content-Type: application/json" \\')
    print(
        '        -d \'{"email":"admin@example.com","password":"admin123"}\''
    )
    print("   3. Ver endpoints: http://localhost:8000/docs")
    print("\n")

    return True


async def main() -> int:
    """Punto de entrada principal."""
    try:
        success = await setup_pepdf()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelado por el usuario")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error durante setup: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
