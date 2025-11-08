#!/usr/bin/env python3
"""
Validate translations according to translation rules
"""

import json
import re


class TranslationValidator:
    """Validate card translations against defined rules."""
    
    def __init__(self):
        # Load rules
        with open('translation_rules.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)['translation_rules']
        
        self.phases = rules['do_not_translate']['game_phases']
        self.steps = rules['do_not_translate']['game_steps']
        self.uppercase_examples = rules['do_not_translate']['uppercase_terms']['examples']
        
        # Compile patterns
        self.phase_pattern = re.compile('|'.join(re.escape(p) for p in self.phases))
        self.uppercase_pattern = re.compile(r'\b[A-Z]{2,}\b')
    
    def check_text(self, text, field_name="text"):
        """Check if text follows translation rules."""
        issues = []
        
        # Check if game phases are preserved
        for phase in self.phases:
            if phase.lower() in text.lower() and phase not in text:
                issues.append(f"⚠ {field_name}: Фаза '{phase}' должна быть на английском")
        
        # Check for translated uppercase terms
        cyrillic_uppercase = re.findall(r'\b[А-ЯЁ]{2,}\b', text)
        for term in cyrillic_uppercase:
            if term not in ['ТРАНСПОРТ', 'ПЕРСОНАЖ', 'ПЕХОТНЫЙ', 'ШАГОХОД']:
                issues.append(f"⚠ {field_name}: Термин '{term}' возможно не должен быть переведен")
        
        return issues
    
    def validate_card(self, card, card_index):
        """Validate a single card."""
        issues = []
        title = card.get('title', 'Unknown')
        
        print(f"\n{'='*60}")
        print(f"Проверка карточки #{card_index}: {title}")
        print('='*60)
        
        # Check title (should be English)
        if 'title' in card:
            if any(ord(c) > 127 for c in card['title']):
                issues.append(f"❌ Заголовок должен быть на английском: '{card['title']}'")
        
        # Check body fields
        body = card.get('body', {})
        
        for field in ['when', 'target', 'effect', 'restriction']:
            if field in body:
                text = body[field]
                field_issues = self.check_text(text, field)
                issues.extend(field_issues)
        
        # Display results
        if issues:
            print(f"🔍 Найдено {len(issues)} проблем:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("✅ Карточка соответствует правилам перевода")
        
        return issues
    
    def validate_file(self, filename):
        """Validate all cards in a JSON file."""
        print(f"\n{'#'*60}")
        print(f"# Проверка файла: {filename}")
        print(f"{'#'*60}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cards = data.get('cards', [])
        print(f"\nВсего карточек: {len(cards)}")
        
        # Find Russian cards
        russian_cards = []
        for i, card in enumerate(cards):
            when_text = card.get('body', {}).get('when', '')
            if when_text and any(ord(c) > 127 for c in when_text):
                russian_cards.append((i, card))
        
        print(f"Карточек на русском: {len(russian_cards)}")
        
        all_issues = []
        for i, card in russian_cards[:5]:  # Check first 5 Russian cards
            issues = self.validate_card(card, i+1)
            all_issues.extend(issues)
        
        print(f"\n{'='*60}")
        print(f"ИТОГО:")
        print(f"  Проверено: {min(5, len(russian_cards))} карточек")
        print(f"  Найдено проблем: {len(all_issues)}")
        print('='*60)
        
        return all_issues


def main():
    """Main function."""
    validator = TranslationValidator()
    
    print("🔍 Валидатор переводов Warhammer 40K")
    print("Проверка соответствия правилам перевода")
    print()
    
    # Validate cards_data.json
    issues = validator.validate_file('cards_data.json')
    
    if not issues:
        print("\n✅ Все проверенные карточки соответствуют правилам!")
    else:
        print(f"\n⚠ Обнаружено {len(issues)} несоответствий правилам перевода")
        print("📖 См. подробности выше")
        print("📄 Правила перевода: TRANSLATION_RULES.md")


if __name__ == '__main__':
    main()
