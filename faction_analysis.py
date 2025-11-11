#!/usr/bin/env python3
"""
Детальная статистика по фракциям для очищенного файла карточек
"""

import json
from collections import Counter, defaultdict

def analyze_by_factions(json_file):
    """Анализ карточек по фракциям с детальной статистикой"""
    
    # Загружаем данные
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cards = data.get('cards', [])
    total_cards = len(cards)
    
    print(f"📊 ДЕТАЛЬНАЯ СТАТИСТИКА ПО ФРАКЦИЯМ")
    print(f"{'='*60}")
    print(f"Общее количество карточек: {total_cards}")
    print()
    
    # Анализ по фракциям
    faction_stats = defaultdict(lambda: {
        'total': 0,
        'cp_0_1': 0,
        'cp_2_plus': 0,
        'english': 0,
        'russian': 0,
        'cards_by_cp': Counter()
    })
    
    for card in cards:
        title = card.get('title', '')
        faction = card.get('faction', 'Неизвестная фракция')
        cost_data = card.get('cost', {})
        cp_cost = sum(cost_data.values()) if cost_data else 0
        
        # Определяем язык
        has_cyrillic = any(ord(char) > 127 for char in title)
        language = 'russian' if has_cyrillic else 'english'
        
        # Обновляем статистику
        stats = faction_stats[faction]
        stats['total'] += 1
        stats[language] += 1
        stats['cards_by_cp'][cp_cost] += 1
        
        if cp_cost <= 1:
            stats['cp_0_1'] += 1
        else:
            stats['cp_2_plus'] += 1
    
    # Сортируем фракции по количеству карточек
    sorted_factions = sorted(faction_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    
    print(f"📈 СТАТИСТИКА ПО ФРАКЦИЯМ:")
    print(f"{'-'*80}")
    print(f"{'ФРАКЦИЯ':<25} | {'ВСЕГО':<6} | {'EN':<4} | {'RU':<4} | {'CP≤1':<6} | {'CP≥2':<6} | {'РАСПРЕДЕЛЕНИЕ ПО CP'}")
    print(f"{'-'*80}")
    
    for faction, stats in sorted_factions:
        # Форматируем распределение по CP
        cp_distribution = []
        for cp in sorted(stats['cards_by_cp'].keys()):
            count = stats['cards_by_cp'][cp]
            cp_distribution.append(f"CP{cp}:{count}")
        
        cp_dist_str = " ".join(cp_distribution)
        if len(cp_dist_str) > 30:
            cp_dist_str = cp_dist_str[:27] + "..."
        
        print(f"{faction:<25} | {stats['total']:<6} | {stats['english']:<4} | {stats['russian']:<4} | "
              f"{stats['cp_0_1']:<6} | {stats['cp_2_plus']:<6} | {cp_dist_str}")
    
    print(f"{'-'*80}")
    
    # Общая статистика
    total_english = sum(stats['english'] for stats in faction_stats.values())
    total_russian = sum(stats['russian'] for stats in faction_stats.values())
    total_cp_0_1 = sum(stats['cp_0_1'] for stats in faction_stats.values())
    total_cp_2_plus = sum(stats['cp_2_plus'] for stats in faction_stats.values())
    
    print(f"\n💡 ОБЩАЯ СТАТИСТИКА:")
    print(f"{'-'*40}")
    print(f"Общее количество фракций: {len(faction_stats)}")
    print(f"Карточек на английском: {total_english} ({total_english/total_cards*100:.1f}%)")
    print(f"Карточек на русском: {total_russian} ({total_russian/total_cards*100:.1f}%)")
    print(f"Карточек CP 0-1: {total_cp_0_1} ({total_cp_0_1/total_cards*100:.1f}%)")
    print(f"Карточек CP 2+: {total_cp_2_plus} ({total_cp_2_plus/total_cards*100:.1f}%)")
    
    # Топ-5 фракций
    print(f"\n🏆 ТОП-5 ФРАКЦИЙ ПО КОЛИЧЕСТВУ КАРТОЧЕК:")
    print(f"{'-'*50}")
    for i, (faction, stats) in enumerate(sorted_factions[:5], 1):
        percentage = (stats['total'] / total_cards) * 100
        print(f"{i}. {faction}: {stats['total']} карточек ({percentage:.1f}%)")
    
    # Анализ эффективности дублирования
    print(f"\n🔍 АНАЛИЗ ДУБЛИРОВАНИЯ:")
    print(f"{'-'*40}")
    
    # Подсчитаем теоретическое количество уникальных карточек
    theoretical_unique = (total_cp_0_1 // 2) + total_cp_2_plus // 2
    print(f"Теоретическое количество уникальных стратагемм: ~{theoretical_unique}")
    print(f"Текущее количество карточек: {total_cards}")
    print(f"Коэффициент дублирования: {total_cards/theoretical_unique:.2f}")
    
    return faction_stats

if __name__ == "__main__":
    analyze_by_factions("cards_data_cleaned.json")