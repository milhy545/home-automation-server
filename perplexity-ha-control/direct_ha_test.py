#!/usr/bin/env python3
"""
Direct Home Assistant API test without external dependencies
"""
import urllib.request
import json
import ssl

# HA configuration
HA_URL = "http://localhost:10002"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkYmRiMDgxMzQ2NzI0MzY5OTI5NzY5YjBiNzFiZGJhNSIsImlhdCI6MTcyMDE5NzIxMCwiZXhwIjoyMDM1NTU3MjEwfQ.Fj4dE2-2TlNuaXyiGhbJXIhiQMkKAXz9WJXo-3pYHZ4"

def test_ha_api():
    # Test getting states
    print("Testing HA API connection...")
    
    try:
        # Get states
        req = urllib.request.Request(f"{HA_URL}/api/states")
        req.add_header("Authorization", f"Bearer {HA_TOKEN}")
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Found {len(data)} entities")
            
            # Find light entities
            lights = [e for e in data if e['entity_id'].startswith('light.')]
            print(f"Found {len(lights)} lights")
            
            if lights:
                print(f"First light: {lights[0]['entity_id']} - {lights[0]['state']}")
                
                # Try to turn on first light
                print(f"Turning on {lights[0]['entity_id']}...")
                
                req2 = urllib.request.Request(f"{HA_URL}/api/services/light/turn_on", 
                                             data=json.dumps({"entity_id": lights[0]['entity_id']}).encode('utf-8'))
                req2.add_header("Authorization", f"Bearer {HA_TOKEN}")
                req2.add_header("Content-Type", "application/json")
                
                with urllib.request.urlopen(req2) as response2:
                    result = json.loads(response2.read().decode('utf-8'))
                    print(f"Result: {result}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ha_api()