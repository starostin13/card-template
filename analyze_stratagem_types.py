#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор типов стратагемм для фильтрации
Определяет основные стратагемы 10-й редакции vs специальные режимы
"""
import csv
from collections import Counter

def analyze_stratagem_types():
    """Анализирует типы стратагемм в CSV файле"""
    
    type_counter = Counter()
    type_examples = {}
    
    with open('Stratagems.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        
        for row in reader:
            stratagem_type = row.get('type', '').strip()
            name = row.get('name', '').strip()
            
            type_counter[stratagem_type] += 1
            
            # Сохраняем примеры
            if stratagem_type not in type_examples:
                type_examples[stratagem_type] = []
            if len(type_examples[stratagem_type]) < 3:
                type_examples[stratagem_type].append(name)
    
    print("=== АНАЛИЗ ТИПОВ СТРАТАГЕММ ===")
    print(f"Всего уникальных типов: {len(type_counter)}")
    print()
    
    # Категоризируем типы стратагемм
    main_game_keywords = [
        "Battle Tactic", "Epic Deed", "Strategic Ploy",
        "Wargear Stratagem"
    ]
    
    special_modes = [
        "Boarding Actions", "Combat Patrol", "Crusade",
        "Challenger", "Kill Team"
    ]
    
    main_game_stratagems = []
    special_mode_stratagems = []
    unknown_stratagems = []
    
    for stratagem_type, count in type_counter.most_common():
        is_main_game = False
        is_special_mode = False
        
        # Проверяем основную игру
        for keyword in main_game_keywords:
            if keyword in stratagem_type:
                main_game_stratagems.append((stratagem_type, count))
                is_main_game = True
                break
        
        # Проверяем специальные режимы
        if not is_main_game:
            for keyword in special_modes:
                if keyword in stratagem_type:
                    special_mode_stratagems.append((stratagem_type, count))
                    is_special_mode = True
                    break
        
        # Неопределенные
        if not is_main_game and not is_special_mode:
            unknown_stratagems.append((stratagem_type, count))
    
    # Выводим результаты
    print("🎯 ОСНОВНЫЕ СТРАТАГЕМЫ 10-Й РЕДАКЦИИ:")
    main_total = 0
    for stratagem_type, count in main_game_stratagems:
        main_total += count
        print(f"  {count:3d}: {stratagem_type}")
        if stratagem_type in type_examples:
            print(f"       Примеры: {', '.join(type_examples[stratagem_type][:2])}")
    print(f"Итого основных: {main_total}")
    print()
    
    print("🚀 СПЕЦИАЛЬНЫЕ РЕЖИМЫ (исключаем):")
    special_total = 0
    for stratagem_type, count in special_mode_stratagems:
        special_total += count
        print(f"  {count:3d}: {stratagem_type}")
        if stratagem_type in type_examples:
            print(f"       Примеры: {', '.join(type_examples[stratagem_type][:2])}")
    print(f"Итого специальных: {special_total}")
    print()
    
    print("❓ НЕОПРЕДЕЛЕННЫЕ (требуют анализа):")
    unknown_total = 0
    for stratagem_type, count in unknown_stratagems:
        unknown_total += count
        print(f"  {count:3d}: {stratagem_type}")
        if stratagem_type in type_examples:
            print(f"       Примеры: {', '.join(type_examples[stratagem_type][:2])}")
    print(f"Итого неопределенных: {unknown_total}")
    print()
    
    print("📊 ОБЩАЯ СТАТИСТИКА:")
    total = main_total + special_total + unknown_total
    print(f"Всего стратагемм: {total}")
    print(f"Основные: {main_total} ({main_total/total*100:.1f}%)")
    print(f"Специальные: {special_total} ({special_total/total*100:.1f}%)")
    print(f"Неопределенные: {unknown_total} ({unknown_total/total*100:.1f}%)")
    
    return main_game_stratagems, special_mode_stratagems, unknown_stratagems

if __name__ == "__main__":
    analyze_stratagem_types()