"""Test de conexión a la base de datos PostgreSQL"""
import asyncio
from sqlalchemy import text
from app.core.database import engine
from app.config import settings


async def test_connection():
    """Test conexión a la BD"""
    print("=" * 60)
    print("TEST DE CONEXIÓN A BASE DE DATOS")
    print("=" * 60)
    
    print(f"\n📍 Configuración:")
    print(f"   DATABASE_URL: {settings.database_url}")
    
    try:
        print(f"\n⏳ Conectando a PostgreSQL...")
        
        # Intentar conectar
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            value = result.scalar()
            
            if value == 1:
                print(f"✅ Conexión EXITOSA")
                print(f"   El servidor PostgreSQL está respondiendo correctamente")
                return True
    except Exception as e:
        print(f"❌ ERROR de conexión:")
        print(f"   {type(e).__name__}: {str(e)}")
        return False
    finally:
        await engine.dispose()


async def main():
    success = await test_connection()
    print("\n" + "=" * 60)
    if success:
        print("✅ Base de datos LISTA para usar")
    else:
        print("❌ NO se puede conectar a la BD")
        print("\nSoluciones:")
        print("1. Verifica que PostgreSQL está corriendo")
        print("   docker-compose ps")
        print("2. Verifica las credenciales en .env")
        print("3. Asegúrate que el puerto 5432 está disponible")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
