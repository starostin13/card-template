#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Фильтрация фракций - исключаем указанные фракции
"""
import json

def filter_factions():
    """Исключает указанные фракции из данных"""
    
    # Фракции для исключения (точные названия и возможные вариации)
    exclude_factions = {
        # Основные названия для исключения
        "Adeptus Mechanicus",
        "Astra Militarum", 
        "Agents of the Imperium",
        "Adepta Sororitas",
        "Emperor's Children",
        "Genestealer Cults",
        "Leagues of Votann",
        "Questoris Imperialis", 
        "Questoris Traitoris",
        "T'au Empire",
        "Tyranids",
        "World Eaters",
        
        # Возможные вариации названий в наших данных
        "Hammer of the Emperor",  # Astra Militarum
        "Army of Faith", "Champions of Faith", "Penitent Host",  # Adepta Sororitas
        "Biosanctic Broodsurge", "Final Day", "Outlander Claw",  # Genestealer Cults
        "Cult Unveiled", "Genespawn Onslaught", "Xenocreed Congregation",  # Genestealer Cults
        "Brood Brother Auxilia",  # Genestealer Cults
        "Brandfast Oathband", "Hearthband", "Hearthfyre Arsenal",  # Leagues of Votann
        "Needgaârd Oathband", "Hearthfire Strike", "Void Salvagers",  # Leagues of Votann
        "Imperial Knights", "Gate Warden Lance", "Questor Forgepact",  # Questoris Imperialis
        "Spearhead-At-Arms", "Valourstrike Lance", "Houndpack Lance",  # Questoris Imperialis
        "Infernal Lance", "Traitoris Lance", "Iconoclast Fiefdom",  # Questoris Traitoris
        "Auxiliary Cadre", "Experimental Prototype Cadre", "Kauyon",  # T'au Empire
        "Mont'ka", "Retaliation Cadre", "Kroot Hunting Pack",  # T'au Empire
        "Kroot Raiding Party", "Starfire Cadre",  # T'au Empire
        "Crusher Stampede", "Subterranean Assault", "Synaptic Nexus",  # Tyranids
        "Warrior Bioform Onslaught", "Assimilation Swarm", "Invasion Fleet",  # Tyranids
        "Unending Swarm", "Vanguard Onslaught", "Boarding Swarm",  # Tyranids
        "Biotide", "Tyranid Attack",  # Tyranids
        "Berzerker Warband", "Boarding Butchers", "Cult of Blood",  # World Eaters
        "Skullsworn",  # World Eaters
        
        # Adeptus Mechanicus вариации
        "Cohort Cybernetica", "Data-Psalm Conclave", "Haloscreed Battle Clade",
        "Explorator Maniple", "Electromartyrs", "Machine Cult", "Response Clade",
    }
    
    # Загружаем отфильтрованные данные основной игры
    with open('cards_data_main_game_only.json', 'r', encoding='utf-8') as f:
        all_cards = json.load(f)
    
    print("=== ИСКЛЮЧЕНИЕ ФРАКЦИЙ ===")
    print(f"Исходное количество карточек: {len(all_cards)}")
    
    # Фильтруем карточки
    filtered_cards = []
    excluded_cards = []
    
    for card in all_cards:
        faction = card.get('faction', '')
        
        if faction in exclude_factions:
            excluded_cards.append(card)
        else:
            filtered_cards.append(card)
    
    print(f"Карточек после фильтрации: {len(filtered_cards)}")
    print(f"Исключено карточек: {len(excluded_cards)}")
    print()
    
    # Статистика исключений по фракциям
    if excluded_cards:
        print("🚫 ИСКЛЮЧЕННЫЕ ФРАКЦИИ:")
        exclusion_stats = {}
        for card in excluded_cards:
            faction = card.get('faction', 'Unknown')
            exclusion_stats[faction] = exclusion_stats.get(faction, 0) + 1
        
        for faction, count in sorted(exclusion_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {faction}: {count} карточек")
        print()
    
    # Сохраняем отфильтрованные данные
    with open('cards_data_filtered_factions.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_cards, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Сохранено в cards_data_filtered_factions.json")
    
    # Анализируем что осталось
    print("\n=== ЧТО ОСТАЛОСЬ ===")
    faction_counts = {}
    language_counts = {'English': 0, 'Russian': 0}
    cp_counts = {}
    
    for card in filtered_cards:
        faction = card.get('faction', 'Unknown')
        language = card.get('language', 'Unknown')
        cp_cost = card.get('cp_cost', 0)
        
        faction_counts[faction] = faction_counts.get(faction, 0) + 1
        language_counts[language] = language_counts.get(language, 0) + 1
        cp_counts[cp_cost] = cp_counts.get(cp_cost, 0) + 1
    
    # Показываем оставшиеся фракции
    print("ОСТАВШИЕСЯ ФРАКЦИИ:")
    for faction, count in sorted(faction_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(filtered_cards)) * 100
        print(f"  {faction}: {count} карточек ({percentage:.1f}%)")
    
    print(f"\nЯЗЫКИ:")
    for lang, count in language_counts.items():
        if count > 0:
            percentage = (count / len(filtered_cards)) * 100
            print(f"  {lang}: {count} карточек ({percentage:.1f}%)")
    
    print(f"\nСТОИМОСТЬ CP:")
    for cp, count in sorted(cp_counts.items()):
        percentage = (count / len(filtered_cards)) * 100
        print(f"  {cp} CP: {count} карточек ({percentage:.1f}%)")
    
    return len(filtered_cards), len(excluded_cards)

if __name__ == "__main__":
    filter_factions()