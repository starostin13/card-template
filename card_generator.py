#!/usr/bin/env python3
"""
Card Template PDF Generator

This script generates a PDF file with multiple cards based on a JSON input file.
Each card has a similar design but with different content.
"""

import json
import argparse
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white


class CardGenerator:
    """Generate PDF cards from JSON data."""
    
    def __init__(self, page_size=letter):
        """
        Initialize the card generator.
        
        Args:
            page_size: The page size for the PDF (default: letter)
        """
        self.page_size = page_size
        self.page_width, self.page_height = page_size
        
        # Card dimensions
        self.card_width = 3.5 * inch
        self.card_height = 2 * inch
        self.card_margin = 0.5 * inch
        
        # Calculate cards per page
        self.cards_per_row = int((self.page_width - self.card_margin) / (self.card_width + self.card_margin))
        self.cards_per_col = int((self.page_height - self.card_margin) / (self.card_height + self.card_margin))
        self.cards_per_page = self.cards_per_row * self.cards_per_col
        
        # Colors
        self.bg_color = HexColor('#f0f0f0')
        self.border_color = HexColor('#333333')
        self.title_color = HexColor('#2c3e50')
        self.subtitle_color = HexColor('#7f8c8d')
        self.text_color = HexColor('#34495e')
        
    def load_cards_data(self, json_file):
        """
        Load card data from JSON file.
        
        Args:
            json_file: Path to the JSON file
            
        Returns:
            List of card dictionaries
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('cards', [])
    
    def draw_card(self, c, x, y, card_data):
        """
        Draw a single card on the canvas.
        
        Args:
            c: Canvas object
            x: X position for the card
            y: Y position for the card
            card_data: Dictionary containing card content
        """
        # Draw card background
        c.setFillColor(white)
        c.setStrokeColor(self.border_color)
        c.setLineWidth(2)
        c.roundRect(x, y, self.card_width, self.card_height, 10, stroke=1, fill=1)
        
        # Draw header bar
        c.setFillColor(self.title_color)
        c.roundRect(x, y + self.card_height - 0.5 * inch, self.card_width, 0.5 * inch, 10, stroke=0, fill=1)
        
        # Draw title
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        title = card_data.get('title', 'Card Title')
        c.drawCentredString(x + self.card_width / 2, y + self.card_height - 0.3 * inch, title)
        
        # Draw subtitle
        c.setFillColor(self.subtitle_color)
        c.setFont("Helvetica-Oblique", 10)
        subtitle = card_data.get('subtitle', '')
        if subtitle:
            c.drawCentredString(x + self.card_width / 2, y + self.card_height - 0.8 * inch, subtitle)
        
        # Draw description
        c.setFillColor(self.text_color)
        c.setFont("Helvetica", 9)
        description = card_data.get('description', '')
        if description:
            # Handle multi-line text
            lines = description.split('\n')
            text_y = y + self.card_height - 1.1 * inch
            for line in lines[:4]:  # Limit to 4 lines
                if text_y > y + 0.4 * inch:  # Ensure we don't overlap footer
                    c.drawString(x + 0.2 * inch, text_y, line[:50])  # Limit line length
                    text_y -= 0.15 * inch
        
        # Draw footer
        c.setFillColor(self.text_color)
        c.setFont("Helvetica", 8)
        footer = card_data.get('footer', '')
        if footer:
            c.drawCentredString(x + self.card_width / 2, y + 0.15 * inch, footer)
    
    def generate_pdf(self, json_file, output_file):
        """
        Generate PDF with cards from JSON data.
        
        Args:
            json_file: Path to input JSON file
            output_file: Path to output PDF file
        """
        # Load card data
        cards = self.load_cards_data(json_file)
        
        if not cards:
            raise ValueError("No cards found in JSON file")
        
        # Create PDF
        c = canvas.Canvas(output_file, pagesize=self.page_size)
        
        # Draw cards
        for idx, card_data in enumerate(cards):
            # Calculate position
            page_idx = idx % self.cards_per_page
            row = page_idx // self.cards_per_row
            col = page_idx % self.cards_per_row
            
            x = self.card_margin + col * (self.card_width + self.card_margin)
            y = self.page_height - self.card_margin - (row + 1) * (self.card_height + self.card_margin)
            
            # Draw the card
            self.draw_card(c, x, y, card_data)
            
            # Create new page if needed
            if (idx + 1) % self.cards_per_page == 0 and idx < len(cards) - 1:
                c.showPage()
        
        # Save PDF
        c.save()
        print(f"PDF generated successfully: {output_file}")
        print(f"Total cards: {len(cards)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate PDF cards from JSON data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python card_generator.py cards_data.json -o output.pdf
  python card_generator.py my_cards.json --page-size A4
        """
    )
    
    parser.add_argument(
        'input',
        help='Input JSON file containing card data'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='cards_output.pdf',
        help='Output PDF file (default: cards_output.pdf)'
    )
    
    parser.add_argument(
        '--page-size',
        choices=['letter', 'A4'],
        default='letter',
        help='Page size for the PDF (default: letter)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    # Set page size
    page_size = letter if args.page_size == 'letter' else A4
    
    # Generate PDF
    try:
        generator = CardGenerator(page_size=page_size)
        generator.generate_pdf(args.input, args.output)
        return 0
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
