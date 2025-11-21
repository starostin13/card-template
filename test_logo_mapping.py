import json
import os

# Загружаем данные
with open('cards_data_filtered.json', encoding='utf-8') as f:
    data = json.load(f)

# Маппинг фракций на логотипы (тот же что в card_generator.py)
faction_logo_map = {
    # Русские названия (старые)
    "Общие стратагемы": "general.png",
    "Абордаж": "boarding.png", 
    "Претендент": "challenger.png",
    "Базовые стратагемы": "core.png",
    "Adeptus Astartes": "space_marines.png",
    "Chaos": "chaos.png",
    "Imperial Guard": "imperial_guard.png", 
    "Orks": "orks.png",
    "Necrons": "necrons.png",
    "Tyranids": "tyranids.png",
    "Eldar": "eldar.png",
    
    # Английские названия (новые из CSV)
    "Core Stratagems": "core.png",
    "Adeptus Custodes": "custodes.png",
    "Space Marines": "space_marines.png",
    "Chaos Daemons": "chaos.png",
    "Grey Knights": "grey_knights.png",
    "Death Guard": "death_guard.png",
    "Aeldari": "eldar.png",
    "Questoris Imperialis": "imperial_knights.png",
}

cards = data['cards']

# Проверяем какие фракции есть и какие логотипы назначены
factions = set(card['faction'] for card in cards)

print("Маппинг фракций на логотипы:")
for faction in sorted(factions):
    logo = faction_logo_map.get(faction, "general.png")
    logo_path = os.path.join("faction_logos", logo)
    exists = "✅" if os.path.exists(logo_path) else "❌"
    print(f"{exists} {faction} -> {logo}")