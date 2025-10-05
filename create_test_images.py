#!/usr/bin/env python3
"""
Script to create simple test images for card generation testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename, color, text, size=(200, 150)):
    """Create a simple colored test image with text."""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill='white', font=font)
    
    # Save image
    img.save(filename)
    print(f"Created test image: {filename}")

def main():
    """Create test images for the card examples."""
    
    # Create test images
    test_images = [
        ("lightning.jpg", (255, 100, 100), "LIGHTNING"),
        ("forest_guardian.jpg", (100, 200, 100), "FOREST"),
        ("fireball.jpg", (255, 150, 50), "FIREBALL")
    ]
    
    for filename, color, text in test_images:
        create_test_image(filename, color, text)
    
    print("All test images created successfully!")

if __name__ == '__main__':
    main()