#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный анализ фракций с группировкой
"""
import json
from collections import defaultdict

def analyze_fixed_factions():
    """Анализирует исправленные данные по фракциям"""
    
    with open('cards_data_fixed_factions.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    # Группировка фракций по основным армиям
    faction_groups = {
        "Imperium": [
            "Adeptus Custodes", "Talons Of The Emperor", "Adeptus Astartes", "Space Wolves", 
            "Blood Angels", "Imperial Fists", "Adeptus Mechanicus", "Grey Knights",
            "Army of Faith", "Champions of Faith", "Penitent Host", "Alien Hunters",
            "1st Company Task Force", "Angelic Inheritors", "Black Spear Task Force",
            "Company Of Hunters", "Emperor's Shield", "Inner Circle Task Force",
            "Liberator Assault Group", "The Angelic Host", "The Lost Brethren",
            "Lion's Blade Task Force", "Unforgiven Task Force", "Gladius Task Force",
            "Vanguard Spearhead", "Stormlance Task Force", "Firestorm Assault Force",
            "Imperial Knights", "Valourstrike Lance", "Gate Warden Lance",
            "Questor Forgepact", "Spearhead-At-Arms", "Hammer of the Emperor",
            "Combined Arms", "Rad-Zone Corps", "Siege Regiment", "Embarked Regiment",
            "Recon Element", "Imperialis Fleet", "Tempestus Boarding Regiment",
            "Boarding Strike", "Terminator Assault", "Pilum Strike Team",
            "Voidship's Company", "Interdiction Team", "Response Clade",
            "Machine Cult", "Electromartyrs", "Cohort Cybernetica",
            "Data-Psalm Conclave", "Haloscreed Battle Clade", "Explorator Maniple"
        ],
        "Chaos": [
            "Chaos Space Marines", "Demonic Incursion", "Daemon Hunters", "Cabal of Chaos",
            "Chaos Cult", "Deceptors", "Dread Talons", "Fellhammer Siege-Host",
            "Pactbound Zealots", "Renegade Raiders", "Soulforged Warpack",
            "Death Lord's Chosen", "Flyblown Host", "Shamblerot Vectorium",
            "Tallyband Summoners", "Skysplinter Assault", "Coterie of the Conceited",
            "Rapid Evisceration", "Slaanesh's Chosen", "Veterans of the Long War",
            "Legion of Excess", "Plague Legion", "Shadow Legion", "Champions of Contagion",
            "Mortarion's Hammer", "Virulent Vectorium", "Carnival of Excess",
            "Peerless Bladesmen", "Host of Ascension", "Daemonic Incursion",
            "Dread Carnival", "Infernal Onslaught", "Pandaemoniac Inferno",
            "Rotten and Rusted", "Champions of Chaos", "Infernal Reavers",
            "Underdeck Uprising", "Arch-Contaminators", "Vectors of Decay",
            "Berzerker Warband", "Possessed Slaughterband", "Cult of Blood",
            "Rubricae Phalanx", "Changehost of Deceit", "Grand Coven",
            "Hexwarp Thrallband", "Warpforged Cabal", "Warpmeld Pact",
            "Chosen Cabal", "Devoted Thralls", "Fateseekers", "Boarding Butchers",
            "Skullsworn", "Unclean Uprising", "Khorne", "Khorne Daemonkin",
            "Vessels of Wrath", "Traitoris Lance", "Infernal Lance", "Iconoclast Fiefdom"
        ],
        "Aeldari": [
            "Aeldari", "Aspect Host", "Guardian Battlehost", "Seer Council",
            "Spirit Conclave", "Warhost", "Windrider Host", "Devoted of Ynnead",
            "Khaine's Arrow", "Protector Host", "Star-dancer Masque",
            "Wraiths of the Void", "Realspace Raiders", "Reaper's Wager",
            "Mercurial Host", "Kabalite Corsairs", "Painbringers", 
            "Space Lane Raiders"
        ],
        "Tyranids": [
            "Tyranids", "Biosanctic Broodsurge", "Final Day", "Outlander Claw",
            "Crusher Stampede", "Subterranean Assault", "Synaptic Nexus",
            "Warrior Bioform Onslaught", "Assimilation Swarm", "Invasion Fleet",
            "Unending Swarm", "Vanguard Onslaught", "Brood Brother Auxilia",
            "Xenocreed Congregation", "Ship-killer Cult", "Cult Unveiled",
            "Genespawn Onslaught", "Biotide", "Boarding Swarm", "Tyranid Attack"
        ],
        "Tau Empire": [
            "Auxiliary Cadre", "Experimental Prototype Cadre", "Kauyon", "Mont'ka",
            "Retaliation Cadre", "Kroot Hunting Pack", "Kroot Raiding Party",
            "Starfire Cadre"
        ],
        "Orks": [
            "Bully Boyz", "Da Big Hunt", "Dread Mob", "Green Tide", "Kult of Speed",
            "Taktikal Brigade", "More Dakka!", "War Horde", "Deranged Outcasts",
            "Kaptin Killers", "Ramship Raiders"
        ],
        "Necrons": [
            "Awakened Dynasty", "Canoptek Court", "Hypercrypt Legion",
            "Starshatter Arsenal", "Canoptek Harvesters", "Tomb Ship Complement"
        ],
        "Leagues of Votann": [
            "Brandfast Oathband", "Hearthband", "Hearthfyre Arsenal",
            "Needgaârd Oathband", "Hearthfire Strike", "Void Salvagers"
        ],
        "Special/Core": [
            "Core Stratagems", "Общие стратагемы", "Challenger", "Boarding Actions",
            "Anvil Siege Force"
        ]
    }
    
    # Подсчет карточек по группам
    group_counts = defaultdict(int)
    faction_counts = defaultdict(int)
    
    for card in cards:
        faction = card['faction']
        faction_counts[faction] += 1
        
        # Определяем группу
        assigned_group = "Unassigned"
        for group_name, factions in faction_groups.items():
            if faction in factions:
                assigned_group = group_name
                break
        
        group_counts[assigned_group] += 1
    
    # Выводим результаты
    print("=== ФИНАЛЬНАЯ СТАТИСТИКА ПО ФРАКЦИЯМ ===")
    print(f"Общее количество карточек: {len(cards)}")
    print()
    
    print("=== РАСПРЕДЕЛЕНИЕ ПО ОСНОВНЫМ АРМИЯМ ===")
    total_assigned = 0
    for group, count in sorted(group_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(cards)) * 100
        print(f"{group}: {count} карточек ({percentage:.1f}%)")
        if group != "Unassigned":
            total_assigned += count
    
    print()
    print("=== ТОП-20 ФРАКЦИЙ ПО КОЛИЧЕСТВУ КАРТОЧЕК ===")
    for faction, count in sorted(faction_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        percentage = (count / len(cards)) * 100
        print(f"{faction}: {count} карточек ({percentage:.1f}%)")
    
    # Статистика по языкам
    print()
    print("=== РАСПРЕДЕЛЕНИЕ ПО ЯЗЫКАМ ===")
    lang_counts = defaultdict(int)
    for card in cards:
        lang_counts[card['language']] += 1
    
    for lang, count in lang_counts.items():
        percentage = (count / len(cards)) * 100
        print(f"{lang}: {count} карточек ({percentage:.1f}%)")
    
    # Статистика по стоимости CP
    print()
    print("=== РАСПРЕДЕЛЕНИЕ ПО СТОИМОСТИ CP ===")
    cp_counts = defaultdict(int)
    for card in cards:
        cp_counts[card['cp_cost']] += 1
    
    for cp, count in sorted(cp_counts.items()):
        percentage = (count / len(cards)) * 100
        print(f"{cp} CP: {count} карточек ({percentage:.1f}%)")
    
    # Оценка уникальных стратагемм
    unique_names = set()
    for card in cards:
        if card['language'] == 'English':  # Считаем только английские для подсчета уникальных
            unique_names.add(card['name'])
    
    print()
    print("=== ОЦЕНКА ДУБЛИРОВАНИЯ ===")
    print(f"Уникальных стратагемм (по названиям): ~{len(unique_names)}")
    print(f"Средний коэффициент дублирования: {len(cards) / len(unique_names):.2f}")

if __name__ == "__main__":
    analyze_fixed_factions()