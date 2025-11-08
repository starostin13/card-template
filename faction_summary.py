#!/usr/bin/env python3
"""
Faction Logo Summary

This script provides an overview of the faction logo implementation.
"""

import os
import json

def print_faction_summary():
    """Print summary of faction logos and their usage."""
    
    print("=" * 60)
    print("FACTION LOGO IMPLEMENTATION SUMMARY")
    print("=" * 60)
    
    # Check faction logos directory
    logos_dir = "faction_logos"
    if os.path.exists(logos_dir):
        logo_files = [f for f in os.listdir(logos_dir) if f.endswith('.png')]
        print(f"\n✅ Created {len(logo_files)} faction logos:")
        for logo_file in sorted(logo_files):
            faction_name = logo_file.replace('.png', '').replace('_', ' ').title()
            print(f"   • {logo_file} ({faction_name})")
    else:
        print(f"\n❌ Logos directory not found: {logos_dir}")
    
    # Check cards data for faction usage
    cards_file = "cards_data.json"
    if os.path.exists(cards_file):
        with open(cards_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        faction_counts = {}
        for card in data["cards"]:
            faction = card.get('faction', 'No Faction')
            faction_counts[faction] = faction_counts.get(faction, 0) + 1
        
        print(f"\n📊 Faction usage in {len(data['cards'])} cards:")
        for faction, count in sorted(faction_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {faction}: {count} cards")
    
    # Check generated PDFs
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and 'logo' in f]
    if pdf_files:
        print(f"\n📄 Generated PDFs with logos:")
        for pdf_file in sorted(pdf_files):
            file_size = os.path.getsize(pdf_file) / (1024 * 1024)  # MB
            print(f"   • {pdf_file} ({file_size:.1f} MB)")
    
    print(f"\n🎨 Logo Design Features:")
    print("   • 40x40 pixel PNG format")
    print("   • Transparent background support")
    print("   • Faction-specific colors and abbreviations")
    print("   • Positioned symmetrically to CP cost")
    print("   • Automatic fallback to default if logo missing")
    
    print(f"\n🔧 Implementation Details:")
    print("   • Logos integrated into card_generator.py")
    print("   • Added _draw_faction_logo() method")
    print("   • Position: top-left corner (0.3 inch from edge)")
    print("   • Size: 0.24 inch (24 points)")
    print("   • Error handling for missing logo files")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_faction_summary()