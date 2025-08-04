# Instalační návod - Perplexity HA Integration

## 🎯 Přehled

Tato integrace nahrazuje původní automatizační skript **moderní Home Assistant custom integration** s následujícími výhodami:

✅ **GUI konfigurace** - Žádné CLI příkazy  
✅ **HACS podpora** - Snadná instalace a aktualizace  
✅ **Nativní HA integrace** - Plně součást ekosystému  
✅ **Pokročilá konfigurace** - Options flow pro fine-tuning  

## 📦 Instalace

### Metoda 1: HACS (Doporučeno)

1. **Otevřete HACS**
   ```
   Settings → Devices & Services → HACS
   ```

2. **Přidejte custom repository**
   - Klikněte na ⋮ menu
   - "Custom repositories"
   - URL: `https://github.com/custom-components/perplexity`
   - Kategorie: Integration

3. **Nainstalujte integraci**
   - Vyhledejte "Perplexity AI Assistant"
   - Klikněte "Download"
   - Restartujte Home Assistant

### Metoda 2: Manuální kopírování

```bash
# Zkopírujte celou složku
cp -r /root/perplexity-ha-integration/custom_components/perplexity \
      /config/custom_components/

# Restart HA
docker restart homeassistant
# NEBO
systemctl restart homeassistant
```

## ⚙️ Konfigurace

### 1. Přidání integrace

```
Settings → Devices & Services → Add Integration
```

1. Vyhledejte **"Perplexity AI Assistant"**
2. Zadejte **Perplexity API Key**
   - Získejte na: https://www.perplexity.ai/settings/api
3. Vyberte **výchozí model** (doporučujeme `sonar-pro`)
4. **Pojmenujte** integraci (např. "Perplexity AI")

### 2. Pokročilá nastavení (Options)

Po instalaci klikněte na **"Configure"**:

- **Temperature** (0.0-2.0): Kreativita odpovědí
- **Max Tokens** (10-4000): Délka odpovědí
- **Enable TTS**: Automatické hlasové odpovědi
- **TTS Entity**: Výběr TTS služby

## 🚀 Použití

### Základní služby

#### Položení otázky
```yaml
service: perplexity.ask_question
data:
  question: "Jaké je dnes počasí v Praze?"
  # Volitelné parametry:
  model: "sonar-pro"
  temperature: 0.8
  max_tokens: 500
```

#### Změna modelu
```yaml
service: perplexity.set_model
data:
  model: "sonar-reasoning"
```

### Entity a senzory

Po instalaci máte k dispozici:

- **`sensor.perplexity_last_response`** - Poslední odpověď
- **`sensor.perplexity_status`** - Stav API připojení

### Události

Integrace vysílá událost `perplexity_question_answered`:

```yaml
automation:
  - alias: "Log Perplexity Answers"
    trigger:
      - platform: event
        event_type: perplexity_question_answered
    action:
      - service: logbook.log
        data:
          name: "Perplexity"
          message: "{{ trigger.event.data.response.answer[:100] }}..."
```

## 📝 Příklady automatizací

### Hlasové ovládání

```yaml
automation:
  - alias: "Voice Questions to Perplexity"
    trigger:
      - platform: conversation
        command: "Ask Perplexity {question}"
    action:
      - service: perplexity.ask_question
        data:
          question: "{{ trigger.slots.question.value }}"
      - delay: "00:00:02"
      - service: tts.google_translate_say
        data:
          entity_id: media_player.living_room
          message: "{{ states('sensor.perplexity_last_response') }}"
```

### Webhook pro externí aplikace

```yaml
automation:
  - alias: "Perplexity Webhook"
    trigger:
      - platform: webhook
        webhook_id: perplexity_external
        local_only: false
    action:
      - service: perplexity.ask_question
        data:
          question: "{{ trigger.json.question }}"
      - service: webhook.response
        data:
          status_code: 200
          body: |
            {
              "answer": "{{ states('sensor.perplexity_last_response') }}",
              "sources": {{ state_attr('sensor.perplexity_last_response', 'sources') | tojson }},
              "timestamp": "{{ state_attr('sensor.perplexity_last_response', 'timestamp') }}"
            }
```

### Smart notifikace

```yaml
automation:
  - alias: "Perplexity to Mobile"
    trigger:
      - platform: event
        event_type: perplexity_question_answered
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Perplexity odpověděl"
          message: "{{ trigger.event.data.response.answer[:100] }}..."
          data:
            actions:
              - action: "read_full"
                title: "Přečíst celé"
```

## 🔧 Migrace z původního skriptu

Pokud jste používali původní automatizační skript:

### 1. Zálohování
```bash
cp /config/automations_perplexity.yaml /config/automations_perplexity.yaml.backup
cp /config/python_scripts/perplexity_integration.py /config/python_scripts/perplexity_integration.py.backup
```

### 2. Odebrání starého systému
```bash
# Odeberte ze secrets.yaml
nano /config/secrets.yaml
# Vymažte řádky:
# perplexity_api_key: "..."
# perplexity_webhook_id: "..."

# Odeberte automatizace
rm /config/automations_perplexity.yaml
rm /config/python_scripts/perplexity_integration.py

# Odeberte z configuration.yaml
nano /config/configuration.yaml
# Vymažte řádky:
# automation: !include automations_perplexity.yaml
# sensor: !include sensors_perplexity.yaml
```

### 3. Instalace nové integrace
Následujte kroky výše pro instalaci custom integration.

### 4. Aktualizace automatizací

**Starý způsob:**
```yaml
- service: python_script.perplexity_integration
  data:
    question: "{{ trigger.json.question }}"
```

**Nový způsob:**
```yaml
- service: perplexity.ask_question
  data:
    question: "{{ trigger.json.question }}"
```

## 🏃‍♂️ Rychlý test

Po instalaci otestujte funkcionalnost:

### Developer Tools → Services

```yaml
service: perplexity.ask_question
data:
  question: "Kolik je teď hodin?"
```

### Template test

```yaml
{{ states('sensor.perplexity_last_response') }}
{{ state_attr('sensor.perplexity_last_response', 'question') }}
{{ state_attr('sensor.perplexity_last_response', 'sources') }}
```

## 🔍 Troubleshooting

### Časté problémy

**❌ Integration not found**
- Zkontrolujte, že je složka v `/config/custom_components/perplexity/`
- Restartujte Home Assistant

**❌ Invalid API Key**
- Ověřte klíč na https://www.perplexity.ai/settings/api
- Zkontrolujte kredit na účtu

**❌ Slow responses**
- Použijte rychlejší model (`sonar`)
- Snižte `max_tokens`

### Debug logování

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.perplexity: debug
```

## 📊 Porovnání přístupů

| Aspekt | Starý skript | Nová integrace |
|--------|--------------|----------------|
| Instalace | CLI + bash | GUI + HACS |
| Konfigurace | YAML edity | GUI forms |
| Aktualizace | Manuální | HACS automaticky |
| Debugging | Log soubory | HA dev tools |
| Údržba | Bash scripting | Python standard |

## 🎉 Výhody nové integrace

1. **Žádné CLI** - Vše přes Home Assistant GUI
2. **HACS podpora** - Automatické aktualizace
3. **Lepší UX** - Konfigurace přes formuláře
4. **Debugging** - Integrované HA nástroje
5. **Události** - Pokročilé automatizace
6. **Services** - Flexibilní API
7. **Standardy** - Následuje HA best practices

Tato integrace představuje **modernější a udržitelnější** přístup k propojení Perplexity s Home Assistantem! 🚀