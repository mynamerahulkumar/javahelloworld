#!/usr/bin/env python3
"""
Test script to verify Auth0 configuration
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from auth.auth0.config import get_auth0_config

def test_auth0_config():
    print("=" * 50)
    print("Testing Auth0 Configuration")
    print("=" * 50)
    
    try:
        config = get_auth0_config()
        
        if config is None:
            print("\n❌ Auth0 is not configured")
            print("\nPlease add the following to backend/.env:")
            print("  AUTH0_DOMAIN=your-tenant.auth0.com")
            print("  AUTH0_CLIENT_ID=your_client_id")
            print("  AUTH0_CLIENT_SECRET=your_client_secret")
            print("  AUTH0_AUDIENCE=your_api_audience (optional)")
            return False
        
        print("\n✅ Auth0 Configuration Loaded Successfully!")
        print(f"\nDomain: {config.domain}")
        print(f"Client ID: {config.client_id[:10]}..." if config.client_id else "None")
        print(f"Client Secret: {'***' if config.client_secret else 'None'}")
        print(f"Audience: {config.audience or 'Not set (optional)'}")
        print(f"Algorithm: {config.algorithm}")
        print(f"Enable Whitelist: {config.enable_whitelist}")
        print(f"Issuer: {config.issuer}")
        print(f"\nJWKS URL: {config.get_jwks_url()}")
        
        # Test if configuration is valid
        if config.is_configured():
            print("\n✅ All required Auth0 configuration is present")
            return True
        else:
            print("\n❌ Some required Auth0 configuration is missing")
            return False
    
    except Exception as e:
        print(f"\n❌ Error loading Auth0 configuration: {e}")
        print("\nPlease check your backend/.env file")
        return False

if __name__ == "__main__":
    success = test_auth0_config()
    sys.exit(0 if success else 1)





