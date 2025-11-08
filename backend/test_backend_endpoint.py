"""
Test the backend Fear & Greed Index endpoint
This simulates what the frontend does
"""
import asyncio
import httpx
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_backend_endpoint():
    """Test the backend endpoint"""
    print("🧪 Testing Backend Fear & Greed Index Endpoint")
    print("=" * 60)
    
    # Check if backend is running
    backend_url = "http://localhost:8501"
    endpoint = f"{backend_url}/api/v1/fear-greed-index"
    
    print(f"\n1. Checking if backend is running on {backend_url}...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # First check if backend is up
            health_check = await client.get(f"{backend_url}/")
            print(f"   ✅ Backend is running (status: {health_check.status_code})")
    except httpx.ConnectError:
        print(f"   ❌ Backend is NOT running on {backend_url}")
        print(f"   💡 Start backend with: cd backend && ./start.sh")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test the endpoint (will fail without auth, but we can see the structure)
    print(f"\n2. Testing endpoint: {endpoint}")
    print(f"   ⚠️  Note: This requires Supabase authentication")
    print(f"   Without auth, you'll get 401/403, but we can verify the endpoint exists")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(endpoint)
            
            print(f"\n   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS! Endpoint is working!")
                print(f"   Response: {data}")
                return True
            elif response.status_code == 401:
                print(f"   ⚠️  401 Unauthorized - Authentication required (expected)")
                print(f"   ✅ Endpoint exists and is accessible")
                print(f"   💡 This is normal - you need to be logged in via Supabase")
                return True  # Endpoint exists, just needs auth
            elif response.status_code == 403:
                print(f"   ⚠️  403 Forbidden - Email not in CSV whitelist (expected)")
                print(f"   ✅ Endpoint exists and is accessible")
                print(f"   💡 Make sure your email is in backend/privatedata/srp_client_trading.csv")
                return True  # Endpoint exists, just needs whitelist
            elif response.status_code == 500:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('detail', response.text)
                print(f"   ❌ 500 Internal Server Error")
                print(f"   Error: {error_msg}")
                if "CRYPTO_MARKET_API_KEY" in error_msg:
                    print(f"   💡 Add CRYPTO_MARKET_API_KEY to backend/.env file")
                return False
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except httpx.TimeoutException:
        print(f"   ❌ Request timeout")
        return False
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_backend_endpoint())
    print("\n" + "=" * 60)
    if result:
        print("✅ Backend endpoint test completed!")
        print("\n💡 Summary:")
        print("   - Backend is running")
        print("   - Endpoint exists and is accessible")
        print("   - To test fully, you need to:")
        print("     1. Be logged in via Supabase")
        print("     2. Have your email in backend/privatedata/srp_client_trading.csv")
        print("     3. Have CRYPTO_MARKET_API_KEY in backend/.env")
    else:
        print("❌ Backend endpoint test failed")
        sys.exit(1)





