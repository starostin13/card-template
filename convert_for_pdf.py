#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конвертер формата карточек для генератора PDF
Преобразует формат с фракциями в формат, понятный генератору
"""
import json

def get_card_color(cp_cost: int) -> str:
    """Определяет цвет карточки на основе стоимости CP"""
    if cp_cost == 0:
        return "#4caf50"  # Зеленый для бесплатных
    elif cp_cost == 1:
        return "#2196f3"  # Синий для 1 CP
    elif cp_cost >= 2:
        return "#f44336"  # Красный для 2+ CP
    else:
        return "#9e9e9e"  # Серый по умолчанию

def convert_to_pdf_format():
    """Конвертирует карточки с фракциями в формат для PDF генератора"""
    
    # Загружаем отфильтрованные карточки (исключены указанные фракции)
    with open('cards_data_filtered_factions.json', 'r', encoding='utf-8') as f:
        source_cards = json.load(f)
    
    # Преобразуем в формат для PDF генератора
    converted_cards = []
    
    for card in source_cards:
        cp_cost = card["cp_cost"]
        converted_card = {
            "title": card["name"],
            "faction": card["faction"],
            "color": get_card_color(cp_cost),
            "body": {
                "when": card.get("when", ""),
                "target": card.get("target", ""),
                "effect": card.get("effect", ""),
                "restriction": card.get("restriction", "")
            },
            "cost": {"CP": cp_cost},  # Добавляем стоимость в правильном формате
            "language": card.get("language", "English"),
            "cp_cost": cp_cost,
            "type": card.get("type", "")
        }
        
        converted_cards.append(converted_card)
    
    # Сохраняем в правильном формате
    result = {
        "cards": converted_cards
    }
    
    with open('cards_data_for_pdf.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Конвертировано {len(converted_cards)} карточек")
    print(f"Сохранено в cards_data_for_pdf.json")
    
    # Показываем статистику по цветам
    color_stats = {}
    for card in converted_cards:
        color = card["color"]
        color_stats[color] = color_stats.get(color, 0) + 1
    
    print("\nСтатистика по цветам:")
    color_names = {
        "#4caf50": "Зеленый (0 CP)",
        "#2196f3": "Синий (1 CP)", 
        "#f44336": "Красный (2+ CP)",
        "#9e9e9e": "Серый (неопределенный)"
    }
    
    for color, count in color_stats.items():
        name = color_names.get(color, color)
        print(f"  {name}: {count} карточек")

if __name__ == "__main__":
    convert_to_pdf_format()