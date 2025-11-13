#!/usr/bin/env python3
"""
Анализ карточек - создание сводной таблицы для проверки дубликатов и статистики
"""

import json
from collections import Counter, defaultdict

def analyze_cards(json_file):
    """Анализ карточек и создание сводной таблицы"""
    
    # Загружаем данные
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cards = data.get('cards', [])
    total_cards = len(cards)
    
    print(f"📊 СВОДНАЯ СТАТИСТИКА ПО КАРТОЧКАМ")
    print(f"{'='*50}")
    print(f"Общее количество карточек: {total_cards}")
    print()
    
    # Статистика по фракциям
    faction_stats = Counter()
    title_stats = Counter()
    language_stats = {'english': 0, 'russian': 0, 'mixed': 0}
    cost_stats = Counter()
    
    # Детальный анализ дубликатов
    duplicates = defaultdict(list)
    
    for idx, card in enumerate(cards):
        title = card.get('title', '')
        faction = card.get('faction', 'Неизвестная фракция')
        cost_data = card.get('cost', {})
        total_cost = sum(cost_data.values()) if cost_data else 0
        
        # Статистика по фракциям
        faction_stats[faction] += 1
        
        # Статистика по названиям
        title_stats[title] += 1
        
        # Статистика по стоимости
        cost_stats[total_cost] += 1
        
        # Анализ языка
        has_cyrillic = any(ord(char) > 127 for char in title)
        has_latin = any(ord(char) < 127 and char.isalpha() for char in title)
        
        if has_cyrillic and has_latin:
            language_stats['mixed'] += 1
        elif has_cyrillic:
            language_stats['russian'] += 1
        else:
            language_stats['english'] += 1
        
        # Поиск дубликатов
        duplicates[title].append({
            'index': idx,
            'faction': faction,
            'cost': total_cost
        })
    
    # Выводим статистику по фракциям
    print(f"📈 СТАТИСТИКА ПО ФРАКЦИЯМ:")
    print(f"{'-'*50}")
    for faction, count in faction_stats.most_common():
        percentage = (count / total_cards) * 100
        print(f"{faction:<25} | {count:>4} карточек ({percentage:5.1f}%)")
    
    print()
    
    # Статистика по языкам
    print(f"🌐 СТАТИСТИКА ПО ЯЗЫКАМ:")
    print(f"{'-'*30}")
    for lang, count in language_stats.items():
        percentage = (count / total_cards) * 100
        lang_name = {'english': 'Английский', 'russian': 'Русский', 'mixed': 'Смешанный'}[lang]
        print(f"{lang_name:<12} | {count:>4} карточек ({percentage:5.1f}%)")
    
    print()
    
    # Статистика по стоимости
    print(f"💰 СТАТИСТИКА ПО СТОИМОСТИ (CP):")
    print(f"{'-'*35}")
    for cost in sorted(cost_stats.keys()):
        count = cost_stats[cost]
        percentage = (count / total_cards) * 100
        print(f"CP {cost:<2} | {count:>4} карточек ({percentage:5.1f}%)")
    
    print()
    
    # Анализ дубликатов
    print(f"🔍 АНАЛИЗ ДУБЛИКАТОВ:")
    print(f"{'-'*50}")
    
    exact_duplicates = {title: entries for title, entries in duplicates.items() if len(entries) > 1}
    
    if exact_duplicates:
        print(f"Найдено {len(exact_duplicates)} названий с дубликатами:")
        print()
        
        for title, entries in sorted(exact_duplicates.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"📝 '{title}' - {len(entries)} копий:")
            for entry in entries[:5]:  # Показываем первые 5 копий
                print(f"   ├─ Индекс {entry['index']}: {entry['faction']} (CP: {entry['cost']})")
            if len(entries) > 5:
                print(f"   └─ ... и еще {len(entries) - 5} копий")
            print()
    else:
        print("✅ Точных дубликатов по названию не найдено!")
    
    # Топ-10 самых частых названий
    print(f"🏆 ТОП-10 САМЫХ ЧАСТЫХ НАЗВАНИЙ:")
    print(f"{'-'*45}")
    for title, count in title_stats.most_common(10):
        if count > 1:
            print(f"{title:<30} | {count:>2} раз")
    
    print()
    
    # Рекомендации
    print(f"💡 РЕКОМЕНДАЦИИ:")
    print(f"{'-'*20}")
    
    total_duplicates = sum(count - 1 for count in title_stats.values() if count > 1)
    if total_duplicates > 0:
        print(f"⚠️  Можно удалить {total_duplicates} дубликатов")
        print(f"   Останется: {total_cards - total_duplicates} уникальных карточек")
    else:
        print("✅ Дубликатов не обнаружено")
    
    if language_stats['mixed'] > 0:
        print(f"⚠️  {language_stats['mixed']} карточек имеют смешанный язык")
    
    return {
        'total_cards': total_cards,
        'faction_stats': faction_stats,
        'title_stats': title_stats,
        'duplicates': exact_duplicates,
        'language_stats': language_stats,
        'cost_stats': cost_stats
    }

if __name__ == "__main__":
    analyze_cards("cards_data.json")