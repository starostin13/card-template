#!/usr/bin/env python3
"""
Faction Logo Generator

This script creates simple faction logos for Warhammer 40k stratagems.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_faction_logo(text, background_color, text_color, size=(40, 40), output_path=None):
    """
    Create a simple faction logo with text.
    
    Args:
        text: Text to display on logo
        background_color: Background color (hex or tuple)
        text_color: Text color (hex or tuple)
        size: Logo size tuple (width, height)
        output_path: Path to save the logo
    """
    # Create image
    img = Image.new('RGBA', size, background_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default if not available
    try:
        # Try to find Arial font
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf", 
            "arial.ttf",
            "/System/Library/Fonts/Arial.ttf"  # macOS
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 12)
                break
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw border
    draw.rectangle([1, 1, size[0]-2, size[1]-2], outline=text_color, width=2)
    
    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)
    
    if output_path:
        img.save(output_path)
        print(f"Created logo: {output_path}")
    
    return img

def generate_all_faction_logos():
    """Generate logos for all factions."""
    
    # Create logos directory
    os.makedirs('faction_logos', exist_ok=True)
    
    # Faction definitions
    factions = {
        "Общие стратагемы": {
            "text": "CORE",
            "bg_color": "#2c3e50",
            "text_color": "#ffffff",
            "filename": "general.png"
        },
        "Абордаж": {
            "text": "BOARD", 
            "bg_color": "#8b0000",
            "text_color": "#ffffff",
            "filename": "boarding.png"
        },
        "Претендент": {
            "text": "CHAL",
            "bg_color": "#4b0082", 
            "text_color": "#ffffff",
            "filename": "challenger.png"
        },
        "Базовые стратагемы": {
            "text": "BASE",
            "bg_color": "#228b22",
            "text_color": "#ffffff", 
            "filename": "core.png"
        },
        # Дополнительные фракции для будущего расширения
        "Adeptus Astartes": {
            "text": "SM",
            "bg_color": "#1e40af",
            "text_color": "#ffffff",
            "filename": "space_marines.png"
        },
        "Chaos": {
            "text": "CHAOS",
            "bg_color": "#dc2626",
            "text_color": "#ffffff",
            "filename": "chaos.png" 
        },
        "Imperial Guard": {
            "text": "IG",
            "bg_color": "#059669",
            "text_color": "#ffffff",
            "filename": "imperial_guard.png"
        },
        "Orks": {
            "text": "ORKS",
            "bg_color": "#16a34a", 
            "text_color": "#000000",
            "filename": "orks.png"
        },
        "Necrons": {
            "text": "NEC",
            "bg_color": "#000000",
            "text_color": "#00ff00",
            "filename": "necrons.png"
        },
        "Tyranids": {
            "text": "TYR",
            "bg_color": "#7c2d12",
            "text_color": "#ffffff",
            "filename": "tyranids.png"
        },
        "Eldar": {
            "text": "ELD",
            "bg_color": "#0891b2",
            "text_color": "#ffffff", 
            "filename": "eldar.png"
        },
        "Adeptus Custodes": {
            "text": "CUST",
            "bg_color": "#fbbf24",
            "text_color": "#000000",
            "filename": "custodes.png"
        },
        "Grey Knights": {
            "text": "GK",
            "bg_color": "#9ca3af",
            "text_color": "#ffffff",
            "filename": "grey_knights.png"
        },
        "Death Guard": {
            "text": "DG",
            "bg_color": "#4b5563",
            "text_color": "#22c55e",
            "filename": "death_guard.png"
        },
        "Questoris Imperialis": {
            "text": "KNIGHT",
            "bg_color": "#92400e",
            "text_color": "#ffffff",
            "filename": "imperial_knights.png"
        }
    }
    
    # Generate all logos
    for faction_name, config in factions.items():
        output_path = os.path.join('faction_logos', config['filename'])
        create_faction_logo(
            text=config['text'],
            background_color=config['bg_color'],
            text_color=config['text_color'],
            size=(40, 40),
            output_path=output_path
        )
    
    print(f"Generated {len(factions)} faction logos in ./faction_logos/")

if __name__ == "__main__":
    generate_all_faction_logos()