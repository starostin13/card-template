#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Фильтрация стратагемм - оставляем только основные 40K 10-й редакции
Исключаем специальные режимы игры
"""
import json
import csv

def should_exclude_stratagem(stratagem_type: str, name: str) -> tuple[bool, str]:
    """
    Определяет, нужно ли исключить стратагему
    Возвращает (нужно_исключить, причина)
    """
    
    # Специальные режимы для исключения
    exclude_keywords = [
        "Boarding Actions",  # Режим абордажа
        "Combat Patrol",     # Боевой патруль  
        "Crusade",          # Крестовый поход
        "Challenger",       # Режим челленджера
        "Kill Team",        # Команда убийц
        "Narrative",        # Нарративные игры
        "Open Play",        # Открытая игра
        "Matched Play",     # Матчевая игра (если отдельные стратагемы)
    ]
    
    # Проверяем тип стратагемы
    for keyword in exclude_keywords:
        if keyword in stratagem_type:
            return True, f"Специальный режим: {keyword}"
    
    # Проверяем название стратагемы на специальные маркеры
    name_lower = name.lower()
    if any(keyword.lower() in name_lower for keyword in ["boarding", "crusade", "narrative"]):
        return True, f"Специальный режим в названии: {name}"
    
    return False, ""

def filter_main_game_stratagems():
    """Фильтрует стратагемы, оставляя только основную игру 40K 10-й редакции"""
    
    # Загружаем текущие данные с правильными фракциями
    with open('cards_data_fixed_factions.json', 'r', encoding='utf-8') as f:
        all_cards = json.load(f)
    
    print("=== ФИЛЬТРАЦИЯ СТРАТАГЕММ ===")
    print(f"Исходное количество карточек: {len(all_cards)}")
    
    # Фильтруем карточки
    main_game_cards = []
    excluded_cards = []
    
    for card in all_cards:
        stratagem_type = card.get('type', '')
        name = card.get('name', '')
        
        should_exclude, reason = should_exclude_stratagem(stratagem_type, name)
        
        if should_exclude:
            excluded_cards.append({
                'card': card,
                'reason': reason
            })
        else:
            main_game_cards.append(card)
    
    # Статистика исключений
    print(f"Карточек основной игры: {len(main_game_cards)}")
    print(f"Исключенных карточек: {len(excluded_cards)}")
    print()
    
    # Показываем что исключили
    if excluded_cards:
        print("🚫 ИСКЛЮЧЕННЫЕ СТРАТАГЕМЫ:")
        exclusion_stats = {}
        for excluded in excluded_cards:
            reason = excluded['reason']
            exclusion_stats[reason] = exclusion_stats.get(reason, 0) + 1
        
        for reason, count in sorted(exclusion_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {reason}: {count} карточек")
        
        print("\nПримеры исключенных стратагемм:")
        shown_examples = set()
        for excluded in excluded_cards[:10]:  # Показываем первые 10 примеров
            card = excluded['card']
            name = card.get('name', '')
            if name not in shown_examples:
                print(f"  • {name} ({card.get('type', '')})")
                shown_examples.add(name)
        print()
    
    # Сохраняем отфильтрованные данные
    with open('cards_data_main_game_only.json', 'w', encoding='utf-8') as f:
        json.dump(main_game_cards, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Сохранено в cards_data_main_game_only.json")
    
    # Анализируем что осталось по фракциям
    print("\n=== РАСПРЕДЕЛЕНИЕ ОСНОВНЫХ СТРАТАГЕММ ПО ФРАКЦИЯМ ===")
    faction_counts = {}
    language_counts = {'English': 0, 'Russian': 0}
    cp_counts = {}
    
    for card in main_game_cards:
        faction = card.get('faction', 'Unknown')
        language = card.get('language', 'Unknown')
        cp_cost = card.get('cp_cost', 0)
        
        faction_counts[faction] = faction_counts.get(faction, 0) + 1
        language_counts[language] = language_counts.get(language, 0) + 1
        cp_counts[cp_cost] = cp_counts.get(cp_cost, 0) + 1
    
    # Топ-20 фракций
    print("ТОП-20 ФРАКЦИЙ:")
    for faction, count in sorted(faction_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        percentage = (count / len(main_game_cards)) * 100
        print(f"  {faction}: {count} карточек ({percentage:.1f}%)")
    
    print(f"\nЯЗЫКИ:")
    for lang, count in language_counts.items():
        if count > 0:
            percentage = (count / len(main_game_cards)) * 100
            print(f"  {lang}: {count} карточек ({percentage:.1f}%)")
    
    print(f"\nСТОИМОСТЬ CP:")
    for cp, count in sorted(cp_counts.items()):
        percentage = (count / len(main_game_cards)) * 100
        print(f"  {cp} CP: {count} карточек ({percentage:.1f}%)")
    
    return len(main_game_cards), len(excluded_cards)

if __name__ == "__main__":
    filter_main_game_stratagems()