#!/usr/bin/env python3
"""
Check JSON encoding and content
"""

import json

print("=" * 60)
print("JSON ENCODING CHECK")
print("=" * 60)

# Read JSON
with open("cards_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Find first Russian card
for i, card in enumerate(data["cards"]):
    when_text = card["body"]["when"]
    
    # Check if it starts with Cyrillic
    if when_text and ord(when_text[0]) > 127:
        print(f"\n✓ Found Russian card #{i+1}: {card['title']}")
        print(f"  When (raw): {repr(when_text)}")
        print(f"  When (display): {when_text}")
        print(f"  First char code: {ord(when_text[0])}")
        print(f"  Is Cyrillic: {1040 <= ord(when_text[0]) <= 1103}")
        
        # Try to encode/decode
        try:
            utf8_bytes = when_text.encode('utf-8')
            print(f"  UTF-8 bytes: {utf8_bytes[:30]}...")
            decoded = utf8_bytes.decode('utf-8')
            print(f"  Decoded: {decoded[:50]}...")
        except Exception as e:
            print(f"  × Encoding error: {e}")
        
        break
else:
    print("\n× No Russian cards found")

print("\n" + "=" * 60)
