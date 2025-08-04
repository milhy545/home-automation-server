#!/usr/bin/env python3
"""
OFFLINE DEMO: Complete Perplexity-Home Assistant Integration
Shows working system without external API dependencies
"""
import json
import time
import re

def simulate_perplexity_response(command):
    """Simulate Perplexity API responses based on command."""
    print(f"🤖 PERPLEXITY PROCESSING: {command}")
    
    responses = {
        "turn on the bedroom light": "I'll turn on the bedroom light for you. {\"action\": \"turn_on\", \"entity_id\": \"light.bedroom\"}",
        "turn off all lights": "I'll turn off all the lights in your home. {\"action\": \"turn_off\", \"entity_id\": \"light.all_lights\"}",
        "set the living room light to 50% brightness": "I'll set the living room light to 50% brightness. {\"action\": \"set_brightness\", \"entity_id\": \"light.living_room\", \"brightness\": 128}",
        "what's the weather like today?": "I'd need to check the weather service for current conditions. This would be a regular conversation, not a home automation command.",
        "lock the front door": "I'll lock the front door for you. {\"action\": \"lock\", \"entity_id\": \"lock.front_door\"}",
        "set thermostat to 72 degrees": "I'll set the thermostat to 72 degrees. {\"action\": \"set_temperature\", \"entity_id\": \"climate.main\", \"temperature\": 72}",
        "turn on the coffee maker": "I'll turn on the coffee maker for you. {\"action\": \"turn_on\", \"entity_id\": \"switch.coffee_maker\"}",
        "play music in the living room": "I'll start playing music in the living room. {\"action\": \"play_media\", \"entity_id\": \"media_player.living_room\", \"media\": \"playlist\"}",
        "close the garage door": "I'll close the garage door for you. {\"action\": \"close\", \"entity_id\": \"cover.garage_door\"}",
        "turn on security mode": "I'll activate security mode. {\"action\": \"arm_home\", \"entity_id\": \"alarm_control_panel.home_security\"}"
    }
    
    return responses.get(command.lower(), "I'm not sure how to control that device. Could you be more specific?")

def parse_command_from_response(response):
    """Parse JSON command from Perplexity response."""
    try:
        # Look for JSON in response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None

def execute_ha_command(command):
    """Simulate Home Assistant command execution."""
    if not command:
        return {"status": "error", "message": "No command to execute"}
    
    action = command.get("action")
    entity_id = command.get("entity_id")
    
    # Simulate different device types
    if action == "turn_on":
        print(f"✅ Turning ON {entity_id}")
        return {"status": "success", "message": f"Successfully turned on {entity_id}"}
    
    elif action == "turn_off":
        print(f"❌ Turning OFF {entity_id}")
        return {"status": "success", "message": f"Successfully turned off {entity_id}"}
    
    elif action == "set_brightness":
        brightness = command.get("brightness", 128)
        print(f"🔆 Setting {entity_id} brightness to {brightness}")
        return {"status": "success", "message": f"Set {entity_id} brightness to {brightness}"}
    
    elif action == "lock":
        print(f"🔒 Locking {entity_id}")
        return {"status": "success", "message": f"Successfully locked {entity_id}"}
    
    elif action == "set_temperature":
        temp = command.get("temperature", 70)
        print(f"🌡️  Setting {entity_id} to {temp}°F")
        return {"status": "success", "message": f"Set {entity_id} to {temp}°F"}
    
    elif action == "play_media":
        media = command.get("media", "default")
        print(f"🎵 Playing {media} on {entity_id}")
        return {"status": "success", "message": f"Playing {media} on {entity_id}"}
    
    elif action == "close":
        print(f"📥 Closing {entity_id}")
        return {"status": "success", "message": f"Successfully closed {entity_id}"}
    
    elif action == "arm_home":
        print(f"🚨 Arming {entity_id}")
        return {"status": "success", "message": f"Successfully armed {entity_id}"}
    
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}

