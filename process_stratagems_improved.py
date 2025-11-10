#!/usr/bin/env python3
import csv
import json
import html
import re
from typing import Dict, List, Tuple

def clean_html_description(description: str) -> str:
    """Очищает HTML теги и преобразует в читаемый текст"""
    if not description:
        return ""
    
    # Удаляем HTML теги
    text = re.sub(r'<[^>]+>', '', description)
    # Декодируем HTML entities
    text = html.unescape(text)
    # Убираем лишние пробелы и переносы
    text = ' '.join(text.split())
    
    return text

def parse_description(description: str) -> Dict[str, str]:
    """Парсит описание стратагемы на компоненты when, target, effect, restriction"""
    if not description:
        return {"when": "", "target": "", "effect": "", "restriction": ""}
    
    # Очищаем HTML
    clean_desc = clean_html_description(description)
    
    result = {"when": "", "target": "", "effect": "", "restriction": ""}
    
    # Разбиваем по секциям
    sections = clean_desc.split('WHEN:')
    if len(sections) > 1:
        remaining = sections[1]
        
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
    
    # Расширенный словарь переводов для Warhammer 40k терминов
    translations = {
        # Фразы начала
        "Your ": "В вашу ",
        "Any phase": "Любая фаза",
        "Either player's turn": "Ход любого игрока",
        "Your turn": "Ваш ход", 
        "Opponent's turn": "Ход противника",
        "just after": "сразу после того как",
        "just before": "непосредственно перед",
        
        # Фазы игры
        "Command phase": "фазу команд",
        "Movement phase": "фазу движения",
        "Shooting phase": "фазу стрельбы", 
        "Charge phase": "фазу атаки",
        "Fight phase": "фазу боя",
        
        # Базовые игровые термины
        "Hit roll": "бросок попадания",
        "Wound roll": "бросок ранения",
        "Damage roll": "бросок урона", 
        "saving throw": "спасбросок",
        "Advance roll": "бросок движения",
        "Charge roll": "бросок атаки",
        "Battle-shock test": "тест боевого шока",
        "Hazardous test": "тест опасности",
        "Desperate Escape test": "тест отчаянного побега",
        "re-roll": "перебросить",
        "Normal move": "обычное движение",
        "Advance move": "ускоренное движение",  
        "Fall Back": "отступление",
        "mortal wound": "смертельная рана",
        "Engagement Range": "дистанция ближнего боя",
        "visible": "видимые",
        "Strategic Reserves": "стратегический резерв",
        "Pile-in": "сближение",
        "Consolidation move": "консолидация",
        "declare a charge": "объявить атаку",
        "invulnerable save": "неуязвимый спасбросок",
        "Benefit of Cover": "преимущество укрытия",
        
        # Единицы и типы
        "One unit from your army": "Одно подразделение из вашей армии",
        "One model in your unit": "Одну модель в вашем подразделении",
        "That unit from your army": "Это подразделение из вашей армии",
        "That unit or model from your army": "Это подразделение или модель из вашей армии",
        "Leader": "лидер",
        "Bodyguard": "телохранитель",
        "CHARACTER": "ПЕРСОНАЖ",
        "INFANTRY": "ПЕХОТА",
        "VEHICLE": "ТЕХНИКА",
        "MONSTER": "МОНСТР", 
        "WALKER": "ШАГАЮЩАЯ МАШИНА",
        
        # Способности оружия
        "[BLAST]": "[ВЗРЫВ]",
        "[HAZARDOUS]": "[ОПАСНОЕ]",
        "[LETHAL HITS]": "[СМЕРТОНОСНЫЕ ПОПАДАНИЯ]",
        "[SUSTAINED HITS 1]": "[НЕПРЕРЫВНЫЕ ПОПАДАНИЯ 1]",
        "[PRECISION]": "[ТОЧНОСТЬ]",
        
        # Временные рамки
        "Until the end of the phase": "До конца фазы",
        "Until the end of the turn": "До конца хода",
        "Until the start of your next": "До начала следующего",
        "Start of": "Начало",
        "End of": "Конец",
        
        # Общие фразы
        "that has not been selected": "которое не было выбрано",
        "that was selected as the target": "которое было выбрано целью",
        "within 6\"": "в пределах 6\"",
        "within Engagement Range": "в дистанции ближнего боя",
        "is equipped with a weapon": "экипировано оружием",
        "to shoot this phase": "для стрельбы в эту фазу",
        "to fight this phase": "для боя в эту фазу",
        "You cannot use this Stratagem more than once per battle": "Вы не можете использовать эту стратагему более одного раза за битву",
        "attacking model": "атакующая модель",
        "target unit": "целевое подразделение",
        "enemy unit": "вражеское подразделение",
        "friendly unit": "дружественное подразделение",
        "attacks made with that weapon": "атаки совершённые этим оружием",
        "can be allocated to models": "могут быть назначены моделям",
        "models that are not": "модели которые не",
        "for the purpose of that ability": "для цели этой способности",
        "when determining how many models": "при определении количества моделей",
        "include models": "включать модели",
        "are in the target unit": "находятся в целевом подразделении",
        "Select one model": "Выберите одну модель",
        "In addition": "Кроме того",
        "You re-roll": "Вы перебрасываете",
        "that roll, test or saving throw": "этот бросок, тест или спасбросок",
        "for an attack, model or unit from your army": "для атаки, модели или подразделения из вашей армии",
        "to determine the number of attacks made with a weapon": "чтобы определить количество атак оружием",
        "you have rolled the dice": "вы бросили кости",
        "you have made a": "вы совершили",
        "or just after": "или сразу после",
    }
    
    # Применяем переводы
    result = text
    for english, russian in translations.items():
        result = result.replace(english, russian)
    
    return result

