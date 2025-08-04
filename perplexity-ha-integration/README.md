# Perplexity AI Assistant for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/custom-components/perplexity.svg)](https://GitHub.com/custom-components/perplexity/releases/)

Integrace Perplexity AI Asistenta do Home Assistantu s možností pokládání otázek a získávání odpovědí s citacemi zdrojů.

## Funkce

✅ **GUI konfigurace** - Žádné editování YAML souborů  
✅ **Služby pro automatizace** - `perplexity.ask_question` a `perplexity.set_model`  
✅ **Senzory** - Sledování posledních odpovědí a stavu API  
✅ **Události** - `perplexity_question_answered` pro pokročilé automatizace  
✅ **Více modelů** - Sonar, Sonar Pro, Sonar Reasoning, Sonar Deep Research  
✅ **Konfigurovatelné parametry** - Temperature, max tokens, TTS podpora  

## Instalace

### HACS (Doporučeno)

1. Otevřete HACS v Home Assistantu
2. Přejděte do Integrations
3. Klikněte na ⋮ menu a vyberte "Custom repositories"
4. Přidejte tuto URL: `https://github.com/custom-components/perplexity`
5. Kategorie: Integration
6. Restartujte Home Assistant
7. Přejděte do Settings → Devices & Services
8. Klikněte "Add Integration" a vyhledejte "Perplexity"

### Manuální instalace

1. Stáhněte `perplexity` složku
2. Zkopírujte do `config/custom_components/perplexity`
3. Restartujte Home Assistant
4. Přidejte integraci přes UI

## Konfigurace

### 1. Získání API klíče

1. Jděte na [Perplexity API Settings](https://www.perplexity.ai/settings/api)
2. Vygenerujte nový API klíč
3. Zkopírujte klíč pro konfiguraci

### 2. Přidání integrace

1. Settings → Devices & Services → Add Integration
2. Vyhledejte "Perplexity AI Assistant"
3. Zadejte API klíč
4. Vyberte výchozí model
5. Pojmenujte integraci

### 3. Pokročilá nastavení (Volitelné)

V možnostech integrace můžete nastavit:
- **Temperature** (0.0-2.0) - Kreativita odpovědí
- **Max Tokens** (10-4000) - Délka odpovědí  
- **TTS Entity** - Pro hlasové odpovědi

## Použití

### Základní služby

#### Ask Question
```yaml
service: perplexity.ask_question
data:
  question: "Jaké je dnes počasí v Praze?"
  entity_id: sensor.perplexity_last_response  # volitelné
```

#### Set Model
```yaml
service: perplexity.set_model
data:
  model: "sonar-pro"
```

### Automatizace

#### Příklad: Hlasové dotazy
```yaml
automation:
  - alias: "Perplexity Voice Questions"
    trigger:
      - platform: conversation
        command: "Ask Perplexity {question}"
    action:
      - service: perplexity.ask_question
        data:
          question: "{{ trigger.slots.question.value }}"
      - service: tts.google_translate_say
        data:
          entity_id: media_player.living_room
          message: "{{ states('sensor.perplexity_last_response') }}"
```

#### Příklad: Smartwatch notifikace
```yaml
automation:
  - alias: "Perplexity to Watch"
    trigger:
      - platform: event
        event_type: perplexity_question_answered
    action:
      - service: notify.mobile_app_watch
        data:
          title: "Perplexity Answer"
          message: "{{ trigger.event.data.response.answer[:100] }}..."
```

### Template příklady

#### Získání posledního dotazu
```yaml
{{ state_attr('sensor.perplexity_last_response', 'question') }}
```

#### Kontrola zdrojů
```yaml
{% if state_attr('sensor.perplexity_last_response', 'sources') %}
  Sources: {{ state_attr('sensor.perplexity_last_response', 'sources')|join(', ') }}
{% endif %}
```

## Entity

### Senzory

- **`sensor.perplexity_last_response`** - Poslední odpověď
  - Atributy: `question`, `model`, `timestamp`, `sources`, `token_count`
- **`sensor.perplexity_status`** - Stav API
  - Atributy: `current_model`, `temperature`, `max_tokens`

### Události

- **`perplexity_question_answered`** - Vyvolána po zodpovězení otázky
  - Data: `entity_id`, `question`, `response`

## Modely

| Model | Kontext | Popis |
|-------|---------|-------|
| `sonar` | 16k | Základní model, rychlý |
| `sonar-pro` | 200k | Pro složitější dotazy |
| `sonar-reasoning` | 200k | Pokročilé reasoning |
| `sonar-deep-research` | 200k | Hluboký výzkum |

## Troubleshooting

### Časté problémy

**❌ Invalid API key**
- Ověřte platnost klíče na [Perplexity Settings](https://www.perplexity.ai/settings/api)
- Zkontrolujte, že máte dostatečný kredit

**❌ Rate limit exceeded**
- Snižte frekvenci dotazů
- Upgradujte na vyšší tarif

**❌ Timeout errors**
- Použijte jednodušší model (`sonar` místo `sonar-pro`)
- Snižte `max_tokens`

### Debug logování

```yaml
logger:
  default: info
  logs:
    custom_components.perplexity: debug
```

### Reinstalace

1. Odeberte integraci z UI
2. Restartujte HA
3. Přidejte znovu

## Bezpečnost

- API klíč je uložen šifrovaně v HA
- Podporuje pouze HTTPS komunikaci
- Rate limiting na straně Perplexity

## Podpora

- **Issues**: [GitHub Issues](https://github.com/custom-components/perplexity/issues)
- **Dokumentace**: [Wiki](https://github.com/custom-components/perplexity/wiki)
- **Community**: [Home Assistant Community](https://community.home-assistant.io/)

## Licence

MIT License - viz [LICENSE](LICENSE) soubor.

---

**Verze**: 1.0.0  
**Autor**: Claude AI Assistant  
**Datum**: 2025-07-05