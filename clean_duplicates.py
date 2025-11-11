#!/usr/bin/env python3
"""
Скрипт для удаления дубликатов карточек из cards_data.json
Оставляет только уникальные карточки согласно правилам дублирования.
"""

import json
from collections import defaultdict
from typing import Dict, List, Any

def clean_duplicates(input_file: str, output_file: str):
    """Удаляет дубликаты согласно правилам CP стоимости"""
    
    # Загружаем данные
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cards = data.get('cards', [])
    
    print(f"📊 Исходных карточек: {len(cards)}")
    
    # Группируем карточки по названию и языку
    card_groups = defaultdict(list)
    
    for card in cards:
        title = card.get('title', '')
        
        # Определяем язык карточки
        has_cyrillic = any(ord(char) > 127 for char in title)
        language = 'ru' if has_cyrillic else 'en'
        
        # Группируем по названию (без учета языка - для дубликатов переводов)
        key = f"{title}_{language}"
        card_groups[key].append(card)
    
    # Убираем дубликаты и применяем правила CP
    cleaned_cards = []
    stats = {
        'removed_duplicates': 0,
        'total_groups': len(card_groups),
        'cp_0_1_count': 0,
        'cp_2_plus_count': 0
    }
    
    for key, group in card_groups.items():
        if len(group) > 1:
            stats['removed_duplicates'] += len(group) - 1
            print(f"🔧 Найдено {len(group)} дубликатов для '{key}', оставляем 1")
        
        # Берем первую карточку из группы (уникальную)
        card = group[0]
        cp_cost = card.get('cost', {}).get('cp', 0)
        
        if cp_cost <= 1:
            # Для CP 0-1: добавляем карточку дважды
            cleaned_cards.append(card)
            cleaned_cards.append(card.copy())  # Копия для второго экземпляра
            stats['cp_0_1_count'] += 1
        else:
            # Для CP 2+: добавляем карточку один раз
            cleaned_cards.append(card)
            stats['cp_2_plus_count'] += 1
    
    # Создаем очищенную структуру
    cleaned_data = {
        "cards": cleaned_cards
    }
    
    # Сохраняем результат
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📈 РЕЗУЛЬТАТ ОЧИСТКИ:")
    print(f"{'='*40}")
    print(f"Удалено дубликатов: {stats['removed_duplicates']}")
    print(f"Уникальных групп: {stats['total_groups']}")
    print(f"Карточек CP 0-1 (x2): {stats['cp_0_1_count']} → {stats['cp_0_1_count'] * 2} карточек")
    print(f"Карточек CP 2+ (x1): {stats['cp_2_plus_count']} → {stats['cp_2_plus_count']} карточек")
    print(f"Итоговых карточек: {len(cleaned_cards)}")
    print(f"Сохранено в: {output_file}")

if __name__ == "__main__":
    clean_duplicates("cards_data.json", "cards_data_cleaned.json")