def get_faction_name(faction_id: str) -> str:
    """Возвращает название фракции по ID"""
    faction_map = {
        "": "Общие стратагемы",
        "000009218": "Абордаж",
        "000010252": "Претендент", 
        "000008335": "Базовые стратагемы",
    }
    
    return faction_map.get(faction_id, f"Фракция {faction_id}")

def get_card_color(stratagem_type: str, cp_cost: int) -> str:
    """Определяет цвет карточки на основе типа стратагемы и стоимости"""
    if cp_cost == 0:
        return "#4caf50"  # Зеленый для бесплатных
    elif cp_cost == 1:
        return "#2196f3"  # Синий для 1 CP
    elif cp_cost >= 2:
        return "#f44336"  # Красный для 2+ CP
    else:
        return "#9e9e9e"  # Серый по умолчанию

def process_csv_to_cards(csv_file: str, output_file: str):
    """Обрабатывает CSV файл и создает карточки"""
    cards = []
    
    # Загружаем только первые карточки из исходного файла
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            original_cards = existing_data["cards"][:4]  # Сохраняем первые 4 оригинальные карточки
    except (FileNotFoundError, json.JSONDecodeError):
        original_cards = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        # Используем pipe как разделитель
        reader = csv.DictReader(f, delimiter='|')
        
        for row in reader:
            # Пропускаем пустые строки
            if not row.get('name') or not row.get('name').strip():
                continue
                
            name = row['name'].strip()
            cp_cost_str = row.get('cp_cost', '0').strip()
            cp_cost = int(cp_cost_str) if cp_cost_str and cp_cost_str.isdigit() else 0
            description = row.get('description', '').strip()
            faction_id = row.get('faction_id', '').strip()
            stratagem_type = row.get('type', '').strip()
            
            # Парсим описание
            body_parts = parse_description(description)
            
            # Создаем английскую версию
            english_card = {
                "title": name,
                "faction": get_faction_name(faction_id),
                "color": get_card_color(stratagem_type, cp_cost),
                "body": body_parts,
                "cost": {
                    "cp": cp_cost
                }
            }
            
            # Создаем русскую версию
            russian_card = {
                "title": translate_stratagem_text(name),
                "faction": get_faction_name(faction_id), 
                "color": get_card_color(stratagem_type, cp_cost),
                "body": {
                    "when": translate_stratagem_text(body_parts["when"]),
                    "target": translate_stratagem_text(body_parts["target"]),
                    "effect": translate_stratagem_text(body_parts["effect"]),
                    "restriction": translate_stratagem_text(body_parts["restriction"])
                },
                "cost": {
                    "cp": cp_cost
                }
            }
            
            # Добавляем карточки согласно правилам дублирования
            if cp_cost <= 1:
                # Для стоимости 0-1 CP добавляем по 2 копии
                cards.extend([english_card, english_card])
                cards.extend([russian_card, russian_card])
            else:
                # Для стоимости 2+ CP добавляем по 1 копии
                cards.append(english_card)
                cards.append(russian_card)
    
    # Создаем финальную структуру
    final_data = {
        "cards": original_cards + cards
    }
    
    # Сохраняем результат
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"Обработано стратагем: {len(cards)}")
    print(f"Общее количество карточек (включая оригинальные): {len(final_data['cards'])}")

if __name__ == "__main__":
    process_csv_to_cards("Stratagems.csv", "cards_data.json")