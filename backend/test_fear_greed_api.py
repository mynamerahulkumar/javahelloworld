"""
Test script to verify CoinMarketCap Fear & Greed Index API
"""
import asyncio
import httpx

async def test_coinmarketcap_api():
    """Test CoinMarketCap API directly"""
    api_key = "577e124fb9f14e7791f16231887d9fe6"
    
    print("🧪 Testing CoinMarketCap Fear & Greed Index API")
    print("=" * 60)
    
    base_url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json',
        'Accept-Encoding': 'deflate, gzip'
    }
    params = {
        'start': 1,
        'limit': 1
    }
    
    try:
        print(f"\n1. Calling CoinMarketCap API...")
        print(f"   URL: {base_url}")
        print(f"   Params: {params}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(base_url, headers=headers, params=params)
            
            print(f"\n2. Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"3. Response Structure:")
                print(f"   - Has 'status': {'status' in data}")
                print(f"   - Has 'data': {'data' in data}")
                
                if 'status' in data:
                    status = data['status']
                    print(f"   - error_code: {status.get('error_code')}")
                    print(f"   - error_message: {status.get('error_message', 'None')}")
                
                error_code = data.get('status', {}).get('error_code')
                if error_code == 0 or error_code == '0' or str(error_code) == '0':
                    index_data = data.get('data', [])
                    
                    if index_data:
                        current_index = index_data[0]
                        print(f"\n✅ SUCCESS! Fear & Greed Index Data:")
                        print(f"   Value: {current_index.get('value')}")
                        print(f"   Classification: {current_index.get('value_classification')}")
                        print(f"   Timestamp: {current_index.get('timestamp')}")
                        print(f"\n✅ API Key is valid and working!")
                        return True
                    else:
                        print(f"\n❌ No data in response")
                        print(f"   Full response: {data}")
                        return False
                else:
                    error_msg = data.get('status', {}).get('error_message', 'Unknown error')
                    print(f"\n❌ CoinMarketCap API Error:")
                    print(f"   {error_msg}")
                    print(f"   Full response: {data}")
                    return False
            else:
                print(f"\n❌ HTTP Error {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
    except httpx.TimeoutException:
        print(f"\n❌ Request timeout")
        return False
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_coinmarketcap_api())
    print("\n" + "=" * 60)
    if result:
        print("✅ Test PASSED - API is working correctly!")
        print("\n💡 Next step: Add CRYPTO_MARKET_API_KEY to backend/.env file")
        print("   echo 'CRYPTO_MARKET_API_KEY=577e124fb9f14e7791f16231887d9fe6' >> backend/.env")
    else:
        print("❌ Test FAILED - Check the errors above")

