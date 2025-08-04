#!/usr/bin/env python3
"""
🏠 SMART HOME FUNCTION LIBRARY
Definice všech funkcí pro ovládání Home Assistantu přes Perplexity
"""

import json
import aiohttp
from typing import Dict, Any, List

class SmartHomeFunctions:
    """Smart home control functions for Perplexity integration"""
    
    def __init__(self, ha_url: str, ha_token: str):
        self.ha_url = ha_url
        self.ha_token = ha_token
        self.headers = {
            "Authorization": f"Bearer {ha_token}",
            "Content-Type": "application/json"
        }
    
    async def call_ha_service(self, domain: str, service: str, entity_id: str = None, data: Dict = None):
        """Call Home Assistant service"""
        url = f"{self.ha_url}/services/{domain}/{service}"
        payload = {"entity_id": entity_id} if entity_id else {}
        if data:
            payload.update(data)
            
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                return await response.json() if response.status == 200 else None
    
    async def get_entity_state(self, entity_id: str):
        """Get entity state"""
        url = f"{self.ha_url}/states/{entity_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.json() if response.status == 200 else None
    
    # FUNCTION DEFINITIONS for Perplexity
    
    def get_function_definitions(self) -> List[Dict]:
        """Get all function definitions for AI"""
        return [
            {
                "name": "turn_on_lights",
                "description": "Turn on lights in specified room or all lights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room": {
                            "type": "string",
                            "description": "Room name (living_room, bedroom, kitchen, etc.) or 'all' for all lights"
                        },
                        "brightness": {
                            "type": "integer", 
                            "description": "Brightness 0-255, default 255",
                            "minimum": 0,
                            "maximum": 255
                        }
                    },
                    "required": ["room"]
                }
            },
            {
                "name": "turn_off_lights", 
                "description": "Turn off lights in specified room or all lights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room": {
                            "type": "string",
                            "description": "Room name or 'all' for all lights"
                        }
                    },
                    "required": ["room"]
                }
            },
            {
                "name": "set_temperature",
                "description": "Set thermostat temperature",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "temperature": {
                            "type": "number",
                            "description": "Target temperature in Celsius"
                        },
                        "room": {
                            "type": "string",
                            "description": "Room name, default 'main'"
                        }
                    },
                    "required": ["temperature"]
                }
            },
            {
                "name": "get_sensor_data",
                "description": "Get sensor readings (temperature, humidity, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sensor_type": {
                            "type": "string", 
                            "enum": ["temperature", "humidity", "motion", "door", "all"],
                            "description": "Type of sensor to read"
                        },
                        "room": {
                            "type": "string",
                            "description": "Room name, optional"
                        }
                    },
                    "required": ["sensor_type"]
                }
            },
            {
                "name": "control_media",
                "description": "Control media players (play, pause, volume)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["play", "pause", "stop", "next", "previous", "volume"],
                            "description": "Media action to perform"
                        },
                        "device": {
                            "type": "string", 
                            "description": "Media player device name"
                        },
                        "volume": {
                            "type": "number",
                            "description": "Volume level 0.0-1.0 (only for volume action)"
                        }
                    },
                    "required": ["action", "device"]
                }
            },
            {
                "name": "trigger_automation",
                "description": "Trigger Home Assistant automation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "automation_name": {
                            "type": "string",
                            "description": "Name or ID of automation to trigger"
                        }
                    },
                    "required": ["automation_name"]
                }
            }
        ]
    
    # FUNCTION IMPLEMENTATIONS
    
    async def turn_on_lights(self, room: str, brightness: int = 255):
        """Turn on lights"""
        if room == "all":
            entity_id = "group.all_lights"
        else:
            entity_id = f"light.{room}"
            
        data = {"brightness": brightness} if brightness < 255 else {}
        result = await self.call_ha_service("light", "turn_on", entity_id, data)
        return f"✅ Rozsvítil jsem světla v {room} (jas: {brightness})"
    
    async def turn_off_lights(self, room: str):
        """Turn off lights"""
        if room == "all":
            entity_id = "group.all_lights"
        else:
            entity_id = f"light.{room}"
            
        result = await self.call_ha_service("light", "turn_off", entity_id)
        return f"✅ Zhasil jsem světla v {room}"
    
    async def set_temperature(self, temperature: float, room: str = "main"):
        """Set temperature"""
        entity_id = f"climate.{room}" if room != "main" else "climate.main_thermostat"
        data = {"temperature": temperature}
        result = await self.call_ha_service("climate", "set_temperature", entity_id, data)
        return f"✅ Nastavil jsem teplotu na {temperature}°C v {room}"
    
    async def get_sensor_data(self, sensor_type: str, room: str = None):
        """Get sensor data"""
        if sensor_type == "all":
            # Get all sensors
            url = f"{self.ha_url}/states"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        entities = await response.json()
                        sensors = [e for e in entities if e['entity_id'].startswith('sensor.')]
                        return f"📊 Našel jsem {len(sensors)} senzorů"
        else:
            entity_id = f"sensor.{room}_{sensor_type}" if room else f"sensor.{sensor_type}"
            state = await self.get_entity_state(entity_id)
            if state:
                return f"📊 {sensor_type} v {room or 'main'}: {state['state']} {state.get('attributes', {}).get('unit_of_measurement', '')}"
            else:
                return f"❌ Sensor {entity_id} not found"
    
    async def control_media(self, action: str, device: str, volume: float = None):
        """Control media player"""
        entity_id = f"media_player.{device}"
        
        if action == "volume" and volume is not None:
            data = {"volume_level": volume}
            result = await self.call_ha_service("media_player", "volume_set", entity_id, data)
            return f"🔊 Nastavil jsem hlasitost {device} na {volume*100}%"
        else:
            service_map = {
                "play": "media_play",
                "pause": "media_pause", 
                "stop": "media_stop",
                "next": "media_next_track",
                "previous": "media_previous_track"
            }
            service = service_map.get(action, action)
            result = await self.call_ha_service("media_player", service, entity_id)
            return f"▶️ {action} na {device}"
    
    async def trigger_automation(self, automation_name: str):
        """Trigger automation"""
        entity_id = f"automation.{automation_name}"
        result = await self.call_ha_service("automation", "trigger", entity_id)
        return f"🤖 Spustil jsem automatizaci: {automation_name}"


# DEMO USAGE
async def demo():
    """Demo použití"""
    functions = SmartHomeFunctions(
        ha_url="http://localhost:10002/api",
        ha_token="your_ha_token_here"
    )
    
    print("🏠 Smart Home Functions Demo")
    print("Functions available:", [f["name"] for f in functions.get_function_definitions()])

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())