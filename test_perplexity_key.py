#!/usr/bin/env python3
"""Test Perplexity API key validation"""

import asyncio
import aiohttp

async def test_api_key(api_key):
    """Test if API key is valid"""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "user", "content": "test"}
        ],
        "max_tokens": 10
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("✅ API klíč je validní!")
                    print(f"Response: {data}")
                    return True
                elif response.status == 401:
                    print("❌ Nevalidní API klíč")
                    return False
                else:
                    text = await response.text()
                    print(f"❌ Chyba {response.status}: {text}")
                    return False
    except Exception as e:
        print(f"❌ Síťová chyba: {e}")
        return False

if __name__ == "__main__":
    # Test s různými klíči
    test_keys = [
        "pplx-test",  # nevalidní
        input("Zadej Perplexity API klíč: ").strip()  # od uživatele
    ]
    
    for key in test_keys:
        if key:
            print(f"\n🔑 Testuji klíč: {key[:10]}...")
            result = asyncio.run(test_api_key(key))
            if result:
                print(f"✅ Tento klíč funguje: {key}")
                break