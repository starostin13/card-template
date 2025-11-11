#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление cards_data.json с отфильтрованными данными
"""
import json

def update_cards_data_json():
    """Обновляет cards_data.json с отфильтрованными данными"""
    
    # Загружаем отфильтрованные карточки
    with open('cards_data_filtered_factions.json', 'r', encoding='utf-8') as f:
        filtered_cards = json.load(f)
    
    # Конвертируем в старый формат для cards_data.json
    converted_cards = []
    
    for card in filtered_cards:
        cp_cost = card.get('cp_cost', 0)
        
        # Определяем цвет карточки
        if cp_cost == 0:
            color = "#4caf50"  # Зеленый
        elif cp_cost == 1:
            color = "#2196f3"  # Синий
        else:
            color = "#f44336"  # Красный
        
        converted_card = {
            "title": card.get('name', ''),
            "faction": card.get('faction', ''),
            "color": color,
            "body": {
                "when": card.get('when', ''),
                "target": card.get('target', ''),
                "effect": card.get('effect', ''),
                "restriction": card.get('restriction', '')
            },
            "cost": {
                "cp": cp_cost
            },
            "language": card.get('language', 'English'),
            "type": card.get('type', '')
        }
        
        converted_cards.append(converted_card)
    
    # Сохраняем в формате cards_data.json
    result = {
        "cards": converted_cards
    }
    
    with open('cards_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Обновлен cards_data.json с {len(converted_cards)} карточками")
    print("🚫 Исключенные фракции:")
    print("  • Adeptus Mechanicus")
    print("  • Astra Militarum (Hammer of the Emperor)")
    print("  • Agents of the Imperium") 
    print("  • Adepta Sororitas (Army/Champions/Penitent)")
    print("  • Emperor's Children")
    print("  • Genestealer Cults")
    print("  • Leagues of Votann")
    print("  • Questoris Imperialis/Traitoris")
    print("  • T'au Empire")
    print("  • Tyranids")
    print("  • World Eaters")

if __name__ == "__main__":
    update_cards_data_json()