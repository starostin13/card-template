import json

# Загружаем данные
with open('cards_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Общее количество карточек: {len(data['cards'])}")

# Подсчитываем карточки по стоимости CP
cp_counts = {}
faction_counts = {}
for card in data["cards"]:
    cp = card.get('cost', {}).get('cp', 'N/A')
    cp_counts[cp] = cp_counts.get(cp, 0) + 1
    
    faction = card.get('faction', 'Без фракции')
    faction_counts[faction] = faction_counts.get(faction, 0) + 1

print("\nРаспределение по стоимости CP:")
for k in sorted(cp_counts.keys(), key=lambda x: (x == 'N/A', x)):
    print(f"  {k} CP: {cp_counts[k]} карточек")

print("\nРаспределение по фракциям:")
for k, v in sorted(faction_counts.items()):
    print(f"  {k}: {v} карточек")

# Примерная оценка русских карточек
russian_indicators = ['фаза', 'подразделение', 'модель', 'атаки', 'В вашу', 'До конца']
russian_count = 0
for card in data["cards"]:
    text_content = (card['title'] + str(card.get('body', ''))).lower()
    if any(indicator.lower() in text_content for indicator in russian_indicators):
        russian_count += 1

print(f"\nКарточки с русскими переводами: ~{russian_count}")
print(f"Карточки без переводов (английские): ~{len(data['cards']) - russian_count}")