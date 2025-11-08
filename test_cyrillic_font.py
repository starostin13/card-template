#!/usr/bin/env python3
"""
Test Cyrillic support in PDF
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register Arial font
arial_regular = 'C:/Windows/Fonts/arial.ttf'
if os.path.exists(arial_regular):
    pdfmetrics.registerFont(TTFont('ArialUnicode', arial_regular))
    print("✓ Arial font registered")
else:
    print("× Arial font not found")
    exit(1)

# Create PDF
c = canvas.Canvas("cyrillic_test.pdf", pagesize=letter)
width, height = letter

# Test texts
test_texts = [
    ("English: Hello World", 100, 700),
    ("Русский: Привет Мир", 100, 650),
    ("Фаза стрельбы противника", 100, 600),
    ("Один ПЕХОТНЫЙ юнит", 100, 550),
    ("До конца фазы все модели", 100, 500),
]

# Draw texts
c.setFont('ArialUnicode', 16)
for text, x, y in test_texts:
    try:
        c.drawString(x, y, text)
        print(f"✓ Drew: {text}")
    except Exception as e:
        print(f"× Failed to draw '{text}': {e}")

c.save()
print("\n✓ PDF created: cyrillic_test.pdf")
print("Please open this file and check if Cyrillic text is visible")
