#!/usr/bin/env python3
"""
Test script for Fear & Greed Index endpoint
This script tests the backend endpoint with proper authentication
"""
import asyncio
import httpx
import os
import sys
from pathlib import Path

# Add src directory to Python path
backend_path = Path(__file__).parent
src_path = backend_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")

async def test_fear_greed_endpoint():
    """Test the Fear & Greed Index endpoint"""
    print("🧪 Testing Fear & Greed Index Endpoint")
    print("=" * 80)
    
    backend_url = "http://localhost:8501/api/v1/fear-greed-index"
    
    # Check if backend is running
    print("\n1. Checking if backend is running...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8501/")
            if response.status_code == 200:
                print("   ✅ Backend is running")
            else:
                print(f"   ⚠️  Backend responded with status: {response.status_code}")
    except httpx.ConnectError as e:
        print(f"   ❌ Backend is not running: {e}")
        print("\n   Please start the backend first:")
        print("   cd backend && ./start.sh")
        return False
    except Exception as e:
        print(f"   ❌ Error checking backend: {e}")
        return False
    
    # Check environment variables
    print("\n2. Checking environment variables...")
    crypto_api_key = os.getenv("CRYPTO_MARKET_API_KEY")
    if crypto_api_key:
        print(f"   ✅ CRYPTO_MARKET_API_KEY is set (length: {len(crypto_api_key)})")
    else:
        print("   ❌ CRYPTO_MARKET_API_KEY is not set")
        print("   Please add it to backend/.env file")
        return False
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if supabase_url and supabase_key:
        print(f"   ✅ Supabase configuration found (URL: {supabase_url[:30]}...)")
    else:
        print("   ⚠️  Supabase configuration not found")
        print("   The endpoint requires Supabase authentication")
    
    # Test endpoint without auth (should fail with 401)
    print("\n3. Testing endpoint without authentication (should fail)...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(backend_url)
            print(f"   Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Correctly requires authentication")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test endpoint with mock auth (if we can get a token)
    print("\n4. Testing endpoint with authentication...")
    print("   ⚠️  This requires a valid Supabase JWT token")
    print("   To get a token, you need to:")
    print("   1. Log in via the frontend")
    print("   2. Get the JWT token from browser localStorage or cookies")
    print("   3. Pass it in the Authorization header: Bearer <token>")
    
    # Check if we can test the CoinMarketCap API directly
    print("\n5. Testing CoinMarketCap API directly...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                'X-CMC_PRO_API_KEY': crypto_api_key,
                'Accept': 'application/json',
            }
            params = {'start': 1, 'limit': 1}
            response = await client.get(
                "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                error_code = data.get('status', {}).get('error_code')
                if error_code == 0 or error_code == '0' or str(error_code) == '0':
                    index_data = data.get('data', [])
                    if index_data:
                        current_index = index_data[0]
                        value = current_index.get('value', 50)
                        classification = current_index.get('value_classification', 'Neutral')
                        print(f"   ✅ CoinMarketCap API is working!")
                        print(f"   Value: {value}")
                        print(f"   Classification: {classification}")
                        print(f"   Timestamp: {current_index.get('timestamp', 'N/A')}")
                    else:
                        print("   ⚠️  CoinMarketCap API returned empty data")
                else:
                    error_msg = data.get('status', {}).get('error_message', 'Unknown error')
                    print(f"   ❌ CoinMarketCap API error: {error_msg}")
            else:
                print(f"   ❌ CoinMarketCap API HTTP error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
    except httpx.TimeoutException:
        print("   ❌ CoinMarketCap API request timed out")
    except Exception as e:
        print(f"   ❌ Error testing CoinMarketCap API: {e}")
    
    print("\n" + "=" * 80)
    print("📋 Summary:")
    print("   - Backend is running: ✅")
    print("   - CRYPTO_MARKET_API_KEY is configured: ✅")
    print("   - To test the full endpoint, you need a valid Supabase JWT token")
    print("   - Check backend logs for detailed error messages:")
    print("     tail -f backend/logs/bot.log")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    asyncio.run(test_fear_greed_endpoint())
