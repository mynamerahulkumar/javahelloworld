#!/usr/bin/env python3
"""
Simple test script to verify Auth0 configuration from .env file
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

def test_auth0_config():
    print("=" * 50)
    print("Testing Auth0 Configuration from .env")
    print("=" * 50)
    
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")
    audience = os.getenv("AUTH0_AUDIENCE")
    algorithm = os.getenv("AUTH0_ALGORITHM", "RS256")
    enable_whitelist = os.getenv("AUTH0_ENABLE_WHITELIST", "true")
    
    print(f"\nAUTH0_DOMAIN: {domain or '❌ NOT SET'}")
    print(f"AUTH0_CLIENT_ID: {client_id[:10] + '...' if client_id else '❌ NOT SET'}")
    print(f"AUTH0_CLIENT_SECRET: {'***' if client_secret else '❌ NOT SET'}")
    print(f"AUTH0_AUDIENCE: {audience or 'Not set (optional)'}")
    print(f"AUTH0_ALGORITHM: {algorithm}")
    print(f"AUTH0_ENABLE_WHITELIST: {enable_whitelist}")
    
    # Check if required variables are set
    missing = []
    if not domain:
        missing.append("AUTH0_DOMAIN")
    if not client_id:
        missing.append("AUTH0_CLIENT_ID")
    if not client_secret:
        missing.append("AUTH0_CLIENT_SECRET")
    
    # Clean domain (remove https:// if present)
    clean_domain = domain
    if clean_domain:
        if clean_domain.startswith("https://"):
            clean_domain = clean_domain.replace("https://", "", 1)
        if clean_domain.startswith("http://"):
            clean_domain = clean_domain.replace("http://", "", 1)
        clean_domain = clean_domain.rstrip("/")
    
    if missing:
        print(f"\n❌ Missing required Auth0 configuration: {', '.join(missing)}")
        print("\nPlease add these to backend/.env:")
        for var in missing:
            print(f"  {var}=your_value_here")
        return False
    else:
        print("\n✅ All required Auth0 configuration is present!")
        print(f"\nCleaned Domain: {clean_domain}")
        print(f"Issuer URL: https://{clean_domain}/")
        print(f"JWKS URL: https://{clean_domain}/.well-known/jwks.json")
        
        # Note about audience
        if audience == "your_auth_api_identifier":
            print("\n⚠️  Note: AUTH0_AUDIENCE is set to placeholder value.")
            print("   If you're using Auth0 API authentication, update this value.")
            print("   Otherwise, you can leave it as is or remove it.")
        
        return True

if __name__ == "__main__":
    success = test_auth0_config()
    sys.exit(0 if success else 1)

