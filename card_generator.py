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
        
        # Card dimensions (120mm x 65mm)
        self.card_width = 65 * 0.0393701 * inch  # 65mm to inches
        self.card_height = 120 * 0.0393701 * inch  # 120mm to inches
        self.card_margin = 0  # No margins between cards
        
        # Calculate optimal layout
        self._calculate_optimal_layout()
        
        # Colors
        self.bg_color = HexColor('#f0f0f0')
        self.border_color = HexColor('#333333')
        self.title_color = HexColor('#2c3e50')
        self.subtitle_color = HexColor('#7f8c8d')
        self.text_color = HexColor('#34495e')
        
        # Mana colors
        self.mana_colors = {
            'red': HexColor('#d32f2f'),
            'blue': HexColor('#1976d2'),
            'green': HexColor('#388e3c'),
            'white': HexColor('#fafafa'),
            'black': HexColor('#424242'),
            'colorless': HexColor('#9e9e9e')
        }
    
    def _calculate_optimal_layout(self):
        """Calculate optimal card layout with rotation if beneficial."""
        # Normal orientation
        normal_per_row = int(self.page_width / self.card_width)
        normal_per_col = int(self.page_height / self.card_height)
        normal_total = normal_per_row * normal_per_col
        
        # Rotated orientation (90 degrees)
        rotated_per_row = int(self.page_width / self.card_height)
        rotated_per_col = int(self.page_height / self.card_width)
        rotated_total = rotated_per_row * rotated_per_col
        
        # Mixed layout (some normal, some rotated)
        # Try fitting normal cards first, then rotated in remaining space
        remaining_width = self.page_width - (normal_per_row * self.card_width)
        remaining_height = self.page_height - (normal_per_col * self.card_height)
        
        extra_rotated_in_width = int(remaining_width / self.card_height) * normal_per_col
        extra_rotated_in_height = int(remaining_height / self.card_width) * normal_per_row
        mixed_total = normal_total + max(extra_rotated_in_width, extra_rotated_in_height)
        
        # Choose best layout
        if mixed_total >= max(normal_total, rotated_total):
            self.layout_type = 'mixed'
            self.cards_per_row = normal_per_row
            self.cards_per_col = normal_per_col
            self.cards_per_page = mixed_total
            self.extra_rotated = max(extra_rotated_in_width, extra_rotated_in_height)
        elif rotated_total > normal_total:
            self.layout_type = 'rotated'
            self.cards_per_row = rotated_per_row
            self.cards_per_col = rotated_per_col
            self.cards_per_page = rotated_total
        else:
            self.layout_type = 'normal'
            self.cards_per_row = normal_per_row
            self.cards_per_col = normal_per_col
            self.cards_per_page = normal_total
        
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
    
    def draw_card(self, c, x, y, card_data, rotated=False):
        """
        Draw a single card on the canvas.
        
        Args:
            c: Canvas object
            x: X position for the card
            y: Y position for the card
            card_data: Dictionary containing card content
            rotated: Whether to draw the card rotated 90 degrees
        """
        if rotated:
            # Save current state and rotate
            c.saveState()
            c.translate(x + self.card_height, y)
            c.rotate(90)
            # Use swapped dimensions for rotated card
            card_w, card_h = self.card_height, self.card_width
            x, y = 0, 0
        else:
            card_w, card_h = self.card_width, self.card_height
        
        # Get card color
        card_color = card_data.get('color', '#2c3e50')  # Default to title_color if no color specified
        # Draw card background (light gray for better contrast)
        c.setFillColor(HexColor('#f5f5f5'))  # Light gray background
        c.setStrokeColor(self.border_color)
        c.setLineWidth(2)
        c.rect(x, y, card_w, card_h, stroke=1, fill=1)
        
        # Draw header bar with individual card color
        card_color = card_data.get('color', '#2c3e50')  # Default to title_color if no color specified
        c.setFillColor(HexColor(card_color))
        c.rect(x, y + card_h - 0.5 * inch, card_w, 0.5 * inch, stroke=0, fill=1)
        
        # Draw title
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        title = card_data.get('title', 'Card Title')
        c.drawCentredString(x + card_w / 2, y + card_h - 0.3 * inch, title)
        
        # Draw mana cost in top right corner
        cost_data = card_data.get('cost', {})
        if cost_data:
            cost_x = x + card_w - 0.3 * inch
            cost_y = y + card_h - 0.25 * inch
            total_cost = sum(cost_data.values())
            
            # Draw total cost circle (no color)
            c.setFillColor(white)
            c.setStrokeColor(black)
            c.circle(cost_x, cost_y, 0.12 * inch, stroke=1, fill=1)
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(cost_x, cost_y - 0.03 * inch, str(total_cost))
        
        # Draw card body
        body = card_data.get('body', {})
        if body:
            text_y = y + card_h - 0.7 * inch
            c.setFillColor(self.text_color)
            
            # When
            when = body.get('when', '')
            if when:
                c.setFont("Helvetica-Bold", 8)
                c.setFillColor(HexColor(card_color))  # Use card color for keyword
                c.drawString(x + 0.1 * inch, text_y, "When:")
                c.setFont("Helvetica", 8)
                c.setFillColor(self.text_color)  # Normal color for text
                c.drawString(x + 0.5 * inch, text_y, when[:35])
                text_y -= 0.15 * inch
            
            # Target
            target = body.get('target', '')
            if target:
                c.setFont("Helvetica-Bold", 8)
                c.setFillColor(HexColor(card_color))  # Use card color for keyword
                c.drawString(x + 0.1 * inch, text_y, "Target:")
                c.setFont("Helvetica", 8)
                c.setFillColor(self.text_color)  # Normal color for text
                c.drawString(x + 0.5 * inch, text_y, target[:32])
                text_y -= 0.15 * inch
            
            # Effect
            effect = body.get('effect', '')
            if effect:
                c.setFont("Helvetica-Bold", 8)
                c.setFillColor(HexColor(card_color))  # Use card color for keyword
                c.drawString(x + 0.1 * inch, text_y, "Effect:")
                c.setFont("Helvetica", 8)
                c.setFillColor(self.text_color)  # Normal color for text
                # Handle long effect text
                effect_lines = self._wrap_text(effect, 32)
                for line in effect_lines[:2]:  # Max 2 lines
                    c.drawString(x + 0.5 * inch, text_y, line)
                    text_y -= 0.12 * inch
                text_y -= 0.03 * inch
            
            # Restriction
            restriction = body.get('restriction', '')
            if restriction and restriction.lower() != 'none':
                c.setFont("Helvetica-Bold", 7)
                c.setFillColor(HexColor(card_color))  # Use card color for "Restriction:" keyword
                c.drawString(x + 0.1 * inch, text_y, "Restriction:")
                c.setFont("Helvetica-Oblique", 7)
                c.setFillColor(self.subtitle_color)  # Keep subtitle color for restriction text
                restriction_lines = self._wrap_text(restriction, 35)
                for line in restriction_lines[:2]:  # Max 2 lines
                    c.drawString(x + 0.7 * inch, text_y, line)
                    text_y -= 0.1 * inch
        
        # Draw mana cost breakdown at bottom (no colors)
        if cost_data:
            cost_y = y + 0.15 * inch
            cost_x = x + 0.1 * inch
            c.setFont("Helvetica", 7)
            c.setFillColor(self.text_color)  # Use standard text color
            cost_text = []
            for mana_type, amount in cost_data.items():
                if amount > 0:
                    cost_text.append(f"{mana_type.title()}: {amount}")
            if cost_text:
                c.drawString(cost_x, cost_y, " | ".join(cost_text))
        
        if rotated:
            c.restoreState()
    
    def _wrap_text(self, text, max_chars):
        """Wrap text to fit within specified character limit."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
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
            # Calculate position based on layout type
            page_idx = idx % self.cards_per_page
            
            if self.layout_type == 'normal':
                row = page_idx // self.cards_per_row
                col = page_idx % self.cards_per_row
                x = col * self.card_width
                y = self.page_height - (row + 1) * self.card_height
                self.draw_card(c, x, y, card_data, rotated=False)
                
            elif self.layout_type == 'rotated':
                row = page_idx // self.cards_per_row
                col = page_idx % self.cards_per_row
                x = col * self.card_height
                y = self.page_height - (row + 1) * self.card_width
                self.draw_card(c, x, y, card_data, rotated=True)
                
            else:  # mixed layout
                normal_cards = self.cards_per_row * self.cards_per_col
                if page_idx < normal_cards:
                    # Normal orientation
                    row = page_idx // self.cards_per_row
                    col = page_idx % self.cards_per_row
                    x = col * self.card_width
                    y = self.page_height - (row + 1) * self.card_height
                    self.draw_card(c, x, y, card_data, rotated=False)
                else:
                    # Rotated orientation in remaining space
                    extra_idx = page_idx - normal_cards
                    # Place rotated cards in remaining width space
                    remaining_width = self.page_width - (self.cards_per_row * self.card_width)
                    if remaining_width >= self.card_height:
                        rotated_col = int(remaining_width / self.card_height)
                        row = extra_idx // rotated_col
                        col = extra_idx % rotated_col
                        x = self.cards_per_row * self.card_width + col * self.card_height
                        y = self.page_height - (row + 1) * self.card_width
                        self.draw_card(c, x, y, card_data, rotated=True)
            
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
