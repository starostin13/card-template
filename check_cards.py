import json

data = json.load(open('cards_data.json', encoding='utf-8'))

counter_cards = [c for c in data['cards'] if c['title'] == 'COUNTER-OFFENSIVE']
print(f'COUNTER-OFFENSIVE cards found: {len(counter_cards)}')

for i, card in enumerate(counter_cards, 1):
    lang = 'Russian' if card['body']['when'].startswith('Фаза') else 'English'
    print(f'  Card {i}: {lang}')

print(f'\nTotal cards in file: {len(data["cards"])}')
