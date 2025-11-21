#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для фильтрации стратагем по фракциям и режимам игры
"""

import csv
import json
from typing import Dict, List, Set


def analyze_stratagems_csv(csv_file_path: str):
    """
    Анализирует CSV файл стратагем для понимания структуры фракций и режимов
    """
    faction_ids = set()
    game_modes = set()
    core_count = 0
    faction_count = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        for row in reader:
            # Обрабатываем BOM символ в названии ключа
            faction_key = 'faction_id'
            if '\ufefffaction_id' in row:
                faction_key = '\ufefffaction_id'
            
            faction_name = row[faction_key].strip() if row.get(faction_key) else ""
            if faction_name:
                faction_ids.add(faction_name)
                faction_count += 1
            else:
                core_count += 1
            if row.get('type') and row['type'].strip():
                game_modes.add(row['type'].strip())
    
    print(f"Core стратагемы (без faction_id): {core_count}")
    print(f"Фракционные стратагемы: {faction_count}")
    print()
    print("Уникальные фракции:")
    for fid in sorted(faction_ids):
        print(f"  {fid}")
    
    print("\nПервые 20 типов стратагем:")
    for gm in sorted(game_modes)[:20]:
        print(f"  {gm}")


def filter_stratagems_by_factions_and_mode(csv_file_path: str, 
                                            output_file_path: str):
    """
    Фильтрует стратагемы, оставляя только основной режим и указанные фракции
    """
    # Определяем фракции, которые нужно оставить
    allowed_factions = {
        'Adeptus Custodes',     # кустодесы
        'Questoris Imperialis', # имперские рыцари  
        'Chaos Daemons',        # демоны хаоса
        'Grey Knights',         # серые рыцари
        'Space Marines',        # спейс марины (включает black templars, space wolves)
        'Necrons',              # некроны
        'Orks',                 # орки
        'Death Guard',          # гвардия смерти
        'Aeldari',              # эльдары
        '',                     # Пустое значение для общих стратагем (Core)
    }
    
    # Типы стратагем, которые НЕ относятся к основному режиму
    excluded_modes = {
        'Boarding Actions',
        'Challenger',
        'Combat Patrol',
        'Crusade'
    }
    
    cards = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='|')
            
            for row in reader:
                # Обрабатываем BOM символ в названии ключа
                faction_key = 'faction_id'
                if '\ufefffaction_id' in row:
                    faction_key = '\ufefffaction_id'
                
                faction_name = row.get(faction_key, '').strip()
                stratagem_type = row.get('type', '').strip()
                
                # Проверяем, что это основной режим игры
                is_main_game = True
                for excluded in excluded_modes:
                    if stratagem_type.startswith(excluded):
                        is_main_game = False
                        break
                
                # Проверяем фракцию
                is_allowed_faction = faction_name in allowed_factions
                
                if is_main_game and is_allowed_faction:
                    # Извлекаем структурированную информацию из description
                    body_data = clean_html_and_extract_structure(
                        row.get('description', ''))
                    
                    # Определяем фракцию для отображения
                    faction_display = get_faction_display_name(faction_name)
                    
                    # Определяем цвет карты
                    color = get_stratagem_color(
                        row.get('name', ''),
                        row.get('turn', ''),
                        row.get('legend', '')
                    )
                    
                    # Создаем карточку в нужном формате
                    card = {
                        "title": row.get('name', '').strip(),
                        "faction": faction_display,
                        "color": color,
                        "body": body_data,
                        "cost": {
                            "cp": int(row['cp_cost']) if (
                                row.get('cp_cost') and 
                                row['cp_cost'].isdigit()
                            ) else 0
                        }
                    }
                    
                    cards.append(card)
    
    except FileNotFoundError:
        print(f"Файл {csv_file_path} не найден!")
        return
    except Exception as e:
        print(f"Ошибка при чтении CSV файла: {e}")
        return
    
    # Создаем структуру JSON файла
    json_data = {
        "cards": cards
    }
    
    # Записываем в JSON файл
    try:
        with open(output_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, ensure_ascii=False, indent=2)
        
        print(f"Успешно отфильтровано {len(cards)} стратагем в {output_file_path}")
        
        # Статистика по фракциям
        faction_count = {}
        for card in cards:
            faction = card['faction']
            faction_count[faction] = faction_count.get(faction, 0) + 1
        
        print("\nСтатистика по фракциям:")
        for faction, count in sorted(faction_count.items()):
            print(f"  {faction}: {count}")
            
    except Exception as e:
        print(f"Ошибка при записи JSON файла: {e}")


def get_faction_display_name(faction_name: str) -> str:
    """Возвращает читаемое имя фракции"""
    # Фракции уже имеют читаемые имена в CSV файле
    if not faction_name:
        return 'Core Stratagems'
    return faction_name


def get_stratagem_color(name: str, turn: str, legend: str) -> str:
    """
    Определяет цвет стратагемы на основе её назначения:
    - Красный: атакующие стратагемы
    - Зеленый: защитные/реакционные стратагемы
    - Синий: стратагемы, используемые на фазу
    """
    name_lower = name.lower()
    turn_lower = turn.lower()
    legend_lower = legend.lower()
    
    # Атакующие стратагемы (красный)
    attack_names = ['offensive', 'challenge', 'shock', 'grenade', 'strike', 'assault']
    attack_legends = ['attack', 'damage', 'wound', 'strike', 'ramming',
                      'hurl death', 'deadly duel', 'combat', 'kill']
    
    if (any(word in name_lower for word in attack_names) or
            any(word in legend_lower for word in attack_legends)):
        return "#d32f2f"  # красный
    
    # Защитные/реакционные стратагемы (зеленый)
    defensive_names = ['ground', 'bravery', 'intervention', 'overwatch',
                       'smokescreen', 'shield', 'cover', 'protect']
    defensive_legends = ['salvation', 'cover', 'survival', 'shield',
                         'protection', 'defend', 'drive back', 'veiled',
                         'defensive', 'reaction']
    
    if ("opponent" in turn_lower or
            any(word in name_lower for word in defensive_names) or
            any(word in legend_lower for word in defensive_legends)):
        return "#388e3c"  # зеленый
    
    # Стратагемы на фазу (синий)
    phase_names = ['re-roll', 'ingress', 'orders', 'command', 'tactical']
    phase_legends = ['command', 'fortune', 'strategy', 'hasten',
                     'intelligence', 'tactical', 'phase', 'turn']
    
    if (any(word in name_lower for word in phase_names) or
            any(word in legend_lower for word in phase_legends)):
        return "#1976d2"  # синий
    
    else:
        return "#757575"  # серый для неопределенных


def clean_html_and_extract_structure(html_text: str) -> Dict[str, str]:
    """
    Очищает HTML теги и извлекает структурированную информацию
    (WHEN, TARGET, EFFECT, RESTRICTIONS)
    """
    if not html_text:
        return {
            "when": "",
            "target": "",
            "effect": "",
            "restriction": ""
        }
    
    # Простая очистка HTML тегов
    import re
    
    # Удаляем HTML теги
    clean_text = re.sub(r'<[^>]+>', '', html_text)
    
    # Декодируем HTML entities
    clean_text = clean_text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    # Инициализируем структуру
    result = {
        "when": "",
        "target": "",
        "effect": "",
        "restriction": ""
    }
    
    # Ищем секции WHEN, TARGET, EFFECT, RESTRICTIONS
    patterns = {
        "when": r"WHEN:\s*(.*?)(?:TARGET:|$)",
        "target": r"TARGET:\s*(.*?)(?:EFFECT:|$)",
        "effect": r"EFFECT:\s*(.*?)(?:RESTRICTIONS:|$)",
        "restriction": r"RESTRICTIONS:\s*(.*?)$"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, clean_text, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()
            # Убираем лишние пробелы и переносы строк
            text = re.sub(r'\s+', ' ', text)
            result[key] = text
    
    return result


if __name__ == "__main__":
    csv_file = "Stratagems.csv"
    
    print("=== Анализ CSV файла ===")
    analyze_stratagems_csv(csv_file)
    
    print("\n=== Фильтрация стратагем ===")
    filter_stratagems_by_factions_and_mode(csv_file, "cards_data_filtered.json")