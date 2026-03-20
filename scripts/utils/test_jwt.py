"""Quick test script for JWT authentication module"""
import asyncio
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from jose import JWTError


async def test_password_hashing():
    """Test password hashing and verification"""
    print("🔐 Testing password hashing...")
    password = "admin123"
    
    # Hash password
    hashed = hash_password(password)
    print(f"  ✓ Password hashed: {hashed[:50]}...")
    
    # Verify correct password
    assert verify_password(password, hashed), "Password verification failed"
    print(f"  ✓ Password verification passed")
    
    # Verify incorrect password
    assert not verify_password("wrongpassword", hashed), "Wrong password should not verify"
    print(f"  ✓ Wrong password correctly rejected")


async def test_jwt_tokens():
    """Test JWT token creation and decoding"""
    print("\n🎫 Testing JWT tokens...")
    
    user_data = {"sub": "admin@example.com"}
    
    # Test access token (indefinite)
    access_token = create_access_token(user_data, expires_in=None)
    print(f"  ✓ Access token created (indefinite): {access_token[:50]}...")
    
    # Decode access token
    decoded = decode_token(access_token)
    assert decoded["sub"] == "admin@example.com", "Token subject mismatch"
    assert "exp" not in decoded, "Access token should not have exp when expires_in=None"
    print(f"  ✓ Access token decoded successfully")
    print(f"    Claims: {decoded}")
    
    # Test refresh token (with expiration)
    refresh_token = create_refresh_token(user_data, expires_in=30)
    print(f"\n  ✓ Refresh token created (30 days): {refresh_token[:50]}...")
    
    # Decode refresh token
    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh["sub"] == "admin@example.com", "Refresh token subject mismatch"
    assert decoded_refresh["type"] == "refresh", "Refresh token type mismatch"
    assert "exp" in decoded_refresh, "Refresh token should have exp"
    print(f"  ✓ Refresh token decoded successfully")
    print(f"    Claims: {decoded_refresh}")
    
    # Test invalid token
    try:
        decode_token("invalid.token.here")
        assert False, "Should have raised JWTError"
    except JWTError:
        print(f"  ✓ Invalid token correctly rejected")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("PePDF JWT Authentication Module Test")
    print("=" * 60)
    
    await test_password_hashing()
    await test_jwt_tokens()
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
