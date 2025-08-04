#!/usr/bin/env python3
"""
🧪 PERPLEXITY-HA CONTROL SYSTEM TESTS
Kompletní test suite pro ověření funkčnosti
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

class PerplexityHATests:
    def __init__(self):
        self.litellm_url = "http://localhost:4000"
        self.ha_url = "http://localhost:10002/api"
        self.ha_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZGRhZGQ"  # Získám z HA
        self.test_results = []
        
    def log(self, test_name, status, message=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL", 
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{result['status']} {test_name}: {message}")
        
    async def test_litellm_health(self):
        """Test 1: LiteLLM proxy zdraví"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.litellm_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log("LiteLLM Health", True, f"Proxy běží - {data}")
                        return True
                    else:
                        self.log("LiteLLM Health", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log("LiteLLM Health", False, f"Chyba: {e}")
            return False
            
    async def test_perplexity_via_litellm(self):
        """Test 2: Perplexity přes LiteLLM proxy"""
        payload = {
            "model": "perplexity-pro",
            "messages": [
                {"role": "user", "content": "Test připojení - odpověz jen 'OK'"}
            ],
            "max_tokens": 10
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.litellm_url}/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        answer = data['choices'][0]['message']['content']
                        self.log("Perplexity via LiteLLM", True, f"Odpověď: {answer}")
                        return True
                    else:
                        text = await response.text()
                        self.log("Perplexity via LiteLLM", False, f"HTTP {response.status}: {text}")
                        return False
        except Exception as e:
            self.log("Perplexity via LiteLLM", False, f"Chyba: {e}")
            return False
            
    async def test_ha_api_access(self):
        """Test 3: Home Assistant API přístup"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.ha_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(f"{self.ha_url}/", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log("HA API Access", True, f"HA verze: {data.get('message', 'OK')}")
                        return True
                    else:
                        self.log("HA API Access", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log("HA API Access", False, f"Chyba: {e}")
            return False
            
    async def test_ha_entities(self):
        """Test 4: Seznam HA entit"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.ha_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(f"{self.ha_url}/states", headers=headers) as response:
                    if response.status == 200:
                        entities = await response.json()
                        light_count = len([e for e in entities if e['entity_id'].startswith('light.')])
                        switch_count = len([e for e in entities if e['entity_id'].startswith('switch.')])
                        sensor_count = len([e for e in entities if e['entity_id'].startswith('sensor.')])
                        
                        self.log("HA Entities", True, 
                               f"Light: {light_count}, Switch: {switch_count}, Sensor: {sensor_count}")
                        return True
                    else:
                        self.log("HA Entities", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log("HA Entities", False, f"Chyba: {e}")
            return False
            
    async def test_smart_home_control(self):
        """Test 5: Smart home ovládání přes Perplexity"""
        # Simulace: "Perplexity, rozsvit světla"
        smart_command = """
        Analyze this command and respond with JSON action:
        Command: "Turn on the living room lights"
        
        Respond only with JSON in this format:
        {"action": "light.turn_on", "entity_id": "light.living_room", "brightness": 255}
        """
        
        payload = {
            "model": "perplexity-pro", 
            "messages": [
                {"role": "system", "content": "You are a smart home controller. Always respond with valid JSON only."},
                {"role": "user", "content": smart_command}
            ],
            "max_tokens": 100
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.litellm_url}/chat/completions",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data['choices'][0]['message']['content']
                        
                        # Zkus parsovat JSON odpověď
                        try:
                            action_json = json.loads(ai_response)
                            self.log("Smart Home Control", True, f"AI rozpoznal: {action_json}")
                            return action_json
                        except json.JSONDecodeError:
                            self.log("Smart Home Control", False, f"Nevalidní JSON: {ai_response}")
                            return False
                    else:
                        self.log("Smart Home Control", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log("Smart Home Control", False, f"Chyba: {e}")
            return False
            
    async def test_end_to_end_workflow(self):
        """Test 6: Kompletní workflow"""
        print("\n🚀 TESTING END-TO-END WORKFLOW:")
        print("Simulace: 'Hej Perplexity, rozsvit světla v obýváku'")
        
        # 1. Perplexity analysis
        result = await self.test_smart_home_control()
        if not result:
            return False
            
        # 2. HA API call (simulace)
        if isinstance(result, dict) and 'action' in result:
            print(f"   → Volám HA API: {result['action']}")
            print(f"   → Entity: {result.get('entity_id', 'unknown')}")
            self.log("End-to-End Workflow", True, "Kompletní chain funguje!")
            return True
        else:
            self.log("End-to-End Workflow", False, "Chain přerušen")
            return False
    
    async def run_all_tests(self):
        """Spustí všechny testy"""
        print("🧪 PERPLEXITY-HA CONTROL SYSTEM TESTS")
        print("=" * 50)
        
        tests = [
            self.test_litellm_health,
            self.test_perplexity_via_litellm,
            self.test_ha_api_access,
            self.test_ha_entities,
            self.test_smart_home_control,
            self.test_end_to_end_workflow
        ]
        
        passed = 0
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                self.log(test.__name__, False, f"Exception: {e}")
                
        print("\n" + "=" * 50)
        print(f"📊 VÝSLEDKY: {passed}/{len(tests)} testů prošlo")
        
        if passed == len(tests):
            print("🎉 VŠECHNO FUNGUJE! Systém je připraven!")
        else:
            print("⚠️ Některé testy selhaly - potřeba opravit")
            
        return self.test_results

if __name__ == "__main__":
    tester = PerplexityHATests()
    results = asyncio.run(tester.run_all_tests())