#!/usr/bin/env python3
"""
🌉 PERPLEXITY-HA BRIDGE SERVER
Hlavní server který propojuje Perplexity s Home Assistant
"""

import asyncio
import aiohttp
import json
import logging
from aiohttp import web
from smart_home_functions import SmartHomeFunctions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerplexityHABridge:
    """Bridge server mezi Perplexity a Home Assistant"""
    
    def __init__(self):
        self.litellm_url = "http://localhost:4000"
        self.ha_url = "http://localhost:10002/api"
        self.ha_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"  # Získám z HA
        self.smart_home = SmartHomeFunctions(self.ha_url, self.ha_token)
        
    async def process_voice_command(self, command: str) -> str:
        """Zpracuj hlasový příkaz přes Perplexity"""
        
        # Systémový prompt s funkcemi
        system_prompt = f"""
        You are a smart home assistant that controls Home Assistant.
        
        Available functions:
        {json.dumps(self.smart_home.get_function_definitions(), indent=2)}
        
        When user gives a command:
        1. Analyze what they want to do
        2. Choose appropriate function
        3. Execute the action
        4. Respond in Czech what you did
        
        Examples:
        "Rozsvit světla" → turn_on_lights(room="all")
        "Zhasni v obýváku" → turn_off_lights(room="living_room") 
        "Nastavit teplotu na 22" → set_temperature(temperature=22)
        "Jaká je teplota?" → get_sensor_data(sensor_type="temperature")
        """
        
        # Volání Perplexity přes LiteLLM
        payload = {
            "model": "perplexity-pro",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command}
            ],
            "max_tokens": 200,
            "temperature": 0.3
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
                        
                        # Parsuj odpověď a vykonej akci
                        action_result = await self.parse_and_execute(ai_response, command)
                        return action_result
                    else:
                        return f"❌ Chyba Perplexity API: {response.status}"
                        
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"❌ Chyba: {str(e)}"
    
    async def parse_and_execute(self, ai_response: str, original_command: str) -> str:
        """Parsuj AI odpověď a vykonej akci"""
        
        # Jednoduchá detekce příkazů (později bude pokročilejší)
        command_lower = original_command.lower()
        
        try:
            if "rozsvit" in command_lower or "zapni světl" in command_lower:
                if "obývák" in command_lower or "living" in command_lower:
                    result = await self.smart_home.turn_on_lights("living_room")
                elif "kuchyň" in command_lower or "kitchen" in command_lower:
                    result = await self.smart_home.turn_on_lights("kitchen")
                else:
                    result = await self.smart_home.turn_on_lights("all")
                return result
                
            elif "zhasni" in command_lower or "vypni světl" in command_lower:
                if "obývák" in command_lower:
                    result = await self.smart_home.turn_off_lights("living_room")
                elif "kuchyň" in command_lower:
                    result = await self.smart_home.turn_off_lights("kitchen")
                else:
                    result = await self.smart_home.turn_off_lights("all")
                return result
                
            elif "teplota" in command_lower and ("nastav" in command_lower or "na" in command_lower):
                # Extrahuj číslo
                import re
                numbers = re.findall(r'(\d+)', command_lower)
                if numbers:
                    temp = int(numbers[0])
                    result = await self.smart_home.set_temperature(temp)
                    return result
                    
            elif "teplota" in command_lower or "kolik" in command_lower:
                result = await self.smart_home.get_sensor_data("temperature")
                return result
                
            else:
                # Fallback - vrať AI odpověď
                return f"🤖 Perplexity říká: {ai_response}"
                
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return f"❌ Chyba při vykonávání: {str(e)}"
    
    # WEB SERVER ENDPOINTS
    
    async def handle_voice_command(self, request):
        """Handle voice command via HTTP"""
        try:
            data = await request.json()
            command = data.get('command', '')
            
            if not command:
                return web.json_response({"error": "Missing command"}, status=400)
            
            logger.info(f"Processing command: {command}")
            result = await self.process_voice_command(command)
            
            return web.json_response({
                "command": command,
                "result": result,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"Error handling voice command: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_webhook(self, request):
        """Handle webhook from Perplexity Assistant app"""
        try:
            data = await request.json()
            
            # Extract command from various possible formats
            command = (
                data.get('text') or 
                data.get('message') or 
                data.get('query') or 
                data.get('command', '')
            )
            
            result = await self.process_voice_command(command)
            
            return web.json_response({
                "response": result,
                "success": True
            })
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_status(self, request):
        """Status endpoint"""
        return web.json_response({
            "status": "running",
            "bridge": "Perplexity-HA Bridge v1.0",
            "endpoints": {
                "voice_command": "/api/voice",
                "webhook": "/webhook/perplexity",
                "status": "/status"
            }
        })
    
    def create_app(self):
        """Create web application"""
        app = web.Application()
        
        # Routes
        app.router.add_post('/api/voice', self.handle_voice_command)
        app.router.add_post('/webhook/perplexity', self.handle_webhook)
        app.router.add_get('/status', self.handle_status)
        
        # CORS
        async def cors_handler(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        app.middlewares.append(cors_handler)
        
        return app
    
    async def start_server(self, host='0.0.0.0', port=8888):
        """Start bridge server"""
        app = self.create_app()
        
        logger.info(f"🌉 Perplexity-HA Bridge starting on {host}:{port}")
        logger.info("📡 Endpoints:")
        logger.info(f"   POST {host}:{port}/api/voice - Voice commands")
        logger.info(f"   POST {host}:{port}/webhook/perplexity - Webhook from Perplexity app")
        logger.info(f"   GET  {host}:{port}/status - Status check")
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info("✅ Bridge server is running!")
        
        # Keep running
        try:
            await asyncio.Future()  # run forever
        except KeyboardInterrupt:
            logger.info("👋 Shutting down bridge server")
            await runner.cleanup()

# CLI interface pro testování
async def test_command(command: str):
    """Test command via CLI"""
    bridge = PerplexityHABridge()
    result = await bridge.process_voice_command(command)
    print(f"Command: {command}")
    print(f"Result: {result}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # CLI test mode
        command = " ".join(sys.argv[1:])
        asyncio.run(test_command(command))
    else:
        # Server mode
        bridge = PerplexityHABridge()
        asyncio.run(bridge.start_server())