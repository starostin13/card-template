#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ фракций в исходном CSV файле
Определяет все уникальные faction_id и их распределение
"""
import csv
from collections import Counter

def analyze_factions():
    """Анализирует фракции в CSV файле"""
    faction_counter = Counter()
    faction_examples = {}
    
    with open('Stratagems.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        
        for row in reader:
            faction_id = row.get('faction_id', '').strip()
            name = row.get('name', '').strip()
            stratagem_type = row.get('type', '').strip()
            
            faction_counter[faction_id] += 1
            
            # Сохраняем примеры для каждого faction_id
            if faction_id not in faction_examples:
                faction_examples[faction_id] = {
                    'name': name,
                    'type': stratagem_type
                }
    
    print("=== АНАЛИЗ ФРАКЦИЙ В CSV ФАЙЛЕ ===")
    print(f"Всего уникальных faction_id: {len(faction_counter)}")
    print()
    
    # Сортируем по количеству стратагемм (по убыванию)
    for faction_id, count in faction_counter.most_common():
        example = faction_examples[faction_id]
        faction_display = f"'{faction_id}'" if faction_id else "'пустой'"
        
        print(f"Faction ID: {faction_display}")
        print(f"  Количество стратагемм: {count}")
        print(f"  Пример названия: {example['name']}")
        print(f"  Пример типа: {example['type']}")
        print()
    
    # Анализируем типы стратагемм для определения фракций
    print("=== АНАЛИЗ ТИПОВ СТРАТАГЕММ ===")
    type_counter = Counter()
    
    with open('Stratagems.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        
        for row in reader:
            stratagem_type = row.get('type', '').strip()
            type_counter[stratagem_type] += 1
    
    # Показываем топ-20 типов
    for stratagem_type, count in type_counter.most_common(20):
        print(f"{count:4d}: {stratagem_type}")

if __name__ == "__main__":
    analyze_factions()