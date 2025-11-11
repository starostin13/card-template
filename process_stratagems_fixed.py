#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный процессор стратагемм с правильным определением фракций
Извлекает фракции из типа стратагемы вместо faction_id
"""
import csv
import json
import re
import html

def clean_html(text: str) -> str:
    """Очищает HTML теги и декодирует HTML entities"""
    if not text:
        return text
    
    # Удаляем HTML теги
    clean_text = re.sub(r'<[^>]+>', '', text)
    # Декодируем HTML entities
    clean_text = html.unescape(clean_text)
    # Удаляем лишние пробелы
    clean_text = ' '.join(clean_text.split())
    
    return clean_text

def extract_faction_from_type(stratagem_type: str) -> str:
    """Извлекает фракцию из типа стратагемы"""
    if not stratagem_type:
        return "Общие стратагемы"
    
    # Основные фракции и их ключевые слова
    faction_keywords = {
        # Империум
        "Auric Champions": "Adeptus Custodes",
        "Lions of the Emperor": "Adeptus Custodes", 
        "Skitarii Hunter Cohort": "Adeptus Mechanicus",
        "Armoured Warhost": "Adeptus Mechanicus",
        "Librarius Conclave": "Adeptus Astartes",
        "Champions of Fenris": "Space Wolves",
        "Saga of the Bold": "Space Wolves",
        "Bringers of Flame": "Imperial Fists",
        "Lions of": "Dark Angels",
        "Blood Legion": "Blood Angels",
        "Scintillating Legion": "Grey Knights",
        
        # Хаос
        "Lords of Dread": "Chaos Space Marines",
        "Creations of Bile": "Chaos Space Marines",
        "Goretrack Onslaught": "Khorne",
        
        # Ксенос
        "Ghosts of the Webway": "Aeldari",
        "Infestation Swarm": "Tyranids",
        
        # Специальные режимы
        "Boarding Actions": "Boarding Actions",
        "Challenger": "Challenger",
        "Banishers": "Daemon Hunters",
        "Questoris Companions": "Imperial Knights",
        
        # Основные типы
        "Core": "Core Stratagems"
    }
    
    # Ищем соответствия
    stratagem_type_lower = stratagem_type.lower()
    for keyword, faction in faction_keywords.items():
        if keyword.lower() in stratagem_type_lower:
            return faction
    
    # Если не найдено, пытаемся извлечь из начала типа
    # Ищем паттерн "Название – Тип Стратагемы"
    if "–" in stratagem_type:
        faction_part = stratagem_type.split("–")[0].strip()
        if faction_part and len(faction_part) > 3:  # Игнорируем слишком короткие
            return faction_part
    
    return "Общие стратагемы"

def parse_description_structure(description: str) -> dict:
    """Парсит структуру описания стратагемы (WHEN/TARGET/EFFECT/RESTRICTIONS)"""
    if not description:
        return {"effect": ""}
    
    # Очищаем от HTML
    clean_desc = clean_html(description)
    
    result = {
        "when": "",
        "target": "", 
        "effect": "",
        "restriction": ""
    }
    
    # Ищем WHEN
    when_split = clean_desc.split('WHEN:', 1)
    if len(when_split) > 1:
        remaining = when_split[1]
        
        # Ищем TARGET
        target_split = remaining.split('TARGET:', 1)
        if len(target_split) > 1:
            result["when"] = target_split[0].strip()
            remaining = target_split[1]
            
            # Ищем EFFECT
            effect_split = remaining.split('EFFECT:', 1)
            if len(effect_split) > 1:
                result["target"] = effect_split[0].strip()
                remaining = effect_split[1]
                
                # Ищем RESTRICTIONS (если есть)
                restriction_split = remaining.split('RESTRICTIONS:', 1)
                if len(restriction_split) > 1:
                    result["effect"] = restriction_split[0].strip()
                    result["restriction"] = restriction_split[1].strip()
                else:
                    result["effect"] = remaining.strip()
            else:
                result["target"] = remaining.strip()
        else:
            result["when"] = remaining.strip()
    else:
        # Если нет четкой структуры, помещаем все в effect
        result["effect"] = clean_desc.strip()
    
    return result

def translate_stratagem_text(text: str, context: str = "") -> str:
    """Переводит текст стратагемы на русский язык"""
    if not text or not text.strip():
        return text
    
    # Базовые переводы (упрощенные для демонстрации)
    translations = {
        # Фазы
        "Your turn": "Ваш ход",
        "Either player's turn": "Ход любого игрока", 
        "Movement phase": "Фаза движения",
        "Shooting phase": "Фаза стрельбы",
        "Fight phase": "Фаза боя",
        "Command phase": "Фаза команд",
        "Any phase": "Любая фаза",
        
        # Базовые термины
        "WHEN:": "КОГДА:",
        "TARGET:": "ЦЕЛЬ:",
        "EFFECT:": "ЭФФЕКТ:",
        "RESTRICTIONS:": "ОГРАНИЧЕНИЯ:",
        
        # Частые фразы
        "One unit from your army": "Одно подразделение из вашей армии",
        "Until the end of the phase": "До конца фазы",
        "Hit roll": "Бросок попадания", 
        "Wound roll": "Бросок ранения",
        "Saving throw": "Спасательный бросок",
        "re-roll": "перебросить",
    }
    
    result = text
    for en, ru in translations.items():
        result = result.replace(en, ru)
    
    return result

def process_stratagems():
    """Обрабатывает файл CSV и создает JSON с карточками"""
    cards = []
    
    with open('Stratagems.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        
        for row in reader:
            # Получаем данные
            stratagem_id = row.get('id', '').strip()
            name = row.get('name', '').strip()
            stratagem_type = row.get('type', '').strip()
            cp_cost_str = row.get('cp_cost', '').strip()
            description = row.get('description', '').strip()
            
            if not name:
                continue
            
            try:
                cp_cost = int(cp_cost_str) if cp_cost_str else 0
            except ValueError:
                cp_cost = 0
            
            # Извлекаем фракцию из типа
            faction = extract_faction_from_type(stratagem_type)
            
            # Парсим структуру описания
            desc_parts = parse_description_structure(description)
            
            # Определяем количество копий на основе CP
            if cp_cost <= 1:
                english_copies = 2  # 2 английские копии для дешевых
                russian_copies = 2  # 2 русские копии для дешевых
            else:
                english_copies = 1  # 1 английская копия для дорогих
                russian_copies = 1  # 1 русская копия для дорогих
            
            # Создаем английские карточки
            for copy_num in range(english_copies):
                cards.append({
                    "id": f"{stratagem_id}_en_{copy_num + 1}",
                    "name": name,
                    "faction": faction,
                    "type": stratagem_type,
                    "cp_cost": cp_cost,
                    "when": desc_parts["when"],
                    "target": desc_parts["target"],
                    "effect": desc_parts["effect"],
                    "restriction": desc_parts["restriction"],
                    "language": "English"
                })
                
            # Создаем русские карточки
            for copy_num in range(russian_copies):
                cards.append({
                    "id": f"{stratagem_id}_ru_{copy_num + 1}",
                    "name": translate_stratagem_text(name, "name"),
                    "faction": faction, 
                    "type": translate_stratagem_text(stratagem_type, "type"),
                    "cp_cost": cp_cost,
                    "when": translate_stratagem_text(desc_parts["when"], "when"),
                    "target": translate_stratagem_text(desc_parts["target"], "target"),
                    "effect": translate_stratagem_text(desc_parts["effect"], "effect"),
                    "restriction": translate_stratagem_text(desc_parts["restriction"], "restriction"),
                    "language": "Russian"
                })
    
    # Сохраняем в JSON
    with open('cards_data_fixed_factions.json', 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    
    # Статистика
    print(f"Создано карточек: {len(cards)}")
    
    # Подсчет по фракциям
    faction_count = {}
    for card in cards:
        faction = card['faction']
        faction_count[faction] = faction_count.get(faction, 0) + 1
    
    print("\nРаспределение по фракциям:")
    for faction, count in sorted(faction_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {faction}: {count} карточек")

if __name__ == "__main__":
    process_stratagems()