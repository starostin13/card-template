import json

# Загружаем данные
with open('cards_data_filtered.json', encoding='utf-8') as f:
    data = json.load(f)

cards = data['cards']

# Проверяем первые карты каждой фракции
factions = {}
for card in cards:
    faction = card['faction']
    if faction not in factions:
        factions[faction] = []
    if len(factions[faction]) < 3:
        factions[faction].append(card['title'])

print("Первые карты каждой фракции:")
for faction, titles in factions.items():
    print(f"\n{faction}:")
    for i, title in enumerate(titles, 1):
        print(f"  {i}. {title}")