def run_comprehensive_demo():
    """Run complete demo showing all capabilities."""
    print("🎯 PERPLEXITY-HOME ASSISTANT INTEGRATION")
    print("Complete Working Demo")
    print("=" * 60)
    
    # Test commands covering different device types
    test_commands = [
        "Turn on the bedroom light",
        "Turn off all lights",
        "Set the living room light to 50% brightness", 
        "Lock the front door",
        "Set thermostat to 72 degrees",
        "Turn on the coffee maker",
        "Play music in the living room",
        "Close the garage door",
        "Turn on security mode",
        "What's the weather like today?"
    ]
    
    successful_commands = 0
    total_commands = len(test_commands)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🗣️  VOICE COMMAND {i}: {command}")
        print("-" * 50)
        
        # Step 1: Get Perplexity response
        perplexity_response = simulate_perplexity_response(command)
        print(f"🤖 PERPLEXITY: {perplexity_response}")
        
        # Step 2: Parse command
        parsed_command = parse_command_from_response(perplexity_response)
        
        if parsed_command:
            print(f"⚙️  PARSED: {parsed_command}")
            
            # Step 3: Execute on Home Assistant
            result = execute_ha_command(parsed_command)
            print(f"🏠 HA RESULT: {result['message']}")
            
            if result['status'] == 'success':
                successful_commands += 1
                print("✅ SUCCESS")
            else:
                print("❌ FAILED")
        else:
            print("💬 CONVERSATIONAL RESPONSE (No device control)")
        
        time.sleep(0.5)  # Brief pause
    
    print(f"\n📊 DEMO RESULTS")
    print("=" * 60)
    print(f"Total Commands: {total_commands}")
    print(f"Successful Device Controls: {successful_commands}")
    print(f"Success Rate: {(successful_commands/total_commands)*100:.1f}%")
    
    print(f"\n🎉 DEMO COMPLETE!")
    print("This demonstrates how Perplexity Assistant can control your smart home!")

def show_system_architecture():
    """Display the complete system architecture."""
    print("\n🏗️  SYSTEM ARCHITECTURE")
    print("=" * 60)
    print("📱 PERPLEXITY ASSISTANT APP")
    print("    ↓ Voice Command")
    print("🤖 PERPLEXITY API")
    print("    ↓ Natural Language Processing")
    print("⚙️  COMMAND PARSER")
    print("    ↓ JSON Command Structure")
    print("🏠 HOME ASSISTANT API")
    print("    ↓ Device Control")
    print("💡 SMART HOME DEVICES")
    print("    ↓ Status Feedback")
    print("📱 USER NOTIFICATION")
    
    print(f"\n🔧 INTEGRATION COMPONENTS:")
    print("- Custom HA Integration (bidirectional)")
    print("- LiteLLM Proxy (function calling)")
    print("- Command Parser (natural language)")
    print("- Device Controllers (lights, locks, etc.)")
    print("- Voice Automation Triggers")
    
    print(f"\n📂 PROJECT STRUCTURE:")
    print("/root/perplexity-ha-integration/")
    print("├── custom_components/perplexity/")
    print("│   ├── manifest.json")
    print("│   ├── config_flow.py")
    print("│   ├── __init__.py")
    print("│   └── sensor.py")
    print("/root/perplexity-ha-control/")
    print("├── docker-compose.yml")
    print("├── smart_home_functions.py")
    print("├── perplexity_ha_bridge.py")
    print("└── working_demo.py")

if __name__ == "__main__":
    show_system_architecture()
    run_comprehensive_demo()
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. Get valid Perplexity API key working")
    print("2. Configure Home Assistant API token")
    print("3. Set up LiteLLM proxy for function calling")
    print("4. Install custom integration in HA")
    print("5. Configure voice automation triggers")
    print("6. Test with real Perplexity Assistant app")