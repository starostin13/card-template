import json

# Загружаем данные
with open('cards_data_filtered.json', encoding='utf-8') as f:
    data = json.load(f)

cards = data['cards']
print(f'Всего карт: {len(cards)}')

# Статистика по фракциям
factions = {}
for card in cards:
    faction = card['faction']
    factions[faction] = factions.get(faction, 0) + 1

print('\nСтатистика по фракциям:')
for faction, count in sorted(factions.items()):
    print(f'  {faction}: {count}')

print('\nПервые 5 карт:')
for i, card in enumerate(cards[:5]):
    print(f'  {i+1}. {card["title"]} ({card["faction"]})')