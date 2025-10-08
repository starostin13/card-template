#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для конвертации Core стратагем из Stratagems.csv в формат cards_data.json
"""

import csv
import json
import re
from bs4 import BeautifulSoup
from typing import Dict


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
    
    # Используем BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Извлекаем текст без HTML тегов
    clean_text = soup.get_text()
    
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
    attack_names = ['offensive', 'challenge', 'shock', 'grenade']
    attack_legends = ['attack', 'damage', 'wound', 'strike', 'ramming',
                      'hurl death', 'deadly duel']
    
    if (any(word in name_lower for word in attack_names) or
            any(word in legend_lower for word in attack_legends)):
        return "#d32f2f"  # красный
    
    # Защитные/реакционные стратагемы (зеленый)
    defensive_names = ['ground', 'bravery', 'intervention', 'overwatch',
                       'smokescreen']
    defensive_legends = ['salvation', 'cover', 'survival', 'shield',
                         'protection', 'defend', 'drive back', 'veiled']
    
    if ("opponent" in turn_lower or
            any(word in name_lower for word in defensive_names) or
            any(word in legend_lower for word in defensive_legends)):
        return "#388e3c"  # зеленый
    
    # Стратагемы на фазу (синий)
    phase_names = ['re-roll', 'ingress', 'orders']
    phase_legends = ['command', 'fortune', 'strategy', 'hasten',
                     'intelligence']
    
    if (any(word in name_lower for word in phase_names) or
            any(word in legend_lower for word in phase_legends)):
        return "#1976d2"  # синий
    
    else:
        return "#757575"  # серый для неопределенных


def convert_core_stratagems_to_json(csv_file_path: str, output_file_path: str):
    """
    Конвертирует Core стратагемы из CSV в JSON формат cards_data
    """
    cards = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Используем pipe как разделитель
            reader = csv.DictReader(csvfile, delimiter='|')
            
            for row in reader:
                # Проверяем, что тип начинается с "Core"
                if row['type'] and row['type'].strip().startswith('Core'):
                    # Извлекаем структурированную информацию из description
                    body_data = clean_html_and_extract_structure(
                        row['description'])
                    
                    # Создаем карточку в нужном формате
                    card = {
                        "title": row['name'].strip() if row['name'] else "",
                        "color": get_stratagem_color(
                            row['name'] if row['name'] else "",
                            row['turn'] if row['turn'] else "",
                            row['legend'] if row['legend'] else ""
                        ),
                        "body": body_data,
                        "cost": {
                            "cp": (int(row['cp_cost'])
                                   if (row['cp_cost'] and
                                       row['cp_cost'].isdigit())
                                   else 0),
                            "turn": (row['turn'].strip()
                                     if row['turn'] else ""),
                            "phase": (row['phase'].strip()
                                      if row['phase'] else "")
                        },
                        "type": row['type'].strip() if row['type'] else "",
                        "legend": (row['legend'].strip()
                                   if row['legend'] else "")
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
        
        print(f"Успешно конвертировано {len(cards)} Core стратагем в "
              f"{output_file_path}")
        
        # Выводим список конвертированных стратагем
        print("\nКонвертированные стратагемы:")
        for i, card in enumerate(cards, 1):
            print(f"{i}. {card['title']} ({card['type']})")
            
    except Exception as e:
        print(f"Ошибка при записи JSON файла: {e}")


if __name__ == "__main__":
    # Пути к файлам
    csv_file = "Stratagems.csv"
    json_file = "cards_data.json"
    
    # Конвертируем данные
    convert_core_stratagems_to_json(csv_file, json_file)
