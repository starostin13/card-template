#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор четности количества карточек
Проверяет, что все стратагемы имеют четное количество карточек
"""
import json
from collections import defaultdict

def analyze_card_counts():
    """Анализирует количество карточек для каждой уникальной стратагемы"""
    
    with open('cards_data_fixed_factions.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    # Группируем по базовому ID стратагемы (без _en_X или _ru_X)
    stratagem_counts = defaultdict(list)
    
    for card in cards:
        card_id = card['id']
        name = card['name']
        cp_cost = card['cp_cost']
        language = card['language']
        
        # Извлекаем базовый ID (убираем _en_X или _ru_X)
        if '_en_' in card_id:
            base_id = card_id.split('_en_')[0]
        elif '_ru_' in card_id:
            base_id = card_id.split('_ru_')[0]
        else:
            base_id = card_id
        
        stratagem_counts[base_id].append({
            'id': card_id,
            'name': name,
            'cp_cost': cp_cost,
            'language': language
        })
    
    # Анализируем результаты
    print("=== АНАЛИЗ ЧЕТНОСТИ КОЛИЧЕСТВА КАРТОЧЕК ===")
    print(f"Всего уникальных стратагемм: {len(stratagem_counts)}")
    print()
    
    odd_count_stratagems = []
    expected_violations = []
    
    for base_id, card_list in stratagem_counts.items():
        count = len(card_list)
        cp_cost = card_list[0]['cp_cost']  # CP одинаковый для всех копий
        name = card_list[0]['name']
        
        # Определяем ожидаемое количество
        if cp_cost <= 1:
            expected = 4  # 2 англ + 2 рус
        else:
            expected = 2  # 1 англ + 1 рус
        
        # Проверяем на нечетность
        if count % 2 != 0:
            odd_count_stratagems.append((name, count, cp_cost, base_id))
        
        # Проверяем соответствие ожиданиям
        if count != expected:
            expected_violations.append((name, count, expected, cp_cost, base_id))
    
    # Выводим проблемы с четностью
    if odd_count_stratagems:
        print("❌ НАЙДЕНЫ СТРАТАГЕМЫ С НЕЧЕТНЫМ КОЛИЧЕСТВОМ КАРТОЧЕК:")
        for name, count, cp_cost, base_id in odd_count_stratagems:
            print(f"  • {name} ({cp_cost} CP): {count} карточек [ID: {base_id}]")
        print()
    else:
        print("✅ Все стратагемы имеют четное количество карточек")
        print()
    
    # Выводим нарушения ожидаемых количеств
    if expected_violations:
        print("⚠️  НАРУШЕНИЯ ОЖИДАЕМЫХ КОЛИЧЕСТВ:")
        for name, actual, expected, cp_cost, base_id in expected_violations:
            print(f"  • {name} ({cp_cost} CP): {actual} вместо {expected} карточек [ID: {base_id}]")
        print()
    else:
        print("✅ Все стратагемы соответствуют ожидаемым количествам")
        print()
    
    # Статистика распределения количеств
    print("=== РАСПРЕДЕЛЕНИЕ ПО КОЛИЧЕСТВАМ ===")
    count_distribution = defaultdict(int)
    for card_list in stratagem_counts.values():
        count = len(card_list)
        count_distribution[count] += 1
    
    for count in sorted(count_distribution.keys()):
        num_stratagems = count_distribution[count]
        print(f"{count} карточек: {num_stratagems} стратагемм")
    
    # Статистика по языкам для каждой стратагемы
    print()
    print("=== ПРОВЕРКА ЯЗЫКОВОГО БАЛАНСА ===")
    language_issues = []
    
    for base_id, card_list in stratagem_counts.items():
        english_count = sum(1 for card in card_list if card['language'] == 'English')
        russian_count = sum(1 for card in card_list if card['language'] == 'Russian')
        
        if english_count != russian_count:
            name = card_list[0]['name']
            cp_cost = card_list[0]['cp_cost']
            language_issues.append((name, english_count, russian_count, cp_cost))
    
    if language_issues:
        print("❌ НАЙДЕНЫ ПРОБЛЕМЫ С ЯЗЫКОВЫМ БАЛАНСОМ:")
        for name, eng_count, rus_count, cp_cost in language_issues:
            print(f"  • {name} ({cp_cost} CP): {eng_count} англ., {rus_count} рус.")
    else:
        print("✅ Языковой баланс соблюден для всех стратагемм")

if __name__ == "__main__":
    analyze_card_counts()